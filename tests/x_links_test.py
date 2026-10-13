import contextlib,copy,datetime as dt,importlib.util,io,json,pathlib,sys,tempfile,unittest
from unittest.mock import patch
from urllib.error import HTTPError
sys.path.insert(0,'scripts')
from x_archive import archive_posts,readable_post
from x_language import source_hash
spec=importlib.util.spec_from_file_location('x_links_fetch','scripts/fetch-x.py');x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)

class SourceFallbackTests(unittest.TestCase):
 def setUp(self):
  self.now=dt.datetime(2026,10,13,8,tzinfo=dt.timezone.utc)
  self.account={'id':'sample-x','name':'Sample – X','handle':'sample','userId':'12345','type':'MEDIA'}
 def test_rate_limit_is_respected_on_next_run(self):
  error=HTTPError('https://syndication.twitter.com/',429,'Too many requests',{'Retry-After':'3600'},None)
  with patch.object(x,'get',side_effect=error),contextlib.redirect_stdout(io.StringIO()):status,rows=x.fetch_profile(self.account,{},self.now)
  self.assertEqual(rows,[]);self.assertEqual(status['connection'],'error')
  with patch.object(x,'get') as fetch:again,_=x.fetch_profile(self.account,status,self.now+dt.timedelta(minutes=5))
  fetch.assert_not_called();self.assertTrue(all(a['result']=='cooldown' for a in again['attempts']))
 def test_approved_strategy_articles_are_discovery_candidates(self):
  item={'originalUrl':'https://bitcoinmagazine.com/news/strategy-buys-bitcoin','originalTitle':'Strategy adds Bitcoin','publishedAt':'2026-10-12T12:00:00Z'}
  bad={**item,'originalUrl':'https://bitcoinmagazine.com.evil.test/news/test'}
  future={**item,'originalUrl':'https://coindesk.com/future','publishedAt':'2026-10-14T12:00:00Z'}
  self.assertEqual(x.article_references([item,item,bad,future],self.now),[item])
 def test_individual_post_works_when_both_profile_routes_fail(self):
  now=dt.datetime.now(dt.timezone.utc)
  raw={'id_str':'2109513358278054238','user':{'id_str':'12345','screen_name':'sample','name':'Sample'},'created_at':(now-dt.timedelta(hours=1)).isoformat(),'text':'Bitcoin network update.','lang':'en'}
  with tempfile.TemporaryDirectory() as folder:
   root=pathlib.Path(folder);(root/'scripts').mkdir();(root/'public/data').mkdir(parents=True)
   (root/'scripts/x-sources.json').write_text(json.dumps([self.account]));(root/'scripts/x-posts.json').write_text(json.dumps([{'handle':'sample','id':raw['id_str']}]))
   target=root/'public/data/x.json';target.write_text(json.dumps({'posts':[],'sources':[]}))
   def get(url):
    if 'tweet-result' in url:return json.dumps(raw)
    raise HTTPError(url,429,'Too many requests',{},None)
   with patch.object(x,'ROOT',root),patch.object(x,'TARGET',target),patch.object(x,'get',side_effect=get),contextlib.redirect_stdout(io.StringIO()):x.main()
   data=json.loads(target.read_text());status=data['sources'][0]
   self.assertEqual(status['connection'],'limited');self.assertEqual(status['profileConnection'],'error');self.assertEqual(status['method'],'individual-post')
   self.assertEqual(data['posts'][0]['url'],'https://x.com/sample/status/'+raw['id_str']);self.assertIsNotNone(status['lastSuccessAt'])
   self.assertFalse(data['posts'][0]['verified'],'Verifying an original URL does not verify the author claim')
 def test_mmcrypto_identity_is_pinned(self):
  accounts=json.loads(pathlib.Path('scripts/x-sources.json').read_text());account=next(a for a in accounts if a['handle']=='MMCrypto')
  self.assertEqual(account['userId'],'904700529988820992')
  raw={'id_str':'2109513358278054238','user':{'id_str':'wrong','screen_name':'MMCrypto'},'created_at':self.now.isoformat(),'text':'Bitcoin update','lang':'en'}
  self.assertIsNone(x.parse_post(raw,account,self.now))

class PermanentXLinkTests(unittest.TestCase):
 def setUp(self):
  text='Bitcoin update. <script>alert(1)</script> https://t.co/example'
  self.post={'id':'2109513358278054238','handle':'example','author':'Example','url':'https://x.com/example/status/2109513358278054238','publishedAt':'2026-10-12T05:15:52Z','kind':'original-x-post','originalLanguage':'en','text':text,'coins':['BTC'],'categories':['Bitcoin'],'media':[],
   'swedish':{'text':'Kontot beskriver en uppdatering av bitcoin.','method':'summary','sourceHash':source_hash(text),'engine':'reviewed'}}
 def test_link_survives_feed_expiry_and_outage(self):
  archive=archive_posts([], [self.post], '2026-10-13T08:00:00Z')
  later=archive_posts(archive,[], '2027-01-01T08:00:00Z')
  self.assertEqual(later,archive);self.assertTrue(readable_post(later[0]))
 def test_unsafe_url_and_stale_translation_are_not_archived(self):
  self.assertFalse(readable_post({**self.post,'url':'javascript:alert(1)'}))
  changed=copy.deepcopy(self.post);changed['text']='Completely different Bitcoin claim'
  self.assertFalse(readable_post(changed));self.assertEqual(archive_posts([], [changed], '2026-10-13T08:00:00Z'),[])
 def test_export_has_own_metadata_original_link_and_escaped_text(self):
  spec=importlib.util.spec_from_file_location('x_pages','scripts/build-pages.py');pages=importlib.util.module_from_spec(spec);spec.loader.exec_module(pages)
  path,html=pages.x_page(self.post)
  self.assertEqual(path,'/x/'+self.post['id']+'/');self.assertIn('rel="canonical" href="https://kryptokollen.online'+path+'"',html)
  self.assertIn('property="og:url" content="https://kryptokollen.online'+path+'"',html);self.assertIn('name="twitter:card"',html)
  self.assertIn('href="'+self.post['url']+'"',html);self.assertIn('href="https://t.co/example"',html)
  self.assertNotIn('<script>alert(1)</script>',html);self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;',html)
 def test_every_saved_post_has_a_page_after_build(self):
  dist=pathlib.Path('dist');archive=pathlib.Path('public/data/x-archive.json')
  if not dist.exists() or not archive.exists():self.skipTest('Run archive and build first')
  posts=json.loads(archive.read_text())['posts'];self.assertGreater(len(posts),0)
  for post in posts:
   page=dist/'x'/post['id']/'index.html';self.assertTrue(page.exists(),post['id'])
   self.assertIn('href="'+post['url']+'"',page.read_text())

if __name__=='__main__':unittest.main()
