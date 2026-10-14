"""Keep permanent, readable X snapshots so shared links outlive the rolling feed."""
import copy,datetime as dt,json,pathlib,re
from x_language import source_hash,TRUSTED_SWEDISH_ENGINES,CHECKED_ENGINE,CHECK_VERSION,apply_language
ROOT=pathlib.Path(__file__).resolve().parents[1]

def archivable_post(post):
 if not isinstance(post,dict):return False
 pid=post.get('id','');handle=post.get('handle','')
 if not isinstance(pid,str) or not re.fullmatch(r'\d{15,22}',pid):return False
 if not isinstance(handle,str) or not re.fullmatch(r'[A-Za-z0-9_]{1,15}',handle):return False
 if post.get('url')!=f'https://x.com/{handle}/status/{pid}' or post.get('kind')!='original-x-post':return False
 if not isinstance(post.get('text'),str) or not 0<len(post['text'])<=5000:return False
 if not isinstance(post.get('author'),str) or not post['author']:return False
 if not all(isinstance(post.get(key),list) and all(isinstance(value,str) for value in post[key]) for key in ('coins','categories')):return False
 try:
  published=dt.datetime.fromisoformat(post['publishedAt'].replace('Z','+00:00'))
  if published.tzinfo is None:return False
 except (KeyError,ValueError,AttributeError,TypeError):return False
 return isinstance(post.get('originalLanguage'),str)

def readable_post(post):
 if not archivable_post(post):return False
 if post.get('originalLanguage')=='sv':return True
 swedish=post.get('swedish',{})
 return isinstance(swedish,dict) and isinstance(swedish.get('text'),str) and 0<len(swedish['text'])<=15000 and swedish.get('method') in ('summary','translation') and swedish.get('engine') in TRUSTED_SWEDISH_ENGINES and (swedish.get('engine')!=CHECKED_ENGINE or swedish.get('qualityVersion')==CHECK_VERSION) and swedish.get('sourceHash')==source_hash(post['text'])

def archive_posts(previous,posts,now):
 saved={}
 for post in previous:
  if not archivable_post(post):continue
  p=copy.deepcopy(post)
  if not readable_post(p):p.pop('swedish',None)
  saved[p['id']]=p
 for post in posts:
  if not archivable_post(post):continue
  p=copy.deepcopy(post);prior=saved.get(p['id'])
  # A missing/rejected translation never removes an authenticated original.
  if not readable_post(p):
   p.pop('swedish',None)
   if prior and prior['text']==p['text'] and prior['url']==p['url'] and prior.get('swedish',{}).get('engine')==CHECKED_ENGINE and readable_post(prior):p['swedish']=copy.deepcopy(prior['swedish'])
  p.pop('originalCheckedAt',None)
  p['archivedAt']=prior.get('archivedAt',now) if prior and prior['text']==p['text'] else now
  saved[p['id']]=p
 return sorted(saved.values(),key=lambda p:int(p['id']),reverse=True)

def main():
 target=ROOT/'public/data/x-archive.json'
 previous=json.loads(target.read_text()).get('posts',[]) if target.exists() else []
 live=json.loads((ROOT/'public/data/x.json').read_text())
 posts=archive_posts(previous,live['posts'],dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z'))
 reviews=json.loads((ROOT/'scripts/x-summaries.json').read_text())
 counts,_=apply_language(posts,reviews)
 data={'schemaVersion':1,'posts':posts,'language':counts}
 text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
 if not target.exists() or target.read_text()!=text:
  temporary=target.with_suffix('.tmp');temporary.write_text(text);temporary.replace(target)
 print(f"Permanent X pages: {len(data['posts'])}",flush=True)

if __name__=='__main__':main()
