"""Fetch independent sources, stage candidates, publish only readable Swedish summaries."""
import concurrent.futures,datetime as dt,email.utils,hashlib,html,json,pathlib,re,urllib.request,xml.etree.ElementTree as ET,os,time,signal
from crypto_scope import crypto_only
from reader_content import PlainText,feed_excerpt
from editorial import canonical_url,deduplicate,enrich,readable,select_important
from x_sources import sources as x_sources
ROOT=pathlib.Path(__file__).resolve().parents[1]
TARGET=ROOT/'public/data/news.json'
ARCHIVE=ROOT/'public/data/archive.json'
FEEDS=json.loads((ROOT/'scripts/sources.json').read_text())
COINS={'BTC':['bitcoin','btc'],'ETH':['ethereum','ether','eth'],'SOL':['solana'],'SUI':['sui'],'HBAR':['hedera','hbar'],'ONDO':['ondo'],'XRP':['xrp','ripple'],'ADA':['cardano'],'DOGE':['dogecoin','doge'],'XLM':['stellar','xlm'],'AVAX':['avalanche','avax'],'LINK':['chainlink'],'BNB':['bnb'],'HYPE':['hyperliquid'],'LTC':['litecoin','ltc']}
def clean(text):
 parser=PlainText();parser.feed(html.unescape(text or ''));return re.sub(r'\s+',' ',''.join(parser.parts)).strip()
def date(text):
 try:
  try:value=email.utils.parsedate_to_datetime(text)
  except (ValueError,TypeError):value=dt.datetime.fromisoformat(text.replace('Z','+00:00'))
  if value.tzinfo is None:return None
  return value.astimezone(dt.timezone.utc).isoformat().replace('+00:00','Z')
 except (ValueError,TypeError,AttributeError):return None

def parse_feed(payload,source,now):
 if b'<!DOCTYPE' in (payload if isinstance(payload,bytes) else payload.encode()).upper():raise ValueError('DTD is not permitted')
 root=ET.fromstring(payload);entries=root.findall('./channel/item') or root.findall('{http://www.w3.org/2005/Atom}entry');result=[]
 if not entries:
  if root.tag in ('rss','{http://www.w3.org/2005/Atom}feed'):return []
  raise ValueError('Not RSS/Atom')
 for entry in entries[:25]:
  fields={el.tag.split('}')[-1]:''.join(el.itertext()) for el in entry}
  title=clean(fields.get('title',''));link=fields.get('link','').strip()
  if not link:link=next((e.attrib.get('href','') for e in entry if e.tag.endswith('link') and e.attrib.get('rel','alternate')=='alternate'),'')
  try:key=canonical_url(link)
  except ValueError:continue
  published=date(fields.get('pubDate') or fields.get('published') or fields.get('updated'))
  if not title or not published or not crypto_only(title):continue
  age=(dt.datetime.fromisoformat(now.replace('Z','+00:00'))-dt.datetime.fromisoformat(published.replace('Z','+00:00'))).total_seconds()
  if age < -600:continue
  # Keep a bounded private working excerpt; do not publish the source prose.
  raw=fields.get('description') or fields.get('summary') or fields.get('encoded') or fields.get('content') or ''
  if source['id'].endswith('-video'):
   raw=next((e.text for e in entry.iter() if e.tag=='{http://search.yahoo.com/mrss/}description'),'') or ''
   raw=re.split(r'https?://|\b(?:SPONSOR|DISCLAIMER|AFFILIATE)\b',raw,flags=re.I)[0]
  if source['id'].endswith('-watch') or source['id']=='coinmarketcap':raw=''
  source_text=' '.join(clean(raw).split()[:180])
  if source.get('channel')=='X' and not source_text:source_text=title
  coins=[c for c,words in COINS.items() if any(re.search(r'\b'+re.escape(w)+r'\b',title,re.I) for w in words)]
  category='Reglering' if source['id']=='sec' else 'ETF' if re.search(r'\bETF',title,re.I) else 'Bitcoin' if coins==['BTC'] else 'Ethereum' if coins==['ETH'] else 'Altcoins' if coins else 'Institutioner'
  uid=hashlib.sha256(key.encode()).hexdigest()[:20]
  result.append(dict(sourceText=source_text,id=uid,eventKey=key,originalTitle=title,originalText=title,originalLanguage=source.get('language','en'),title=title,translation='',summary='',why='',author=source['name'],publishedAt=published,importedAt=now,category=category,coins=coins,topics=coins or [category],sourceId=source['id'],channel=source.get('channel','RSS'),originalUrl=link,sourceType=source['type'],evidence=[dict(sourceId=source['id'],url=link,originId=key,direct=True,verified=False)],status='unconfirmed',confidence=0,sentiment='Neutral',importance=2,breaking=False,demo=False,analysisMethod='automated'))
 return result

def read_json(path,default):
 try:return json.loads(path.read_text())
 except (OSError,ValueError):return default

def atomic_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)

