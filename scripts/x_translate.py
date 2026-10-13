"""Legacy translation helpers. Automatic model output is disabled for publication.

The active workflow uses only source-bound reviewed text and exact Swedish rules
through x_language.py. This module remains to support regression tests for the
old validators; its entry point is intentionally inert.
"""
import collections,datetime as dt,decimal,hashlib,json,os,pathlib,re,subprocess,time,urllib.request,urllib.parse,urllib.error
from x_language import source_hash
from prepare_x_translator import MODEL,MANIFEST,checksum
ROOT=pathlib.Path(__file__).resolve().parents[1];ENGINE=MANIFEST['engine']
CACHE=ROOT/'.cache/x-translation/history.json'

def input_text(text):
 text=re.sub(r'https?://\S+','',text)
 # $BTC is a ticker, not a dollar amount. Remove only the cashtag marker.
 text=re.sub(r'\$(BTC|ETH|SOL|SUI|XRP|HBAR|ONDO|ADA|DOGE|LINK|AVAX|XLM|BNB)\b',r'\1',text,flags=re.I)
 text=re.sub(r'[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]','',text)
 text=re.sub(r'^\s*(JUST IN|BREAKING|ICYMI|UPDATE):\s*','',text,flags=re.I)
 keep={'BTC','ETH','XRP','SOL','SUI','HBAR','ONDO','USD','SGD','ETF','ETFS','USA','UK','BNB','DOGE','MSTR','STRC','CEO'}
 names={'STRATEGY':'Strategy','BITCOIN':'Bitcoin','ETHEREUM':'Ethereum','COINBASE':'Coinbase','BINANCE':'Binance','METAPLANET':'Metaplanet'}
 text=re.sub(r'\b[A-Z]{3,}\b',lambda m:names.get(m[0],m[0] if m[0] in keep else m[0].lower()),text)
 return text.strip()

def amounts(text,swedish=False):
 values=[]
 for m in re.finditer(r'(?<![\w])\d+(?:[.,’\'\u00a0\u202f ]\d+)*(?:\s*(?:billion|million|thousand|miljarder|miljoner|tusen|[kKmMbB])\b)?',text,re.I):
  token=m[0];unit=re.search(r'(billion|million|thousand|miljarder|miljoner|tusen|[kmb])$',token,re.I)
  scale={'billion':10**9,'miljarder':10**9,'b':10**9,'million':10**6,'miljoner':10**6,'m':10**6,'thousand':1000,'tusen':1000,'k':1000}.get(unit[1].lower(),1) if unit else 1
  number=token[:unit.start()] if unit else token
  number=re.sub(r'[’\'\u00a0\u202f ]','',number)
  if swedish:
   if ',' in number:number=number.replace('.','').replace(',','.')
  else:number=number.replace(',','')
  try:values.append(decimal.Decimal(number)*scale)
  except decimal.InvalidOperation:return None
 return collections.Counter(values)

def quantity_units(text,swedish=False):
 """Keep each quoted quantity attached to its asset/currency, not just its digits."""
 units=[]
 numeric=r'(?<![\w])\d+(?:[.,’\'\u00a0\u202f ]\d+)*(?:\s*(?:billion|million|thousand|miljarder|miljoner|tusen|[kKmMbB])\b)?'
 for m in re.finditer(numeric,text,re.I):
  value=amounts(m[0],swedish)
  if not value:continue
  prefix=text[max(0,m.start()-15):m.start()];suffix=text[m.end():m.end()+45]
  suffix=re.sub(r'^\s*(?:seized|confiscated|beslagtagna|beslagtagen|beslagtogs)\s+',' ',suffix,flags=re.I)
  unit=None
  for name,pattern in [('SGD',r'SGD'),('SEK',r'SEK|kronor'),('JPY',r'¥|yen'),('EUR',r'€|EUR|euro'),('USD',r'\$|USD|dollar(?:s|n|na)?')]:
   if re.search(r'(?:'+pattern+r')\s*$',prefix,re.I) or re.match(r'^\s*(?:'+pattern+r')(?:\b|\s|$)',suffix,re.I):unit=name;break
  if unit is None:
   for name,pattern in [('BTC',r'BTC|Bitcoin'),('ETH',r'ETH|Ethereum|ether'),('SOL',r'SOL|Solana'),('SUI',r'SUI'),('XRP',r'XRP')]:
    if re.match(r'^\s*\$?(?:'+pattern+r')\b',suffix,re.I):unit=name;break
  if unit:units.extend((number,unit) for number,count in value.items() for _ in range(count))
 return collections.Counter(units)

