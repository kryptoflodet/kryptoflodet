"""Local English→Swedish translation. No paid API, credentials or source-text uploads."""
import hashlib,json,pathlib,re,urllib.request,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/translation'
MODEL_URL='https://argos-net.com/v1/translate-en_sv-1_5.argosmodel'
GLOSSARY={'quantum attacks':'kvantattacker','quantum attack':'kvantattack','stablecoins':'stabila kryptovalutor','stablecoin':'stabil kryptovaluta','bullish':'positiv marknadssyn','bearish':'negativ marknadssyn','breaking':'senaste nytt','treasury':'kryptoreserv','spot etf':'spot-ETF','tokenized':'tokeniserad','tokenization':'tokenisering','price prediction':'prisprognos','all-time high':'rekordnivå','all time high':'rekordnivå','on-chain':'på blockkedjan','whales':'storägare','whale':'storägare','airdrop':'tokenutdelning','staking':'låsning av kryptovaluta','rally':'kursuppgång','sell-off':'utförsäljning','selloff':'utförsäljning'}
GLOSSARY.update({'pris förutsägelse':'prisprognos','pris prediction':'prisprognos','cpi drop':'KPI-besked','phishing':'nätfiske','mint':'skapa','tokens':'kryptoenheter','etfs':'ETF:er','inflow streak':'följd av nettoinflöden','inflows':'inflöden','outflows':'utflöden','cash':'kontanter','holding':'innehav','trading':'handel','bull run':'uppgångsfas','whale alert':'storägarbevakning'})
def prepare_model():
 if (CACHE/'en_sv/model/model.bin').exists():return
 CACHE.mkdir(parents=True,exist_ok=True)
 archive=CACHE/'en-sv.zip'
 urllib.request.urlretrieve(MODEL_URL,archive)
 with zipfile.ZipFile(archive) as z:
  for member in z.namelist():
   if not (member.startswith('en_sv/model/') or member=='en_sv/sentencepiece.model'):continue
   target=(CACHE/member).resolve()
   if not target.is_relative_to(CACHE.resolve()):raise ValueError('Invalid model path')
   z.extract(member,CACHE)
 archive.unlink()
def localize(text):
 for a,b in GLOSSARY.items():text=re.sub(r'\b'+re.escape(a)+r'\b',b,text,flags=re.I)
 return text.strip()
def translate_items(items):
 import ctranslate2,sentencepiece
 from lingua import Language,LanguageDetectorBuilder
 prepare_model()
 tokenizer=sentencepiece.SentencePieceProcessor(model_file=str(CACHE/'en_sv/sentencepiece.model'))
 translator=ctranslate2.Translator(str(CACHE/'en_sv/model'),device='cpu',compute_type='int8',intra_threads=2)
 detector=LanguageDetectorBuilder.from_languages(Language.SWEDISH,Language.ENGLISH,Language.GERMAN,Language.FRENCH,Language.SPANISH).build()
 cachefile=CACHE/'headlines-v3.json'
 memo=json.loads(cachefile.read_text()) if cachefile.exists() else {}
 accepted=[];pending=[];texts=[]
 for item in items:
  if item['originalLanguage']=='sv':
   lang=detector.detect_language_of(item['originalTitle'])
   if lang==Language.SWEDISH:item.update(title=item['originalTitle'],translationStatus='original-sv');accepted.append(item);continue
   if lang!=Language.ENGLISH:continue
   item['originalLanguage']='en'
  key=hashlib.sha256(('v3:'+item['originalTitle']).encode()).hexdigest();item['_translationKey']=key
  if key in memo:item.update(title=memo[key],translationStatus='machine-sv');accepted.append(item)
  else:pending.append(item);texts.append(item['originalTitle'])
 for start in range(0,len(texts),32):
  chunk=texts[start:start+32]
  # Preserve proper names; localize common crypto terminology after translation.
  inputs=[tokenizer.encode(t,out_type=str) for t in chunk]
  result=translator.translate_batch(inputs,beam_size=4,max_decoding_length=220,repetition_penalty=1.08)
  for item,out in zip(pending[start:start+32],result):
   title=localize(tokenizer.decode(out.hypotheses[0]))
   original_numbers=re.findall(r'\d+',item['originalTitle'])
   translated_numbers=re.findall(r'\d+',title)
   # Do not publish untranslated or numerically altered headlines.
   if not title or detector.detect_language_of(title)!=Language.SWEDISH or original_numbers!=translated_numbers:continue
   memo[item['_translationKey']]=title;item.update(title=title,translationStatus='machine-sv');accepted.append(item)
 for item in accepted:
  item.pop('_translationKey',None)
  item['summary']=item['summary'].replace(' Rubriken visas på originalspråket.','')
  item['translation']=item['title']
 cachefile.write_text(json.dumps(memo,ensure_ascii=False))
 print(f'Svenska språkgrinden: {len(accepted)}/{len(items)} rubriker godkända; resten väntar på översättning',flush=True)
 return sorted(accepted,key=lambda n:n['publishedAt'],reverse=True)
if __name__=='__main__':prepare_model()