def main():
 now=dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')
 old=read_json(TARGET,{'items':[],'sources':[]})
 archive=read_json(ARCHIVE,{'items':[]})
 previous={canonical_url(n['originalUrl']):n for n in archive['items']+old['items']}
 def fetch(spec):
  sid=spec['id'];public_url='https://x.com/'+spec['handle'] if spec.get('channel')=='X' else spec['url']
  s=dict(id=sid,name=spec['name'],type=spec['type'],channel=spec.get('channel','RSS'),url=public_url,trust=0,enabled=True,connection='planned',independenceGroup=sid,checkedAt=now,language=spec.get('language','en'),coverage=spec.get('coverage','Direkt RSS från utgivaren'))
  if spec.get('disabledReason'):s.update(enabled=False,error=spec['disabledReason']);return s,[]
  try:
   req=urllib.request.Request(spec['url'],headers={'User-Agent':'Kryptokollen/2.0 (+https://kryptokollen.online)','Accept':'application/rss+xml, application/atom+xml, application/xml'})
   with urllib.request.urlopen(req,timeout=12) as r:payload=r.read(3_000_001)
   if len(payload)>3_000_000:raise ValueError('Feed too large')
   rows=parse_feed(payload,s,now);s.update(connection='connected',lastSuccessAt=now,count=len(rows));print(f'{sid}: {len(rows)} kandidater',flush=True);return s,rows
  except Exception as exc:
   prior=next((v for v in old['sources'] if v['id']==sid),{})
   # Never print URLs/errors that could contain a private RSSHub access token.
   s.update(error='Källan kunde inte hämtas ('+type(exc).__name__+'). Tidigare publicerade nyheter behålls.',lastSuccessAt=prior.get('lastSuccessAt'));print(f'{sid}: {type(exc).__name__}',flush=True);return s,[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(fetch,FEEDS+x_sources(ROOT)))
 registry=[s for s,_ in results]
 candidates=deduplicate([n for _,rows in results for n in rows])
 reviews=read_json(ROOT/'scripts/reviewed.json',{})
 held={};drafts=[];accepted=[enrich(n) for n in previous.values() if readable(n) and n.get('translationStatus')=='reviewed-sv']
 accepted_by_url={canonical_url(n['originalUrl']):n for n in accepted}
 # Preserve old reviewed original announcements with independently written Swedish text.
 for n in candidates+list(previous.values()):
  review=reviews.get(n['originalUrl'])
  if review:
   n.update(title=review['title'],summary=review['summary'],readerText=review['summary']+'\n\n'+review['why'],why=review['why'],readerKind='reviewed',coins=review['coins'],status='confirmed',analysisMethod='editorial',verificationNote=review['note'],reviewedAt='2026-10-11T15:15:00Z',translationStatus='reviewed-sv',contentVersion=2)
   n['evidence'][0]['verified']=True;n.pop('sourceText',None)
   accepted_by_url[canonical_url(n['originalUrl'])]=enrich(n)
 from local_editor import cache_key
 memo=read_json(ROOT/'.cache/editor/edits-v2.json',{})
 editor=None;attempts=0;max_edits=int(os.environ.get('EDITOR_MAX_ITEMS','4'));deadline=time.monotonic()+int(os.environ.get('EDITOR_SECONDS','150'))
 for n in candidates:
  key=canonical_url(n['originalUrl'])
  if key in accepted_by_url:continue
  if len(n.get('sourceText','').split())<35:held[n['id']]='insufficient_source';continue
  if cache_key(n) in memo and memo[cache_key(n)] is None:held[n['id']]='previously_rejected';continue
  if os.environ.get('EDITOR_MODE','reviewed-only')!='draft':held[n['id']]='awaiting_editorial_review';continue
  if attempts>=max_edits or time.monotonic()>deadline:held[n['id']]='editor_queue';continue
  attempts+=1
  try:
   if editor is None:
    from local_editor import Editor
    editor=Editor()
   signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('Editor deadline')))
   signal.alarm(max(1,int(deadline-time.monotonic())))
   try:draft,reason=editor.edit(n)
   finally:signal.alarm(0)
   if not draft:held[n['id']]=reason;continue
   # Local inference is experimental: even a passing model check needs a human review.
   held[n['id']]='draft_requires_review'
   drafts.append({'originalUrl':n['originalUrl'],'publishedAt':n['publishedAt'],'source':n['author'],**draft})
   continue
  except Exception as exc:held[n['id']]='editor_unavailable';print('Lokal redaktör:',type(exc).__name__,flush=True);break
 accepted=deduplicate([n for n in accepted_by_url.values() if readable(n)])
 if not accepted:raise RuntimeError('Ingen godkänd artikel; tidigare publicering lämnas orörd')
 for n in accepted:n.pop('sourceText',None);n.pop('readerOriginal',None)
 important=select_important(accepted)
 health={'checkedAt':now,'sourcesConnected':sum(s['connection']=='connected' for s in registry),'sourcesTotal':sum(s['enabled'] for s in registry),'candidates':len(candidates),'published':len(accepted),'held':len(held),'heldReasons':{reason:list(held.values()).count(reason) for reason in set(held.values())},'editorAttempts':attempts,'paidApis':False,'editorMode':'reviewed-only','awaitingReview':len([n for n in candidates if canonical_url(n['originalUrl']) not in accepted_by_url])}
 pending=[{k:n[k] for k in ('id','originalUrl','originalTitle','publishedAt','sourceId')} | {'reason':held.get(n['id'],'editor_queue')} for n in candidates if canonical_url(n['originalUrl']) not in accepted_by_url]
 atomic_json(ROOT/'state/pending.json',{'checkedAt':now,'items':pending})
 if drafts:atomic_json(ROOT/'.cache/editor/drafts.json',{'drafts':drafts})
 # Archive is persisted by Actions in git, unlike disposable runner caches.
 atomic_json(ARCHIVE,{'schemaVersion':2,'items':accepted})
 atomic_json(TARGET,{'schemaVersion':2,'generatedAt':now,'items':accepted[:300],'sources':registry,'intervalMinutes':5,'importantIds':[n['id'] for n in important],'health':health})
 atomic_json(ROOT/'public/data/health.json',health)
 print(json.dumps(health,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
