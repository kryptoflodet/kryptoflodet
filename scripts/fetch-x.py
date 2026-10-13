"""Read X's public embed data, without login, cookies, paid APIs or mirror services.
This is a limited public selection, NOT a complete chronological X API.
Only original posts by configured account IDs are accepted. Original text is preserved.
"""
import concurrent.futures,datetime as dt,email.utils,html,json,pathlib,re,urllib.request,urllib.error
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
 with urllib.request.urlopen(req,timeout=20) as r:
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
 categories=[{'BTC':'Bitcoin','ETH':'Ethereum'}.get(c,'Altcoins') for c in coins]
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
 # Some public X profiles do not expose a stable ID in the profile config.
 # Resolve it only from the response itself, requiring one unique numeric ID
 # and an exact screen-name match; established accounts remain pinned to IDs.
 resolved=account
 if not account.get('userId'):
  authors={str(t.get('user',{}).get('id_str','')) for t in raw
           if t.get('user',{}).get('screen_name','').lower()==account['handle'].lower()}
  authors={value for value in authors if re.fullmatch(r'\d{5,22}',value)}
  if len(authors)!=1:raise ValueError('Could not validate X profile identity')
  resolved={**account,'userId':authors.pop()}
 items=[n for t in raw if (n:=parse_post(t,resolved,now))]
 dates=[d for t in raw if (d:=timestamp(t.get('created_at'))) is not None]
 return list({n['id']:n for n in items}.values()),max(dates).isoformat() if dates else None

def balanced_posts(posts,accounts,per_account=30,maximum=None):
 selected=[]
 for account in accounts:
  own=sorted((p for p in posts.values() if p.get('sourceId')==account['id']),key=lambda p:p['publishedAt'],reverse=True)
  selected.extend(own[:per_account])
 return sorted(selected,key=lambda n:n['publishedAt'],reverse=True)[:maximum or per_account*len(accounts)]

def retry_after(error,now):
 value=error.headers.get('Retry-After') if error.headers else None
 try:until=now+dt.timedelta(seconds=max(60,min(int(value),86400)))
 except (TypeError,ValueError):
  until=timestamp(value) or now+dt.timedelta(minutes=30)
 return until.isoformat().replace('+00:00','Z')

def fetch_profile(account,previous,now):
 stamp=now.isoformat().replace('+00:00','Z')
 status={'id':account['id'],'name':account['name'],'handle':account['handle'],'url':'https://x.com/'+account['handle'],'checkedAt':stamp,'connection':'error','coverage':'Begränsat offentligt urval från X; inte fullständig bevakning.','lastSuccessAt':previous.get('lastSuccessAt'),'lastIndividualSuccessAt':previous.get('lastIndividualSuccessAt'),'attempts':[]}
 routes=[]
 if account.get('userId'):routes.append(('user-id/'+account['userId'],'user-id'))
 routes.append(('screen-name/'+account['handle'],'screen-name'))
 empty=False
 for route,method in routes:
  prior=next((a for a in previous.get('attempts',[]) if a.get('method')==method),{})
  until=timestamp(prior.get('retryAfterAt'))
  if until and until>now:
   status['attempts'].append({'method':method,'result':'cooldown','retryAfterAt':prior['retryAfterAt'],'httpStatus':prior.get('httpStatus')})
   continue
  try:
   rows,newest=parse_timeline(get('https://syndication.twitter.com/srv/timeline-profile/'+route+'?dnt=true&lang=sv'),account,now)
   status['attempts'].append({'method':method,'result':'ok' if rows else 'empty','eligiblePosts':len(rows)})
   status.update(newestAvailableAt=newest,lastProfileSuccessAt=stamp)
   if rows:
    status.update(connection='connected',profileConnection='connected',method=method,count=len(rows),lastSuccessAt=stamp)
    return status,rows
   empty=True
   print(f"{account['id']}: {method} returned no eligible recent posts; newest={newest}",flush=True)
  except Exception as error:
   code=error.code if isinstance(error,urllib.error.HTTPError) else None
   attempt={'method':method,'result':'error','error':type(error).__name__,'httpStatus':code}
   if code==429:attempt['retryAfterAt']=retry_after(error,now)
   status['attempts'].append(attempt)
   status.update(errorType=type(error).__name__,httpStatus=code)
   print(f"{account['id']}: {method} {type(error).__name__}"+(f" HTTP {code}" if code else ''),flush=True)
 status['connection']=status['profileConnection']='limited' if empty else 'error'
 status['message']='Profilflödet gav inga aktuella originalinlägg. Enskilda originalposter och sparade inlägg används som reserv.' if empty else 'Profilflödet kunde inte uppdateras. Senast hämtade inlägg behålls.'
 return status,[]

