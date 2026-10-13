import datetime as dt,importlib.util,json,pathlib,sys,unittest
sys.path.insert(0,'scripts');spec=importlib.util.spec_from_file_location('x','scripts/fetch-x.py');x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
class XTests(unittest.TestCase):
 def setUp(self):
  self.account={'id':'test-x','handle':'example','userId':'123','name':'Example'};self.now=dt.datetime(2026,10,12,12,tzinfo=dt.timezone.utc)
  self.post={'id_str':'2109000000000000000','user':{'id_str':'123','screen_name':'example','name':'Example'},'created_at':'Mon Oct 12 10:00:00 +0000 2026','full_text':'Bitcoin network update published today.','lang':'en'}
 def test_original_identity_and_dates(self):
  n=x.parse_post(self.post,self.account,self.now);self.assertEqual(n['publishedAt'],'2026-10-12T10:00:00Z');self.assertFalse(n['verified']);self.assertEqual(n['coins'],['BTC'])
  self.post['user']['id_str']='impostor';self.assertIsNone(x.parse_post(self.post,self.account,self.now))
 def test_old_popular_and_future_posts_not_current(self):
  for value in ['Tue Oct 12 10:00:00 +0000 2021','Mon Oct 12 14:00:00 +0000 2026','bad']:
   self.post['created_at']=value;self.assertIsNone(x.parse_post(self.post,self.account,self.now))
 def test_irrelevant_replies_and_promotions_rejected(self):
  for text in ['Beautiful day at the beach','Bitcoin giveaway sign up now']:
   self.post['full_text']=text;self.assertIsNone(x.parse_post(self.post,self.account,self.now))
  self.post['full_text']='Bitcoin is interesting';self.post['in_reply_to_status_id_str']='123';self.assertIsNone(x.parse_post(self.post,self.account,self.now))
 def test_cited_post_still_needs_original_identity(self):
  self.post['full_text']='More orange.';context={'title':'Bitcoin purchase discussed by company chair','url':'https://example.org/news'}
  self.assertIsNotNone(x.parse_post(self.post,self.account,self.now,context));self.post['user']['screen_name']='other';self.assertIsNone(x.parse_post(self.post,self.account,self.now,context))
 def test_timeline_deduplicates(self):
  entry={'type':'tweet','content':{'tweet':self.post}};payload='<script id="__NEXT_DATA__" type="application/json">'+json.dumps({'props':{'pageProps':{'timeline':{'entries':[entry,entry]}}}})+'</script>'
  rows,_=x.parse_timeline(payload,self.account,self.now);self.assertEqual(len(rows),1)
  with self.assertRaises(Exception):x.parse_timeline('<html>Login</html>',self.account,self.now)
 def test_unpinned_profile_is_resolved_only_from_one_matching_author(self):
  account={'id':'mmcrypto-x','handle':'MMCrypto','name':'MMCrypto'}
  post={**self.post,'id_str':'2109000000000000001','user':{'id_str':'123456789','screen_name':'MMCrypto','name':'MMCrypto'}}
  entry={'type':'tweet','content':{'tweet':post}};payload='<script id="__NEXT_DATA__" type="application/json">'+json.dumps({'props':{'pageProps':{'timeline':{'entries':[entry]}}}})+'</script>'
  rows,_=x.parse_timeline(payload,account,self.now);self.assertEqual(len(rows),1);self.assertEqual(rows[0]['handle'],'MMCrypto')
  impostor={**post,'user':{'id_str':'987654321','screen_name':'other','name':'Other'}}
  payload='<script id="__NEXT_DATA__" type="application/json">'+json.dumps({'props':{'pageProps':{'timeline':{'entries':[entry,{'type':'tweet','content':{'tweet':impostor}}]}}}})+'</script>'
  rows,_=x.parse_timeline(payload,account,self.now);self.assertEqual(len(rows),1)
 def test_media_host_allowlist(self):
  self.post['photos']=[{'url':'https://pbs.twimg.com/image.jpg'},{'url':'https://pbs.twimg.com.evil.test/image.jpg'},{'url':'javascript:alert(1)'}]
  n=x.parse_post(self.post,self.account,self.now);self.assertEqual(len(n['media']),1)
 def test_balanced_retention_keeps_quieter_sources(self):
  accounts=[{'id':'busy'},{'id':'quiet'}];posts={}
  for source,count in [('busy',80),('quiet',4)]:
   for i in range(count):
    pid=f'{2109000000000000000+i}'
    posts[pid]={'sourceId':source,'publishedAt':(self.now-dt.timedelta(minutes=i)).isoformat(),'id':pid}
  kept=x.balanced_posts(posts,accounts,per_account=30,maximum=40)
  self.assertEqual(sum(p['sourceId']=='quiet' for p in kept),4)
  self.assertEqual(sum(p['sourceId']=='busy' for p in kept),30)
if __name__=='__main__':unittest.main()

class XFailureTests(unittest.TestCase):
 def test_outage_retains_recent_posts(self):
  import pathlib,tempfile,contextlib,io
  from unittest.mock import patch
  now=dt.datetime.now(dt.timezone.utc).isoformat()
  account={'id':'sample-x','name':'Sample','handle':'sample','userId':'12','type':'MEDIA'}
  post={'id':'2109000000000000000','handle':'sample','publishedAt':now,'sourceId':'sample-x','text':'Bitcoin update','media':[]}
  with tempfile.TemporaryDirectory() as folder:
   root=pathlib.Path(folder);(root/'scripts').mkdir();(root/'public/data').mkdir(parents=True)
   (root/'scripts/x-sources.json').write_text(json.dumps([account]));target=root/'public/data/x.json';target.write_text(json.dumps({'posts':[post],'sources':[],'discovery':{}}))
   with patch.object(x,'ROOT',root),patch.object(x,'TARGET',target),patch.object(x,'get',side_effect=TimeoutError),contextlib.redirect_stdout(io.StringIO()):x.main()
   data=json.loads(target.read_text());self.assertEqual(len(data['posts']),1);self.assertEqual(data['posts'][0]['id'],post['id']);self.assertEqual(data['posts'][0]['categories'],[]);self.assertEqual(data['sources'][0]['connection'],'error')

class LocalAssetTests(unittest.TestCase):
 def test_bitcoin_art_is_a_valid_local_webp_at_both_sizes(self):
  root=pathlib.Path(__file__).resolve().parents[1]
  for width in (640,1280):
   payload=(root/f'public/images/bitcoin-{width}.webp').read_bytes()
   self.assertEqual(payload[:4],b'RIFF')
   self.assertEqual(payload[8:12],b'WEBP')
