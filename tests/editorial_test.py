import datetime as dt,importlib.util,json,pathlib,sys,unittest
from unittest.mock import patch
sys.path.insert(0,'scripts')
from editorial import canonical_url,deduplicate,enrich,readable,select_important
from local_editor import validate
from x_sources import sources
class EditorialTests(unittest.TestCase):
 def item(self,**extra):
  return dict(id='1234567890',title='Bitcoin får ett nytt börshandlat instrument',originalTitle='Bitcoin ETF approved',originalText='',originalUrl='https://example.org/a',publishedAt='2026-10-12T08:00:00Z',importedAt='2026-10-12T09:00:00Z',translationStatus='edited-sv',readerText=' '.join(['svensk']*40),contentVersion=2,sourceType='MEDIA',coins=['BTC'],**extra)
 def test_canonical_and_dedup(self):
  self.assertEqual(canonical_url('https://www.example.org/a/?utm_source=x#y'),'https://example.org/a')
  self.assertEqual(canonical_url('https://twitter.com/saylor/status/1'),'https://x.com/saylor/status/1')
  for bad in ['javascript:alert(1)','https://user:password@example.org/','/relative']:
   with self.assertRaises(ValueError):canonical_url(bad)
  a=self.item();b=dict(a,originalUrl=a['originalUrl']+'?utm_source=x',readerText='')
  self.assertEqual(deduplicate([b,a]),[a])
 def test_freshness_and_forecast(self):
  now=dt.datetime(2026,10,12,12,tzinfo=dt.timezone.utc);a=enrich(self.item())
  old=dict(a,publishedAt='2026-09-01T08:00:00Z');future=dict(a,publishedAt='2026-10-13T08:00:00Z')
  self.assertEqual(select_important([old,future,a],now),[a])
  a['originalTitle']='Bitcoin analyst predicts record price';enrich(a)
  self.assertEqual(a['contentType'],'prognos');self.assertEqual(select_important([a],now),[])
 def test_multi_category_and_stable_slug(self):
  a=self.item();a['coins']=['SOL','SUI'];enrich(a);path=a['path'];a['title']='En uppdaterad rubrik';enrich(a)
  self.assertEqual(a['path'],path);self.assertTrue({'Solana','SUI','Altcoins','Institutionellt'}<=set(a['categories']))
 def test_missing_body_never_readable(self):
  self.assertFalse(readable(dict(self.item(),readerText='Bara en rubrik')))
 def test_generated_claim_guards(self):
  source='The Bitcoin fund reported inflows of 25 million on Monday. The company declined to provide a forecast.'
  draft={'title':'Bitcoinfonden redovisar nya inflöden','paragraphs':['Enligt fondens besked kom det in 25 miljoner under måndagen. Uppgiften gäller de inflöden som fonden själv har redovisat i sitt meddelande.','Bolaget lämnade inte någon prognos. Beskedet innehåller därmed ingen bedömning av hur utvecklingen väntas se ut framöver.'],'support':['The Bitcoin fund reported inflows of 25 million on Monday.','The company declined to provide a forecast.']}
  self.assertTrue(validate(draft,source));draft['title']='Bitcoinfonden får 90 miljoner';self.assertFalse(validate(draft,source))
  draft['title']='Bitcoinfonden redovisar nya inflöden';draft['support'][0]='fabricated evidence';self.assertFalse(validate(draft,source))
 def test_x_optional_and_correct_route(self):
  with patch.dict('os.environ',{'RSSHUB_BASE_URL':''}):self.assertTrue(all(x.get('disabledReason') for x in sources()))
  with patch.dict('os.environ',{'RSSHUB_BASE_URL':'https://rss.example.org'}):
   rows=sources();self.assertEqual(len(rows),5);self.assertEqual(rows[-1]["handle"],"BitcoinArchive");self.assertTrue(rows[-1]["url"].endswith("/BitcoinArchive/exclude_rts_replies"));self.assertTrue(all(x['url'].endswith('/exclude_rts_replies') for x in rows))
 def test_archive_x_seeds_are_bounded_and_have_reviewed_swedish(self):
  seeds=json.loads(pathlib.Path('scripts/x-posts.json').read_text());summaries=json.loads(pathlib.Path('scripts/x-summaries.json').read_text())
  archive=[x for x in seeds if x['handle']=='BitcoinArchive']
  self.assertEqual(len(archive),15)
  self.assertTrue(all(x['id'] in summaries and summaries[x['id']]['sourceUrl'].endswith('/'+x['id']) for x in archive))