def article_references(items,now):
 allowed={'cointelegraph.com','coindesk.com','decrypt.co','bitcoinmagazine.com','cryptoslate.com','theblock.co'}
 selected={}
 for item in items:
  host=(urlsplit(item.get('originalUrl','')).hostname or '').removeprefix('www.')
  published=timestamp(item.get('publishedAt'))
  if host in allowed and published and -600<=(now-published).total_seconds()<3*86400:
   selected[item['originalUrl']]=item
 return sorted(selected.values(),key=lambda n:(bool(re.search(r'Saylor|Strategy|\bMSTR\b|MMCrypto|Jaszczynski|Crypto Rover|The Moon|Watcher.Guru',n.get('originalTitle',''),re.I)),n['publishedAt']),reverse=True)

def profile_references(payload,handle):
 """Use public profile pages only to discover IDs; X must verify every post.

 Ignore replies and non-crypto snippets so a small request budget is not spent
 repeatedly checking travel posts. Mirror text is never published as an original.
 """
 found=set();seen=set()
 for match in re.finditer(r'href=[\"\']/'+re.escape(handle)+r'/status/(\d{15,22})[^\"\']*[\"\']',payload,re.I):
  if match[1] in seen:continue
  seen.add(match[1])
  tail=payload[match.end():match.end()+4000]
  body=re.search(r'<div\b[^>]*class=[\"\']activity-descp[\"\'][^>]*>\s*<p[^>]*>(.*?)</p>',tail,re.S)
  if not body:continue
  snippet=html.unescape(re.sub(r'<[^>]*>','',body[1])).strip()
  if not re.match(r'^@[A-Za-z0-9_]+\b',snippet) and crypto_only(snippet):found.add(match[1])
 return sorted(found,key=int,reverse=True)[:8]

