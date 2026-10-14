"""Translate public X text locally with a purpose-trained English–Swedish model.
Publication checks are deterministic; the model does not approve its own output.
"""
import json,re,signal,sys,time
from x_translation_model import prepare,MODEL,MODEL_HASH
from x_translate import input_text,valid_translation,normalize_translation,ENGINE,CHECK_VERSION
from swedish_quality import is_swedish_quality
# This is the upstream TranslateGemma text template, without the BOS token that
# llama.cpp inserts. Keep source text separate from translation instructions.
SYSTEM='You are a professional English (en) to Swedish (sv) translator. Your goal is to accurately convey the meaning and nuances of the original English text while adhering to Swedish grammar, vocabulary, and cultural sensitivities.\nProduce only the Swedish translation, without any additional explanations or commentary. Please translate the following English text into Swedish:\n\n\n'
EDIT='';REVIEW='deterministic-source-checks'
def clean_source(text):return input_text(text)
def language_ok(text,detector,swedish):
 prose=re.sub(r'\b(?:Wu Blockchain|Blockchain[․.]com|High Court|Token Terminal|BNB Chain)\b','källa',text)
 return is_swedish_quality(prose) and detector.detect_language_of(prose)==swedish

def translation_source(text):
 source=clean_source(text)
 terms={r'\bbears\b':'traders who expect prices to fall',r'\bbulls\b':'traders who expect prices to rise',
 r'\bwhales\b':'large investors',r'\bwhale\b':'large investor',
 r'\bopening longs\b':'opening positions that profit when prices rise',
 r'\bgoing long\b':'investing in positions that profit when prices rise',
 r'\bsmart money\b':'experienced investors',
 r'\btokenized ETF market cap\b':'market value of tokenized exchange-traded funds',
 r'\bEveryone wants in\b':'Everyone wants to participate'}
 for pattern,replacement in terms.items():source=re.sub(pattern,replacement,source,flags=re.I)
 return source

def parts(source):
 """Preserve paragraphs and translate each bounded part, including long posts."""
 chunks=[]
 for paragraph in re.split(r'\n\s*\n',source):
  sentences=re.split(r'(?<=[.!?])\s+(?=[A-Z"“])',paragraph) if len(paragraph)>1100 else [paragraph]
  current=''
  for sentence in sentences:
   if len(current)+len(sentence)>1100 and current:chunks.append(current);current=''
   current+=((' ' if current else '')+sentence)
  if current:chunks.append(current)
 return chunks

class Translator:
 def __init__(self):
  prepare()
  from llama_cpp import Llama
  from lingua import Language,LanguageDetectorBuilder
  self.swedish=Language.SWEDISH
  self.detector=LanguageDetectorBuilder.from_languages(Language.SWEDISH,Language.ENGLISH,Language.BOKMAL,Language.DANISH,Language.GERMAN).build()
  self.model=Llama(model_path=str(MODEL),n_ctx=2048,n_threads=2,n_batch=256,verbose=False)
 def translate(self,original,deadline):
  source=input_text(original);translated=[]
  for part in parts(source):
   if time.monotonic()>deadline:return None
   prepared=translation_source(part)
   prompt='<start_of_turn>user\n'+SYSTEM+prepared+'<end_of_turn>\n<start_of_turn>model\n'
   reply=self.model.create_completion(prompt=prompt,max_tokens=1100,temperature=0,stop=['<end_of_turn>','<eos>'])
   if reply['choices'][0].get('finish_reason')=='length':return None
   text=normalize_translation(part,reply['choices'][0]['text'])
   if not valid_translation(part,text) or not language_ok(text,self.detector,self.swedish):
    print('Rejected Swedish translation:',part,text,file=sys.stderr,flush=True);return None
   translated.append(text)
  text='\n\n'.join(translated)
  print('Swedish translation:',text,file=sys.stderr,flush=True)
  return text if valid_translation(source,text) else None

def main():
 request=json.load(sys.stdin);translator=Translator();deadline=time.monotonic()+min(int(request.get('seconds',1200)),1500);output=[]
 def stop(*_):
  nonlocal deadline
  deadline=-1;raise TimeoutError('Translation time budget exhausted')
 signal.signal(signal.SIGALRM,stop);signal.alarm(max(1,int(deadline-time.monotonic())))
 for item in request['items']:
  if time.monotonic()>deadline:break
  try:
   text=translator.translate(item['text'],deadline)
   output.append({'id':item['id'],'text':text,'checked':bool(text)})
  except Exception as error:print('Swedish translation retry:',item['id'],type(error).__name__,file=sys.stderr,flush=True)
 signal.alarm(0);json.dump(output,sys.stdout,ensure_ascii=False)
if __name__=='__main__':main()
