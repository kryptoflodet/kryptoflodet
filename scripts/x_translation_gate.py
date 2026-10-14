"""Refuse a deployment containing an untranslated X original or stale translation."""
import json,pathlib
from x_archive import readable_post
ROOT=pathlib.Path(__file__).resolve().parents[1]
def untranslated(posts):
 return [post['id'] for post in posts if not readable_post(post) or (post.get('originalLanguage')!='sv' and post.get('swedish',{}).get('method')!='translation')]
def main():
 counts={}
 for name in ('x.json','x-archive.json'):
  posts=json.loads((ROOT/'public/data'/name).read_text())['posts']
  missing=untranslated(posts)
  if missing:raise RuntimeError(f'{name}: {len(missing)} X-inlägg väntar på fullständig svensk översättning: '+', '.join(missing))
  counts[name]=len(posts)
 print('Alla X-original har källbundna svenska översättningar:',json.dumps(counts),flush=True)
if __name__=='__main__':main()
