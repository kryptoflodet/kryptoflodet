"""Apply source-bound Swedish originals, reviews, rules and current translation cache.
The next workflow step automatically translates the remaining originals.
"""
import hashlib,json,pathlib,re,datetime as dt
ROOT=pathlib.Path(__file__).resolve().parents[1]
VERSION='x-sv-rules-v1'
CHECKED_ENGINE='translategemma-12b-sv-v1'
CHECK_VERSION='x-swedish-v5'
TRUSTED_SWEDISH_ENGINES={'reviewed',VERSION,CHECKED_ENGINE}
ASSET=r'(?:Bitcoin|Ethereum|Solana|SUI|XRP|BTC|ETH|SOL)'
# English numeric syntax only. Formatting must never change numeric value or unit.
AMOUNT=r'(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?:[kKmMbB]| million| billion)?'

def source_hash(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def clean(text):
 text=re.sub(r'https?://\S+','',text)
 # Only presentation noise, not words, qualifiers, punctuation or named entities.
 text=re.sub(r'[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F]','',text)
 text=re.sub(r'^\s*(?:JUST IN|BREAKING|ICYMI):\s*','',text,flags=re.I)
 return re.sub(r'\s+',' ',text).strip()
def amount_sv(value):
 value=re.sub(r'(?<=\d),(?=\d{3}(?:\D|$))',' ',value)
 value=re.sub(r'(?<=\d)\.(?=\d)',',',value)
 return re.sub(r'(?<=\d)\s*(billion|million|[kmb])$',lambda m:{'billion':' miljarder','million':' miljoner','b':' miljarder','m':' miljoner','k':' tusen'}[m[1].lower()],value,flags=re.I)
def sentence_rule(source):
 # Full matches only: trailing caveats, negations, quoted denials and instructions
 # cannot be silently dropped. Captures are copied, never inferred.
 s=source.strip().rstrip('.!')
 patterns=[
  (rf'({ASSET}) (?:just )?reclaims \$({AMOUNT})',lambda m:f'{m[1]} är åter på {amount_sv(m[2])} dollar.'),
  (rf'({ASSET}) (?:just )?reclaimed \$({AMOUNT})',lambda m:f'{m[1]} är åter på {amount_sv(m[2])} dollar.'),
  (rf'({ASSET}) falls below \$({AMOUNT})',lambda m:f'{m[1]} faller under {amount_sv(m[2])} dollar.'),
  (rf'I think ({ASSET}) will hit \$({AMOUNT}) this cycle',lambda m:f'Jag tror att {m[1]} når {amount_sv(m[2])} dollar under den här cykeln.'),
  (rf'My ({ASSET}) price target is \$({AMOUNT})(?:-\$({AMOUNT}))?',lambda m:f'Mitt kursmål för {m[1]} är {amount_sv(m[2])}'+(f'–{amount_sv(m[3])}' if m[3] else '')+' dollar.'),
  (rf'({ASSET}) could reach \$({AMOUNT})',lambda m:f'{m[1]} skulle kunna nå {amount_sv(m[2])} dollar.'),
  (rf'({ASSET}) is no longer projected to reclaim \$({AMOUNT}) this year',lambda m:f'{m[1]} väntas inte längre åter nå {amount_sv(m[2])} dollar i år.'),
  (rf'(Bitcoin|Ethereum|BTC|ETH) ETFs saw \$({AMOUNT}) in (inflows|outflows)',lambda m:f'ETF:er för {m[1]} noterade '+('inflöden' if m[3].lower()=='inflows' else 'utflöden')+f' på {amount_sv(m[2])} dollar.'),
 ]
 for pattern,render in patterns:
  if render and (m:=re.fullmatch(pattern,s,re.I)):return render(m)
 m=re.fullmatch(rf"(Michael Saylor['’]s ['’]?Strategy['’]?|Tom Lee['’]s ['’]?BitMine['’]?)( \$MSTR)? buys ({AMOUNT}) (Bitcoin|\$ETH) worth \$({AMOUNT})",s,re.I)
 if m:
  company='Michael Saylors Strategy' if m[1].lower().startswith('michael') else 'Tom Lees BitMine'
  return company+(' (MSTR)' if m[2] else '')+f' köper {amount_sv(m[3])} {m[4].lstrip("$")} för {amount_sv(m[5])} dollar.'
 m=re.fullmatch(rf'They now hold a total of ({AMOUNT}) \$BTC valued at \$({AMOUNT})',s,re.I)
 if m:return f'De har nu sammanlagt {amount_sv(m[1])} BTC till ett värde av {amount_sv(m[2])} dollar.'
 m=re.fullmatch(rf'({ASSET}) (?:rises|climbs) (to|above) \$({AMOUNT})',s,re.I)
 if m:return f'{m[1]} stiger '+('till' if m[2].lower()=='to' else 'över')+f' {amount_sv(m[3])} dollar.'
 return None

def automatic(text):
 normalized=clean(text)
 # Preserve explicit speculation; an exact fixed expression can be translated
 # without deciding what the author is hinting at.
 if normalized in {"There’s always room for more orange.","There's always room for more orange."}:
  return 'Det finns alltid plats för mer orange.','translation'
 # For long text, retain all substantive sentences (at most three). No guessed
 # summary of an unmatched paragraph and no truncation at a token boundary.
 sentences=re.split(r'(?<=[.!?])\s+',normalized)
 if not 1<=len(sentences)<=3:return None
 outputs=[sentence_rule(s) for s in sentences]
 if not all(outputs):return None
 result=' '.join(outputs)
 return result,'translation'

def apply_language(posts,reviews):
 counts={'original':0,'reviewed':0,'automatic':0,'pending':0};queue=[]
 for post in posts:
  # Cached text must be revalidated on every run. Never reuse an old translation
  # after an X edit or while its review has been withdrawn.
  cached=post.pop('swedish',None);post.pop('swedishSummary',None)
  text=post.get('text','');digest=source_hash(text)
  if post.get('originalLanguage')=='sv':
   post['swedish']={'text':text,'method':'original','sourceHash':digest,'engine':'original'};counts['original']+=1;continue
  review=reviews.get(post['id'],{})
  if review.get('sourceUrl')==post.get('url') and review.get('textSha256')==digest and isinstance(review.get('text'),str) and review['text'] and review.get('method') in ('translation','summary'):
   if review.get('sourceTruncated'):post['sourceTruncated']=True
   post['swedish']={'text':review['text'],'method':review['method'],'sourceHash':digest,'engine':'reviewed'};counts['reviewed']+=1;continue
  if isinstance(cached,dict) and cached.get('sourceHash')==digest and cached.get('engine') in TRUSTED_SWEDISH_ENGINES and cached.get('engine')!='reviewed' and (cached.get('engine')!=CHECKED_ENGINE or cached.get('qualityVersion')==CHECK_VERSION) and isinstance(cached.get('text'),str) and 0<len(cached['text'])<=15000:
   post['swedish']=cached;counts['automatic']+=1;continue
  auto=automatic(text) if post.get('originalLanguage')=='en' else None
  if auto:
   post['swedish']={'text':auto[0],'method':auto[1],'sourceHash':digest,'engine':VERSION};counts['automatic']+=1
  else:
   counts['pending']+=1;queue.append({'id':post['id'],'sourceUrl':post.get('url'),'originalLanguage':post.get('originalLanguage'),'text':text,'textSha256':digest,'reason':'needs_language_review'})
 return counts,queue

def main():
 target=ROOT/'public/data/x.json'
 data=json.loads(target.read_text());reviews=json.loads((ROOT/'scripts/x-summaries.json').read_text())
 counts,queue=apply_language(data['posts'],reviews);data['language']={'version':VERSION,'checkedAt':dt.datetime.now(dt.timezone.utc).isoformat(),**counts}
 temp=target.with_suffix('.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temp.replace(target)
 state=ROOT/'state';state.mkdir(exist_ok=True);(state/'x-language-review.json').write_text(json.dumps({'items':queue,'counts':counts},ensure_ascii=False,indent=2)+'\n')
 print('X Swedish:',json.dumps(counts),flush=True)
if __name__=='__main__':main()