def valid_translation(source,text):
 if not isinstance(text,str) or not 1<=len(text)<=6000 or len(text)<len(source)*.5 or len(text)>len(source)*3:return False
 if '<' in text or 'https://' in text or source.casefold()==text.casefold():return False
 if amounts(source)!=amounts(text,True):return False
 if quantity_units(source)!=quantity_units(text,True):return False
 if re.search(r'\b(?:BTC|ETH|Bitcoin)[- ]dollar\w*\b',text,re.I):return False
 if re.search(r'\bHigh Court\b',source) and re.search(r'\bhögsta domstolen\b',text,re.I):return False
 if len(re.findall(r'%|\bpercent\b',source,re.I))!=len(re.findall(r'%|\bprocent\b',text,re.I)):return False
 # These checks preserve explicit caveats; they are not independent fact checking.
 checks=[(r'\b(?:not|never|no)\b|n[’\']t\b',r'\b(?:inte|aldrig|ingen|inget|inga|utan|ej|obekräftad\w*)\b'),
  (r'\b(?:could|might|possibly|likely|potential|unconfirmed|rumou?r)\b',r'\b(?:kan|kunde|skulle|möjlig\w*|sannolik\w*|trolig\w*|potentiell\w*|kanske|rykte\w*|obekräftad\w*)\b'),
  (r'\bif\b',r'\b(?:om|ifall|förutsatt)\b'),
  (r'\d(?:[.,]\d+)?[kmb]?\+',r'\b(?:över|mer än)\b|\+')]
 if any(re.search(a,source,re.I) and not re.search(b,text,re.I) for a,b in checks):return False
 for name in ['Bitcoin','Ethereum','Coinbase','Binance','Strategy','Metaplanet','Nasdaq','SGD','MSTR','STRC']:
  if re.search(r'\b'+name+r'\b',source,re.I) and not re.search(r'\b'+name+r'\b',text,re.I):return False
 if re.search(r'\b(?:plong\w*|cry-opt\w*|millon|purchas\w*|backed|inflows?|outflows?|bullish|bearish|will|could|however|according to|year-over-year|år[- ]över[- ]år)\b',text,re.I):return False
 return True

def cache_key(post,engine=ENGINE):return hashlib.sha256((engine+'\n'+post['url']+'\n'+post['text']).encode()).hexdigest()

def load_history(path):
 try:
  memo=json.loads(path.read_text())
  if isinstance(memo,dict) and isinstance(memo.get('items'),dict):return memo
 except (OSError,ValueError):pass
 return {'items':{}}

def ordered_candidates(posts):
 pending=sorted((p for p in posts if not p.get('swedish') and p.get('originalLanguage')=='en'),key=lambda p:p['publishedAt'],reverse=True)
 first=[];rest=[];seen=set()
 for post in pending:
  if post['handle'] not in seen:first.append(post);seen.add(post['handle'])
  else:rest.append(post)
 return first+rest

