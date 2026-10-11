"""Fetch public RSS/Atom metadata. Never treat a publisher's claim as verified fact."""
import concurrent.futures, datetime as dt, email.utils, hashlib, html, json, pathlib, re, urllib.request, xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET = ROOT / 'public/data/news.json'
FEEDS = json.loads((ROOT/'scripts/sources.json').read_text())
COINS={'BTC':['bitcoin','btc'],'ETH':['ethereum','ether','eth'],'SOL':['solana','sol'],'SUI':['sui'],'HBAR':['hedera','hbar'],'ONDO':['ondo'],'XRP':['xrp','ripple'],'ADA':['cardano','ada'],'DOGE':['dogecoin','doge'],'XLM':['stellar','xlm'],'AVAX':['avalanche','avax'],'LINK':['chainlink'],'BNB':['bnb','binance coin'],'HYPE':['hyperliquid','hype'],'LTC':['litecoin','ltc']}
def clean(text): return re.sub(r'\s+', ' ',re.sub(r'<[^>]+>',' ',html.unescape(text or ''))).strip()
def date(text):
 try:
  try: value=email.utils.parsedate_to_datetime(text)
  except (ValueError,TypeError): value=dt.datetime.fromisoformat(text.replace('Z','+00:00'))
  if value.tzinfo is None: value=value.replace(tzinfo=dt.timezone.utc)
  return value.astimezone(dt.timezone.utc).isoformat().replace('+00:00','Z')
 except Exception:return None

def parse_feed(payload, source, now):
 root=ET.fromstring(payload); entries=root.findall('./channel/item') or root.findall('{http://www.w3.org/2005/Atom}entry'); result=[]
 if not entries:
  if root.tag=='rss' or root.tag=='{http://www.w3.org/2005/Atom}feed':return []
  raise ValueError('Svaret är inte RSS/Atom')
 for entry in entries[:20]:
  fields={el.tag.split('}')[-1]:el.text or '' for el in entry}
  title=clean(fields.get('title','')); link=fields.get('link','').strip()
  if not link:
   link=next((e.attrib.get('href','') for e in entry if e.tag.endswith('link') and e.attrib.get('rel','alternate')=='alternate'),'')
  published=date(fields.get('pubDate') or fields.get('published') or fields.get('updated'))
  if not title or not link.startswith(('https://','http://')) or not published: continue
  if dt.datetime.fromisoformat(published.replace('Z','+00:00'))>dt.datetime.fromisoformat(now.replace('Z','+00:00'))+dt.timedelta(minutes=10): continue
  # Retain headline metadata only, rather than republishing full RSS article bodies.
  coins=[symbol for symbol,words in COINS.items() if any(re.search(r'\b'+re.escape(word)+r'\b',title,re.I) for word in words)]
  category='Makro' if source['id']=='fed' else 'Reglering' if source['id']=='sec' else 'ETF' if re.search(r'\bETF',title,re.I) else 'Säkerhet / Hacks' if re.search(r'\b(hack|exploit|breach)',title,re.I) else 'Bitcoin' if coins==['BTC'] else 'Ethereum' if coins==['ETH'] else 'Altcoins' if coins else 'Institutioner'
  if source.get('category') and not coins: category=source['category']
  uid=hashlib.sha256(link.encode()).hexdigest()[:20]
  result.append(dict(id=uid,eventKey=link,originalTitle=title,originalText=title,originalLanguage=source.get('language','en'),title=title,translation='',summary=f"{source['name']} publicerar en nyhet inom {category.lower()}. Läs originalartikeln för fullständiga uppgifter. Rubriken visas på originalspråket.",why='Automatiskt kategoriserad källpost. Händelsens innebörd och eventuell marknadspåverkan har inte bedömts redaktionellt.',author=source['name'],publishedAt=published,importedAt=now,category=category,coins=coins,topics=coins or [category],sourceId=source['id'],originalUrl=link,sourceType=source['type'],evidence=[dict(sourceId=source['id'],url=link,originId=link,direct=True,verified=False)],status='unconfirmed',confidence=0,sentiment='Neutral',importance=3,breaking=False,demo=False,analysisMethod='automated'))
 # A valid feed may contain no articles matching the editorial scope.
 return result

def main():
 now=dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')
 old=json.loads(TARGET.read_text()) if TARGET.exists() else {'items':[],'sources':[]}
 def fetch(spec):
  sid,name,kind,url=(spec[k] for k in ['id','name','type','url'])
  s=dict(id=sid,name=name,type=kind,channel='RSS',url=url,trust=0,enabled=True,connection='planned',independenceGroup=sid,checkedAt=now,language=spec.get('language','en'),category=spec.get('category'),coverage=spec.get('coverage','Direkt RSS från utgivaren'))
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'Kryptoflodet/1.0 (+https://kryptoflodet.github.io/)','Accept':'application/rss+xml, application/atom+xml, application/xml, text/xml'})
   with urllib.request.urlopen(req,timeout=12) as response: payload=response.read(3_000_000)
   items=parse_feed(payload,s,now);s.update(connection='connected',lastSuccessAt=now,count=len(items)); print(f'{sid}: {len(items)} artiklar')
   return s,items
  except Exception as exc:
   previous=next((v for v in old['sources'] if v['id']==sid),{})
   s.update(error=str(exc)[:160],lastSuccessAt=previous.get('lastSuccessAt'));print(f'{sid}: {exc}')
   return s,[i for i in old['items'] if i['sourceId']==sid]
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(fetch,FEEDS))
 sources=[s for s,_ in results]; unique={n['originalUrl']:n for _,items in results for n in items}
 items=sorted(unique.values(),key=lambda n:n['publishedAt'],reverse=True)[:500]
 if not items: raise RuntimeError('Alla källor misslyckades; befintlig fil lämnas orörd')
 for sid,name,url,channel in [('saylor','Michael Saylor','https://x.com/saylor','X'),('rover','CryptoRover','https://x.com/rovercrc','X'),('moon','The Moon Show','https://x.com/TheMoonShow','X'),('bitcoin','Bitcoin','https://x.com/bitcoin','X'),('instagram','Instagram – officiella konton','https://www.instagram.com','Instagram'),('strategy','Strategy','https://www.strategy.com','API'),('blackrock','BlackRock','https://www.blackrock.com','API')]:
  sources.append(dict(id=sid,name=name,type='INFLUENCER' if sid in ['rover','moon'] else 'OFFICIELL',channel=channel,url=url,trust=0,enabled=False,connection='planned',independenceGroup=sid,error='Direktflöde saknas. Öppen mediebevakning finns separat; den täcker inte alla X-inlägg.'))
 from translate_news import translate_items
 raw_count=len(items)
 items=translate_items(items)
 if not items: raise RuntimeError('Inga svenska rubriker; tidigare publicering behålls')
 payload=dict(pendingTranslation=raw_count-len(items),generatedAt=now,items=items,sources=sources,intervalMinutes=5)
 TARGET.parent.mkdir(parents=True,exist_ok=True);tmp=TARGET.with_suffix('.tmp');tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n');tmp.replace(TARGET)
 print(f'Sparade {len(items)} artiklar från {sum(s["connection"]=="connected" for s in sources)} källor')
if __name__=='__main__':main()
