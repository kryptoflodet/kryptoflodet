import importlib.util, unittest
spec=importlib.util.spec_from_file_location('news','scripts/fetch-news.py'); news=importlib.util.module_from_spec(spec);spec.loader.exec_module(news)
class FeedTests(unittest.TestCase):
 def test_feed_rejects_invalid_links_dates_and_future(self):
  xml='''<rss><channel><item><title>Bitcoin &amp; Ethereum update</title><link>https://example.com/a</link><pubDate>Sun, 11 Oct 2026 12:00:00 GMT</pubDate></item><item><title>Unsafe</title><link>javascript:alert(1)</link><pubDate>Sun, 11 Oct 2026 12:00:00 GMT</pubDate></item><item><title>Future</title><link>https://example.com/future</link><pubDate>Sun, 11 Oct 2030 12:00:00 GMT</pubDate></item></channel></rss>'''
  items=news.parse_feed(xml,{'id':'test','name':'Test','type':'OFFICIELL'},'2026-10-11T14:00:00Z')
  self.assertEqual(len(items),1);self.assertEqual(items[0]['coins'],['BTC','ETH']);self.assertEqual(items[0]['status'],'unconfirmed');self.assertFalse(items[0]['demo']);self.assertFalse(items[0]['evidence'][0]['verified'])
 def test_atom_and_html(self):
  xml='''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Sui update</title><link href="https://example.com/sui"/><published>2026-10-10T12:00:00Z</published></entry></feed>'''
  self.assertEqual(news.parse_feed(xml,{'id':'sui','name':'Sui','type':'OFFICIELL'},'2026-10-11T14:00:00Z')[0]['coins'],['SUI'])
  self.assertEqual(news.clean('&lt;b&gt;hello&lt;/b&gt;'),'hello')
 def test_broken_feed_fails(self):
  with self.assertRaises(Exception):news.parse_feed('<html/>',{},'2026-10-11T14:00:00Z')
if __name__=='__main__':unittest.main()

class PublicationTests(unittest.TestCase):
 def test_only_swedish_publication_and_ui(self):
  import json,pathlib
  data=json.loads(pathlib.Path('public/data/news.json').read_text())
  self.assertGreater(len(data['items']),0)
  for item in data['items']:
   self.assertIn(item.get('translationStatus'),['machine-sv','original-sv'])
   self.assertFalse(item['demo'])
  app=pathlib.Path('src/App.tsx').read_text()
  self.assertNotIn('>AI-ILLUSTRATION<',app)
  self.assertNotIn('{modal.originalText}',app)
  self.assertNotIn('Rubriker på originalspråket',app)
 def test_schedule_kept(self):
  import pathlib
  self.assertIn("3-58/5 * * * *",pathlib.Path('.github/workflows/news-pages.yml').read_text())
