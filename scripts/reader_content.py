"""Bounded public feed excerpts for the Swedish on-site reader."""
import hashlib, html, json, re
from html.parser import HTMLParser

class PlainText(HTMLParser):
 def __init__(self): super().__init__(); self.parts=[]; self.hidden=0
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style'):self.hidden+=1
  if tag in ('p','br','div'):self.parts.append(' ')
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.hidden=max(0,self.hidden-1)
  if tag in ('p','div'):self.parts.append(' ')
 def handle_data(self,data):
  if not self.hidden:self.parts.append(data)

def feed_excerpt(fields,title,source_id):
 # Aggregators describe links and videos, not the underlying article.
 if source_id.endswith(('-watch','-video')) or source_id=='coinmarketcap':return ''
 raw=fields.get('description') or fields.get('summary') or fields.get('encoded') or fields.get('content') or ''
 parser=PlainText();parser.feed(html.unescape(raw))
 text=re.sub(r'\s+',' ',''.join(parser.parts)).strip()
 text=re.split(r'\b(?:The post .+? appeared first|Read more|Continue reading)\b',text,flags=re.I)[0].strip()
 if text.casefold()==title.casefold() or len(text.split())<8:return ''
 # A short extract only; stop at a sentence boundary when possible.
 words=text.split();short=' '.join(words[:55])
 if len(words)>55:
  sentences=list(re.finditer(r'[.!?](?:\s|$)',short))
  short=short[:sentences[-1].start()+1] if sentences else short+'…'
 return short

def translate_excerpts(items,tokenizer,translator,detector,swedish,cache_dir):
 from translate_news import localize
 cachefile=cache_dir/'reader-v1.json';memo=json.loads(cachefile.read_text()) if cachefile.exists() else {}
 pending=[]
 for item in items:
  item.pop('readerText',None);item.pop('readerKind',None)
  if item.get('analysisMethod')=='editorial':
   item.update(readerText=item['summary']+'\n\n'+item['why'],readerKind='reviewed');continue
  original=item.get('readerOriginal','')
  if not original:continue
  key=hashlib.sha256(original.encode()).hexdigest()
  if item['originalLanguage']=='sv' and detector.detect_language_of(original)==swedish:memo[key]=original
  if key in memo:
   if memo[key]:item.update(readerText=localize(memo[key]),readerKind='excerpt',summary=localize(memo[key]))
  else:pending.append((item,key,original))
 for start in range(0,len(pending),16):
  chunk=pending[start:start+16]
  results=translator.translate_batch([tokenizer.encode(t,out_type=str) for _,_,t in chunk],beam_size=4,max_decoding_length=300,repetition_penalty=1.08)
  for (item,key,original),result in zip(chunk,results):
   text=localize(tokenizer.decode(result.hypotheses[0]))
   valid=bool(text) and detector.detect_language_of(text)==swedish and re.findall(r'\d+',original)==re.findall(r'\d+',text)
   memo[key]=text if valid else ''
   if valid:item.update(readerText=text,readerKind='excerpt',summary=text)
 for item in items:item.pop('readerOriginal',None)
 cachefile.write_text(json.dumps(memo,ensure_ascii=False))
 print(f'Läsvy: {sum(bool(i.get("readerText")) for i in items)}/{len(items)} med svensk text',flush=True)