def free_fallback(text,memo):
 day=dt.datetime.now(dt.timezone.utc).date().isoformat()
 if memo.get('quotaDay')!=day:memo.update(quotaDay=day,quotaChars=0)
 if len(text.encode())>500 or memo.get('quotaChars',0)+len(text)>4500:return None
 cooldown=memo.get('retryAfterAt',0)
 if cooldown>time.time():return None
 memo['quotaChars']=memo.get('quotaChars',0)+len(text)
 url='https://api.mymemory.translated.net/get?'+urllib.parse.urlencode({'langpair':'en|sv','q':text})
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Kryptopuls/2.0 (+https://kryptopuls.se)'}),timeout=12) as response:data=json.load(response)
  if data.get('quotaFinished') or int(data.get('responseStatus',0))!=200:memo['quotaChars']=4500;return None
  return data.get('responseData',{}).get('translatedText')
 except Exception as error:
  memo['retryAfterAt']=time.time()+1800
  print('X free translation fallback:',type(error).__name__,getattr(error,'code',None),flush=True);return None

def main():
 print('Automatic X translation is disabled; run scripts/x_language.py for reviewed Swedish text.',flush=True)
 return
 target=ROOT/'public/data/x.json';data=json.loads(target.read_text());memo=load_history(CACHE);entries=memo.setdefault('items',{})
 counts={'cached':0,'local':0,'freeFallback':0,'pending':0}
 pending=[]
 for post in ordered_candidates(data['posts']):
  source=input_text(post['text']);key=cache_key(post);cached=entries.get(key) or entries.get(cache_key(post,'nllb-200-600m-q8-v1'),{})
  if cached.get('sourceUrl')==post['url'] and cached.get('sourceHash')==source_hash(post['text']) and valid_translation(source,cached.get('text')):
   post['swedish']={k:cached[k] for k in ('text','method','sourceHash','engine')};counts['cached']+=1
   entries[key]=cached
  elif not cached.get('rejectedUntil',0)>time.time():pending.append(post)
 selected=pending[:int(os.environ.get('X_TRANSLATION_MAX_ITEMS','24'))];seconds=int(os.environ.get('X_TRANSLATION_SECONDS','120'))
 outputs={}
 ready=all((MODEL/name).exists() and checksum(MODEL/name)==expected for name,expected in MANIFEST['files'].items())
 if selected and ready:
  request={'model':str(MODEL),'seconds':seconds,'items':[{'id':p['id'],'text':input_text(p['text'])} for p in selected]}
  try:
   result=subprocess.run(['node',str(ROOT/'scripts/x_translate_model.mjs')],input=json.dumps(request),text=True,capture_output=True,timeout=seconds+40,check=True)
   outputs={p['id']:p.get('text') for p in json.loads(result.stdout)}
  except Exception as error:print('X local translation unavailable:',type(error).__name__,flush=True)
 for post in selected:
  source=input_text(post['text']);text=outputs.get(post['id']);engine=ENGINE
  prior_chars=memo.get('quotaChars',0)
  if not valid_translation(source,text):text=free_fallback(source,memo);engine='mymemory-free-v1'
  key=cache_key(post)
  if valid_translation(source,text):
   post['swedish']={'text':text,'method':'translation','sourceHash':source_hash(post['text']),'engine':engine}
   entries[key]={**post['swedish'],'sourceUrl':post['url'],'checkedAt':time.time()};counts['local' if engine==ENGINE else 'freeFallback']+=1
  elif post['id'] in outputs or memo.get('quotaChars',0)>prior_chars:entries[key]={'rejectedUntil':time.time()+86400,'sourceUrl':post['url'],'sourceHash':source_hash(post['text']),'checkedAt':time.time()}
 counts['pending']=sum(not p.get('swedish') for p in data['posts']);data.setdefault('language',{})['machine']={'engine':ENGINE,**counts};data['language']['pending']=counts['pending']
 tmp=target.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(target)
 memo['items']={k:v for k,v in entries.items() if v.get('checkedAt',0)>time.time()-30*86400};CACHE.parent.mkdir(parents=True,exist_ok=True);tmp_cache=CACHE.with_suffix('.tmp');tmp_cache.write_text(json.dumps(memo,ensure_ascii=False)+'\n');tmp_cache.replace(CACHE)
 queue=ROOT/'state/x-language-review.json'
 if queue.exists():
  report=json.loads(queue.read_text());waiting={p['id'] for p in data['posts'] if not p.get('swedish')};report['items']=[p for p in report['items'] if p['id'] in waiting];report['counts']=data['language'];queue.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('X translation:',json.dumps(counts),flush=True)

if __name__=='__main__':main()
