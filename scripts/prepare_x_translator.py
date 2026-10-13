"""Download pinned translation weights; all inference runs on the Actions CPU."""
import hashlib,json,os,pathlib,urllib.request,concurrent.futures
ROOT=pathlib.Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/'scripts/x-translation-model.json').read_text())
MODEL=pathlib.Path(os.environ.get('X_TRANSLATION_MODEL_PATH',str(ROOT/'.cache/x-translation/model')))

def checksum(path):
 digest=hashlib.sha256()
 with path.open('rb') as f:
  while chunk:=f.read(1024*1024):digest.update(chunk)
 return digest.hexdigest()

def prepare():
 def download(pair):
  name,expected=pair;path=MODEL/name
  if path.exists() and checksum(path)==expected:return
  path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp')
  url=f"https://huggingface.co/{MANIFEST['model']}/resolve/{MANIFEST['revision']}/{name}"
  with urllib.request.urlopen(url,timeout=60) as response,tmp.open('wb') as f:
   while chunk:=response.read(1024*1024):f.write(chunk)
  if checksum(tmp)!=expected:tmp.unlink();raise ValueError('Translation model checksum mismatch: '+name)
  tmp.replace(path);print('Downloaded local X translation asset:',name,flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(download,MANIFEST['files'].items()))
 print('Local X translation model ready:',MANIFEST['engine'],flush=True)

if __name__=='__main__':prepare()
