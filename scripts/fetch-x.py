"""Read X's public embed data, without login, cookies, paid APIs or mirror services.
This is a limited public selection, NOT a complete chronological X API.
Only original posts by configured account IDs are accepted. Original text is preserved.
"""
import concurrent.futures,datetime as dt,email.utils,html,json,pathlib,re,urllib.request
from html.parser import HTMLParser
from urllib.parse import urlsplit
from crypto_scope import crypto_only
ROOT=pathlib.Path(__file__).resolve().parents[1];TARGET=ROOT/'public/data/x.json';UTC=dt.timezone.utc
UA='Kryptokollen/2.0 (+https://kryptokollen.online)'
class NextData(HTMLParser):
 def __init__(self):super().__init__();self.active=False;self.parts=[]
 def handle_starttag(self,tag,attrs):self.active=tag=='script' and dict(attrs).get('id')=='__NEXT_DATA__' if tag=='script' else self.active
 def handle_endtag(self,tag):
  if tag=='script':self.active=False
 def handle_data(self,data):
  if self.active:self.parts.append(data)
def load(path,default):
 try:return json.loads(path.read_text())
 except (OSError,ValueError):return default
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'text/html,application/json'})
 with urllib.request.urlopen(req,timeout=12) as r:
  data=r.read(2_000_001)
  if len(data)>2_000_000:raise ValueError('Response too large')
  return data.decode('utf-8')
def timestamp(value):
 try:
  try:d=dt.datetime.fromisoformat(value.replace('Z','+00:00'))
  except ValueError:d=email.utils.parsedate_to_datetime(value)
  if d.tzinfo is None:return None
  return d.astimezone(UTC)
 except (TypeError,ValueError,AttributeError):return None
def parse_post(t,account,now,context=None):
 u=t.get('user',{});pid=str(t.get('id_str',''));text=html.unescape(t.get('full_text') or t.get('text') or '')
 date=timestamp(t.get('created_at'));handle=account['handle']
 if not re.fullmatch(r'\d{15,22}',pid) or u.get('id_str')!=account['userId'] or u.get('screen_name','').lower()!=handle.lower():return None
 if t.get('retweeted_status') or t.get('in_reply_to_status_id_str') or t.get('in_reply_to_status_id') or t.get('possibly_sensitive'):return None
 if not date or not -600<=(now-date).total_seconds()<=14*86400:return None
 if not text or len(text)>5000 or not (crypto_only(text) or context and crypto_only(context['title'])):return None
 # Drop pure promotion, referral offers and obvious engagement bait.
 if re.search(r'\b(airdrop|giveaway|deposit bonus|referral|promo code|join my|sign up|subscribe to|follow us)\b',text,re.I):return None
 coins=[sym for sym,pattern in [('BTC',r'\b(bitcoin|btc)\b'),('ETH',r'\b(ethereum|eth|ether)\b'),('SUI',r'\bsui\b'),('SOL',r'\b(solana|sol)\b'),('XRP',r'\b(xrp|ripple)\b'),('HBAR',r'\b(hbar|hedera)\b'),('ONDO',r'\bondo\b'),('ADA',r'\b(cardano|ada)\b'),('DOGE',r'\b(dogecoin|doge)\b'),('LINK',r'\bchainlink\b'),('AVAX',r'\b(avalanche|avax)\b'),('XLM',r'\b(stellar|xlm)\b'),('BNB',r'\bbnb\b')] if re.search(pattern,text,re.I)]
 categories=[{'BTC':'Bitcoin','ETH':'Ethereum','SUI':'SUI','SOL':'Solana'}.get(c,'Altcoins') for c in coins]
 if any(c not in ['BTC','ETH'] for c in coins) or re.search(r'\baltcoins?\b',text,re.I):categories.append('Altcoins')
 if re.search(r'\b(regulat\w*|approv\w*|sec|law)\b',text,re.I):categories.append('Reglering')
 if re.search(r'\b(etfs?|institution\w*|treasury)\b',text,re.I):categories.append('Institutionellt')
 if not categories:categories=['Marknaden']
 categories=list(dict.fromkeys(categories))
 media=[]
 for m in (t.get('extended_entities',{}).get('media') or t.get('entities',{}).get('media') or t.get('photos') or [])[:4]:
  url=m.get('media_url_https') or m.get('url','')
  if urlsplit(url).scheme=='https' and urlsplit(url).hostname=='pbs.twimg.com':media.append({'url':url,'alt':m.get('ext_alt_text') or m.get('alt_text') or ''})
 return {'media':media,'id':pid,'handle':handle,'author':u.get('name') or account['name'].removesuffix(' – X'),'sourceId':account['id'],'url':f'https://x.com/{handle}/status/{pid}','publishedAt':date.isoformat().replace('+00:00','Z'),'text':text,'coins':coins,'categories':categories,'originalLanguage':t.get('lang') or 'und','kind':'original-x-post','verified':False,'discoveredVia':'article-reference' if context else 'x-embed','contextSource':context}
def parse_timeline(payload,account,now):
 p=NextData();p.feed(payload);d=json.loads(''.join(p.parts));es=d['props']['pageProps']['timeline']['entries']
 if not isinstance(es,list):raise ValueError('Missing timeline entries')
 raw=[e.get('content',{}).get('tweet',{}) for e in es if e.get('type')=='tweet']
 items=[n for t in raw if (n:=parse_post(t,account,now))]
 dates=[d for t in raw if (d:=timestamp(t.get('created_at'))) is not None]
 return list({n['id']:n for n in items}.values()),max(dates).isoformat() if dates else None