def main():
 now=dt.datetime.now(UTC);stamp=now.isoformat().replace('+00:00','Z');accounts=load(ROOT/'scripts/x-sources.json',[]);old=load(TARGET,{'posts':[],'sources':[],'discovery':{}})
 def fetch(account):
  previous=next((s for s in old.get('sources',[]) if s.get('id')==account['id']),{})
  return fetch_profile(account,previous,now)
 # X's public endpoint can be slow. Lower concurrency and allow a realistic
 # response window instead of marking valid responses as timeouts.
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,accounts))
 posts={n['id']:n for n in old['posts'] if timestamp(n.get('publishedAt')) and 0<=(now-timestamp(n['publishedAt'])).total_seconds()<=14*86400 and any(n.get('handle')==a['handle'] for a in accounts)}
 for _,rows in results:
  posts.update({n['id']:n for n in rows})
 # Keep coin tickers as filters, while grouping SUI and Solana under Altcoins.
 for n in posts.values():
  categories=[c for c in n.get('categories',[]) if c not in {'SUI','Solana'}]
  if any(c not in ('BTC','ETH') for c in n.get('coins',[])) and 'Altcoins' not in categories:categories.append('Altcoins')
  n['categories']=categories
 # Some profiles return only old/popular posts. Discover canonical post IDs in a
 # bounded set of directly fetched RSS publishers' articles, then verify with X.
 # Never infer a post's text, author or date from a secondary publication.
 pending=load(ROOT/'state/pending.json',{'items':[]})['items'];discovery=old.get('discovery',{})
 news_path=ROOT/'public/data/news.json';news=load(news_path,None)
 seeds=load(ROOT/'scripts/x-posts.json',[])
 links={(s['handle'].lower(),s['id']):s.get('context') for s in seeds}
 # Approved articles can contain the best original references too. Do not drop
 # them from discovery as soon as their Swedish summary has been published.
 selected=article_references(pending+(news.get('items',[]) if news else []),now)
 references=[];uncached=[]
 for n in selected:
  key=n['originalUrl'];cached=discovery.get(key);checked=timestamp(cached.get('checkedAt')) if cached else None
  if checked and (now-checked).total_seconds()<86400:references.append((n,cached['links']))
  elif len(uncached)<6:uncached.append(n)
 def discover(n):
  try:
   payload=html.unescape(get(n['originalUrl']));found=list(set(re.findall(r'https?://(?:www\.)?(?:x|twitter)\.com/([A-Za-z0-9_]+)/status/(\d{15,22})',payload)))[:12]
   return n,found
  except Exception as e:print('X discovery',type(e).__name__,flush=True);return n,None
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for n,found in pool.map(discover,uncached):
   if found is not None:
    discovery[n['originalUrl']]={'checkedAt':stamp,'links':found};references.append((n,found))
 for n,found in references:
  for handle,pid in found:
   if any(handle.lower()==a['handle'].lower() for a in accounts):links[(handle.lower(),pid)]={'url':n['originalUrl'],'title':n['originalTitle']}
 sources=[s for s,_ in results]
 # Profile embeds can expose only popular posts from years ago. A public mirror
 # supplies candidate links, not trusted text; the pinned X account ID, timestamp
 # and original JSON are checked by the individual-post endpoint below.
 def discover_profile(pair):
  account,status=pair
  newest=timestamp(status.get('newestAvailableAt'))
  if status['connection']=='connected' and newest and (now-newest).total_seconds()<5400:return []
  url='https://www6.twstalker.com/'+account['handle'];cached=discovery.get(url,{})
  checked=timestamp(cached.get('checkedAt'))
  if checked and (now-checked).total_seconds()<1800:return cached.get('links',[])
  try:
   found=[[account['handle'],pid] for pid in profile_references(get(url),account['handle'])]
   discovery[url]={'checkedAt':stamp,'links':found}
   status['attempts'].append({'method':'public-profile-reference','result':'ok','candidateIds':len(found)})
   print(f"{account['id']}: public-profile-reference found {len(found)} candidate IDs",flush=True)
   return found
  except Exception as e:
   code=e.code if isinstance(e,urllib.error.HTTPError) else None
   discovery[url]={'checkedAt':stamp,'links':cached.get('links',[]),'httpStatus':code,'error':type(e).__name__}
   status['attempts'].append({'method':'public-profile-reference','result':'error','httpStatus':code,'error':type(e).__name__})
   print(f"{account['id']}: public-profile-reference {type(e).__name__}"+(f' HTTP {code}' if code else ''),flush=True)
   return cached.get('links',[])
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for account,found in zip(accounts,pool.map(discover_profile,zip(accounts,sources))):
   for handle,pid in found:links.setdefault((handle.lower(),pid),None)
 # Give each limited profile its own bounded status budget. New references must
 # not be crowded out by a long, fixed list of older seeds from another account.
 def fetch_individual(pair):
  account,status=pair;previous=next((s for s in old.get('sources',[]) if s.get('id')==account['id']),{})
  recovered={}
  own={(handle,pid):context for (handle,pid),context in links.items() if handle==account['handle'].lower()}
  if status['connection']!='connected':
   for p in posts.values():
    if p['sourceId']==account['id']:own.setdefault((account['handle'].lower(),p['id']),p.get('contextSource'))
  candidates=sorted(own.items(),key=lambda entry:(entry[0][1] not in posts,int(entry[0][1])),reverse=True)
  attempts=0;successes=0
  for (handle,pid),context in candidates:
   cached=posts.get(pid);checked=timestamp(cached.get('originalCheckedAt')) if cached else None
   if cached and status['connection']=='connected':continue
   if checked and (now-checked).total_seconds()<3600:continue
   prior=next((a for a in previous.get('attempts',[]) if a.get('method')=='individual-post' and a.get('id')==pid),{})
   until=timestamp(prior.get('retryAfterAt'))
   if until and until>now:
    status['attempts'].append({'method':'individual-post','id':pid,'result':'cooldown','retryAfterAt':prior['retryAfterAt']});continue
   if attempts>=2:break
   attempts+=1
   try:
    t=json.loads(get('https://cdn.syndication.twimg.com/tweet-result?id='+pid+'&lang=sv&token=0'))
    n=parse_post(t,account,now,context)
    status['attempts'].append({'method':'individual-post','id':pid,'result':'ok' if n else 'rejected'})
    if n:
     n['originalCheckedAt']=stamp;recovered[pid]=n;successes+=1
   except Exception as e:
    code=e.code if isinstance(e,urllib.error.HTTPError) else None
    attempt={'method':'individual-post','id':pid,'result':'error','httpStatus':code,'error':type(e).__name__}
    if code==429:attempt['retryAfterAt']=retry_after(e,now)
    status['attempts'].append(attempt)
    print(f"{account['id']}: individual-post {pid} {type(e).__name__}"+(f' HTTP {code}' if code else ''),flush=True)
  if successes:
   status.update(lastSuccessAt=stamp,lastIndividualSuccessAt=stamp)
   if status['connection']!='connected':
    status.update(connection='limited',method='individual-post',message='Enskilda aktuella originalposter har verifierats hos X. Profilflödet är begränsat; alla nya inlägg kan inte garanteras.')
   print(f"{account['id']}: individual-post fallback verified {successes} posts",flush=True)
  elif status['connection']!='connected' and status.get('lastIndividualSuccessAt') and any(p['sourceId']==account['id'] for p in posts.values()):
   status.update(connection='limited',method='cached-individual-post',message='Sparade originalposter från den enskilda X-endpointen visas. Profilflödet är begränsat.')
  return recovered
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  recovered=list(pool.map(fetch_individual,zip(accounts,sources)))
 for rows in recovered:posts.update(rows)
 for s in sources:
  found=[n for n in posts.values() if n['sourceId']==s['id']];s['count']=len(found)
  s['newestPostAt']=max((n['publishedAt'] for n in found),default=None)
  if s['connection']=='limited' and not found:s['message']='Profilflödet gav bara äldre eller irrelevanta poster. Inga aktuella originalposter kunde verifieras i reservvägen.'
 # Keep a fair rolling window for every followed account so the busiest feeds
 # cannot evict every post from quieter accounts.
 data={'generatedAt':stamp,'posts':balanced_posts(posts,accounts),'sources':sources,'discovery':{k:v for k,v in discovery.items() if timestamp(v.get('checkedAt')) and (now-timestamp(v['checkedAt'])).total_seconds()<14*86400}}
 for status in sources:status['count']=sum(p['sourceId']==status['id'] for p in data['posts'])
 tmp=TARGET.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(TARGET)
 if news:
  ids={a['id'] for a in accounts};news['sources']=[s for s in news['sources'] if s['id'] not in ids]
  for account,status in zip(accounts,sources):
   news['sources'].append({'id':account['id'],'name':account['name'],'type':account['type'],'channel':'X','url':status['url'],'trust':0,'enabled':True,'connection':status['connection'],'independenceGroup':account['id'],'checkedAt':stamp,'coverage':status['coverage']+' '+status.get('message',''),'count':status['count']})
  tmp=news_path.with_suffix('.tmp');tmp.write_text(json.dumps(news,ensure_ascii=False,indent=2)+'\n');tmp.replace(news_path)
 print(json.dumps({'xPosts':len(data['posts']),'sources':[{k:s[k] for k in ['handle','connection','count']} for s in sources]},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
