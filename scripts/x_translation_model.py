"""Pinned, local translation model. No remote inference or API credentials."""
import hashlib,pathlib,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
MODEL=ROOT/'.cache/x-translation/model12.gguf'
MODEL_REV='41d7c8aa650b26791225ad9d0597e674e680da96'
MODEL_HASH='b7aac4b4be7ab0c49b6556c29c4467e74313df7f1e95d9f9676bb2adf0afa528'
MODEL_URL=f'https://huggingface.co/mradermacher/translategemma-12b-it-GGUF/resolve/{MODEL_REV}/translategemma-12b-it.Q4_K_M.gguf?download=true'
def prepare():
 MODEL.parent.mkdir(parents=True,exist_ok=True)
 if not MODEL.exists():
  tmp=MODEL.with_suffix('.tmp')
  with urllib.request.urlopen(MODEL_URL,timeout=90) as r,tmp.open('wb') as f:
   while chunk:=r.read(8*1024*1024):f.write(chunk)
  tmp.replace(MODEL)
 h=hashlib.sha256()
 with MODEL.open('rb') as f:
  while chunk:=f.read(8*1024*1024):h.update(chunk)
 if h.hexdigest()!=MODEL_HASH:raise ValueError('Swedish translation model checksum mismatch')
if __name__=='__main__':prepare()