def main():
 now=dt.datetime.now(UTC);stamp=now.isoformat().replace('+00:00','Z');accounts=load(ROOT/'scripts/x-sources.json',[]);old=load(TARGET,{'posts':[],'sources':[],'discovery':{}})
 def fetch(account):
  status={'id':account['id'],'name':account['name'],'handle':account['handle'],'url':'https://x.com/'+account['handle'],'checkedAt':stamp,'connection':'error','coverage':'Begränsat offentligt urval från X:s inbäddningsflöde; inte fullständig bevakning.'}
  try:
   rows,newest=parse_timeline(get('https://syndication.twitter.com/srv/timeline-profile/screen-name/'+account['handle']+'?dnt=true&lang=sv'),account,now)
   status.update(connection='connected' if rows else 'limited',newestAvailableAt=newest,count=len(rows),lastSuccessAt=stamp)
   if not rows:status['message']='X gav inga aktuella relevanta originalinlägg. Äldre populära inlägg visas inte som nya.'
   return status,rows
  except Exception as e:status['message']='Inbäddningsflödet kunde inte uppdateras. Senast hämtade inlägg kan visas.';print(account['id'],type(e).__name__,flush=True);return status,[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,accounts))
 posts={n['id']:n for n in old['posts'] if timestamp(n.get('publishedAt')) and 0<=(now-timestamp(n['publishedAt'])).total_seconds()<=14*86400 and any(n.get('handle')==a['handle'] for a in accounts)}
 for _,rows in results:
  posts.update({n['id']:n for n in rows})
 # Some profiles return only old/popular posts. Discover canonical post IDs in a
 # bounded set of directly fetched RSS publishers' articles, then verify with X.
 # Never infer a post's text, author or date from a secondary publication.
 pending=load(ROOT/'state/pending.json',{'items':[]})['items'];discovery=old.get('discovery',{})
 allowed={'cointelegraph.com','coindesk.com','decrypt.co','bitcoinmagazine.com','cryptoslate.com','theblock.co'}
 seeds=load(ROOT/'scripts/x-posts.json',[])
 links={(s['handle'].lower(),s['id']):s.get('context') for s in seeds}
 selected=[]
 for n in pending:
  host=(urlsplit(n['originalUrl']).hostname or '').removeprefix('www.')
  published=timestamp(n['publishedAt'])
  if host in allowed and published and (now-published).total_seconds()<3*86400 and re.search(r'Saylor|Crypto Rover|The Moon|Watcher.Guru',n['originalTitle'],re.I):selected.append(n)
 for n in selected[:3]:
  key=n['originalUrl'];cached=discovery.get(key);checked=timestamp(cached.get('checkedAt')) if cached else None
  try:
   if checked and (now-checked).total_seconds()<86400:found=cached['links']
   else:
    payload=html.unescape(get(key));found=list(set(re.findall(r'https?://(?:www\.)?(?:x|twitter)\.com/([A-Za-z0-9_]+)/status/(\d{15,22})',payload)))[:12]
    discovery[key]={'checkedAt':stamp,'links':found}
   for handle,pid in found:
    if any(handle.lower()==a['handle'].lower() for a in accounts):links[(handle.lower(),pid)]={'url':key,'title':n['originalTitle']}
  except Exception as e:print('X discovery',type(e).__name__,flush=True)
 for (handle,pid),context in list(links.items())[:8]:
  if pid in posts and 'media' in posts[pid]:continue
  account=next((a for a in accounts if a['handle'].lower()==handle),None)
  if not account:continue
  try:
   t=json.loads(get('https://cdn.syndication.twimg.com/tweet-result?id='+pid+'&lang=sv&token=0'))
   n=parse_post(t,account,now,context)
   if n:posts[pid]=n
  except Exception as e:print('X individual post',type(e).__name__,flush=True)
 sources=[s for s,_ in results]
 for s in sources:
  found=[n for n in posts.values() if n['sourceId']==s['id']];s['count']=len(found)
  s['newestPostAt']=max((n['publishedAt'] for n in found),default=None)
  if s['connection']=='limited' and found:s['message']='Profilflödet är begränsat. Enskilda originalinlägg har verifierats via X; alla nya inlägg kan inte garanteras.'
 data={'generatedAt':stamp,'posts':sorted(posts.values(),key=lambda n:n['publishedAt'],reverse=True)[:100],'sources':sources,'discovery':{k:v for k,v in discovery.items() if timestamp(v.get('checkedAt')) and (now-timestamp(v['checkedAt'])).total_seconds()<14*86400}}
 tmp=TARGET.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(TARGET)
 news_path=ROOT/'public/data/news.json';news=load(news_path,None)
 if news:
  ids={a['id'] for a in accounts};news['sources']=[s for s in news['sources'] if s['id'] not in ids]
  for account,status in zip(accounts,sources):
   news['sources'].append({'id':account['id'],'name':account['name'],'type':account['type'],'channel':'X','url':status['url'],'trust':0,'enabled':True,'connection':'connected' if status['count'] and status['connection']!='error' else 'planned','independenceGroup':account['id'],'checkedAt':stamp,'coverage':status['coverage']+' '+status.get('message',''),'count':status['count']})
  tmp=news_path.with_suffix('.tmp');tmp.write_text(json.dumps(news,ensure_ascii=False,indent=2)+'\n');tmp.replace(news_path)
 print(json.dumps({'xPosts':len(data['posts']),'sources':[{k:s[k] for k in ['handle','connection','count']} for s in sources]},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
