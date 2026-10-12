"""Optional self-hosted RSSHub connector; never depends on a public demo instance.
RSSHUB_BASE_URL is supplied as a GitHub secret. Cookies stay on the RSSHub host.
"""
import os,json,pathlib
from urllib.parse import urlsplit

def sources(root=None):
 root=root or pathlib.Path(__file__).resolve().parents[1]
 base=os.environ.get('RSSHUB_BASE_URL','').rstrip('/')
 if base and (urlsplit(base).scheme!='https' or not urlsplit(base).hostname):base=''
 result=[]
 for account in json.loads((root/'scripts/x-sources.json').read_text()):
  s=dict(account,language='en',channel='X',coverage='Inlägg från kontots X-flöde via egen RSSHub. Uttalanden är inte oberoende bekräftade fakta.')
  s['url']=base+'/twitter/user/'+s['handle']+'/exclude_rts_replies' if base else 'https://x.com/'+s['handle']
  if not base:s['disabledReason']='Ej ansluten. Kräver en fungerande egen RSSHub-instans; publika RSSHub/Nitter-alternativ svarade inte. RSS och YouTube körs oberoende.'
  result.append(s)
 return result