class ExportTests(unittest.TestCase):
 def test_all_articles_have_safe_permanent_pages_and_metadata(self):
  from html.parser import HTMLParser
  spec=importlib.util.spec_from_file_location('pages','scripts/build-pages.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  self.assertNotIn('<script>alert',m.page('<script>alert(1)</script>','text','/test/','',{'headline':'</script><script>alert(1)</script>'}))
  if not pathlib.Path('dist/sitemap.xml').exists():self.skipTest('Run npm run build for export integration check')
  data=json.loads(pathlib.Path('public/data/news.json').read_text())
  for n in data['items']:
   self.assertTrue(readable(n),n['id']);text=(pathlib.Path('dist')/n['path'].strip('/')/'index.html').read_text()
   self.assertIn('https://kryptokollen.online'+n['path'],text);self.assertIn('NewsArticle',text);self.assertIn('Nyhetstext',text);self.assertIn('og:title',text)
  self.assertTrue(pathlib.Path('dist/kategori/sui/index.html').exists());self.assertTrue(pathlib.Path('dist/idag/index.html').exists())
 def test_video_hosts(self):
  spec=importlib.util.spec_from_file_location('pages','scripts/build-pages.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  n={'sourceId':'moon-video','originalUrl':'https://youtube.com.evil.test/watch?v=abcdefghijk','title':'test'};self.assertEqual(m.embed(n),'')
  n['originalUrl']='https://youtube.com/watch?v=abcdefghijk';self.assertIn('youtube-nocookie.com/embed/abcdefghijk',m.embed(n))
class FailureIsolationTests(unittest.TestCase):
 def test_all_sources_down_preserves_reviewed_archive(self):
  import tempfile,shutil,contextlib,io
  spec=importlib.util.spec_from_file_location('fetch_news','scripts/fetch-news.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  with tempfile.TemporaryDirectory() as folder:
   root=pathlib.Path(folder);(root/'public/data').mkdir(parents=True);(root/'scripts').mkdir()
   for name in ['news.json','archive.json']:shutil.copy('public/data/'+name,root/'public/data'/name)
   for name in ['reviewed.json','x-sources.json']:shutil.copy('scripts/'+name,root/'scripts'/name)
   before=json.loads((root/'public/data/archive.json').read_text())
   with patch.object(m,'ROOT',root),patch.object(m,'TARGET',root/'public/data/news.json'),patch.object(m,'ARCHIVE',root/'public/data/archive.json'),patch('urllib.request.urlopen',side_effect=TimeoutError),patch.dict('os.environ',{'EDITOR_MODE':'reviewed-only','RSSHUB_BASE_URL':''}),contextlib.redirect_stdout(io.StringIO()):m.main()
   after=json.loads((root/'public/data/archive.json').read_text());health=json.loads((root/'public/data/health.json').read_text())
   self.assertEqual([n['path'] for n in before['items']],[n['path'] for n in after['items']]);self.assertEqual(health['sourcesConnected'],0);self.assertEqual(health['editorAttempts'],0)
 def test_unreviewed_model_output_not_readopted(self):
  # The production archive accepts reviewed texts only, even if a model labelled its own work valid.
  source=pathlib.Path('scripts/fetch-news.py').read_text()
  self.assertIn("n.get('translationStatus')=='reviewed-sv'",source)
  self.assertIn("held[n['id']]='draft_requires_review'",source)
