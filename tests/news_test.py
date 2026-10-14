import importlib.util, unittest,sys
sys.path.insert(0,'scripts')
spec=importlib.util.spec_from_file_location('news','scripts/fetch-news.py'); news=importlib.util.module_from_spec(spec);spec.loader.exec_module(news)
class FeedTests(unittest.TestCase):
 def test_feed_rejects_invalid_links_dates_and_future(self):
  xml='''<rss><channel><item><title>Bitcoin &amp; Ethereum update</title><link>https://example.com/a</link><pubDate>Sun, 11 Oct 2026 12:00:00 GMT</pubDate></item><item><title>Unsafe</title><link>javascript:alert(1)</link><pubDate>Sun, 11 Oct 2026 12:00:00 GMT</pubDate></item><item><title>Future</title><link>https://example.com/future</link><pubDate>Sun, 11 Oct 2030 12:00:00 GMT</pubDate></item><item><title>Old Bitcoin item</title><link>https://example.com/old</link><pubDate>Mon, 1 Sep 2026 12:00:00 GMT</pubDate></item></channel></rss>'''
  items=news.parse_feed(xml,{'id':'test','name':'Test','type':'OFFICIELL'},'2026-10-11T14:00:00Z')
  self.assertEqual(len(items),1);self.assertEqual(items[0]['coins'],['BTC','ETH']);self.assertEqual(items[0]['status'],'unconfirmed');self.assertFalse(items[0]['demo']);self.assertFalse(items[0]['evidence'][0]['verified'])
 def test_candidates_are_prioritized_by_recency(self):
  items=[{'id':'old','publishedAt':'2026-10-10T12:00:00Z'},{'id':'new','publishedAt':'2026-10-13T08:00:00Z'}]
  ordered=news.prioritize_candidates(items)
  self.assertEqual([item['id'] for item in ordered],['new','old'])
 def test_atom_and_html(self):
  xml='''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Sui update</title><link href="https://example.com/sui"/><published>2026-10-10T12:00:00Z</published></entry></feed>'''
  self.assertEqual(news.parse_feed(xml,{'id':'sui','name':'Sui','type':'OFFICIELL'},'2026-10-11T14:00:00Z')[0]['coins'],['SUI'])
  self.assertEqual(news.clean('&lt;b&gt;hello&lt;/b&gt;'),'hello')
 def test_broken_feed_fails(self):
  with self.assertRaises(Exception):news.parse_feed('<html/>',{},'2026-10-11T14:00:00Z')
 def test_youtube_handle_resolves_only_one_real_channel_id(self):
  class Response:
   def __init__(self,page):self.page=page
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def read(self,size):return self.page
  own='UC'+'1'*22;other='UC'+'2'*22
  cases=[f'<meta itemprop="channelId" content="{own}"><meta content="{other}">',f'<meta content="{own}" itemprop="channelId">',f'<script>{{"channelMetadataRenderer":{{"externalId":"{own}"}}}}</script>']
  for page in cases:
   url=news.youtube_feed_url('MMCryptoTube',lambda request,timeout:Response(page.encode()))
   self.assertEqual(url,'https://www.youtube.com/feeds/videos.xml?channel_id='+own)
  large_page=(f'<meta itemprop="channelId" content="{own}">'+(' '*(2_100_000))).encode()
  self.assertIn(own,news.youtube_feed_url('TheDiaryOfACEO',lambda request,timeout:Response(large_page)))
  with self.assertRaises(ValueError):news.youtube_feed_url('bad/handle',lambda *a,**k:Response(b''))
  with self.assertRaises(ValueError):news.youtube_feed_url('ambiguous',lambda *a,**k:Response(f'<meta itemprop="channelId" content="{own}"><meta itemprop="channelId" content="{other}">'.encode()))
if __name__=='__main__':unittest.main()

class PublicationTests(unittest.TestCase):
 def test_only_swedish_publication_and_ui(self):
  import json,pathlib
  data=json.loads(pathlib.Path('public/data/news.json').read_text())
  self.assertGreater(len(data['items']),0)
  for item in data['items']:
   self.assertEqual(item.get('translationStatus'),'reviewed-sv')
   self.assertFalse(item['demo'])
  app=pathlib.Path('src/App.tsx').read_text()
  self.assertNotIn('>AI-ILLUSTRATION<',app)
  self.assertNotIn('{modal.originalText}',app)
  self.assertNotIn('Rubriker på originalspråket',app)
 def test_schedule_kept(self):
  import pathlib
  self.assertIn("3-58/5 * * * *",pathlib.Path('.github/workflows/news-pages.yml').read_text())

class CryptoScopeTests(unittest.TestCase):
 def test_scope(self):
  from crypto_scope import crypto_only
  for title in ['Oil prices rise as Bitcoin miners watch','Fed cuts rates as Bitcoin investors wait','Bitcoin depends on cheap energy','Apple launches a new iPhone','Jobs report improves - CryptoSlate','CryptoRover unveils a new Ferrari']:
   self.assertFalse(crypto_only(title),title)
  for title in ['Bitcoin rises 5%','Ethereum publishes testnet update','Sui integrates USDC','Bitcoin mining difficulty reaches record','SEC approves spot Bitcoin ETF']:
   self.assertTrue(crypto_only(title),title)

class StrictPublicationTests(unittest.TestCase):
 def test_published_scope_and_review(self):
  import json,pathlib
  from crypto_scope import crypto_only
  data=json.loads(pathlib.Path('public/data/news.json').read_text())
  removed={'di','avanza','realtid','dagensps','svt','riksbank','wsj','fed'}
  reviews=json.loads(pathlib.Path('scripts/reviewed.json').read_text())
  for item in data['items']:
   self.assertNotIn(item['sourceId'],removed)
   self.assertTrue(crypto_only(item['originalTitle']),item['title'])
   if item['status']=='confirmed':
    self.assertIn(item['originalUrl'],reviews)
    self.assertTrue(item['evidence'][0]['verified'])
    self.assertTrue(item.get('verificationNote'))

class ReaderTests(unittest.TestCase):
 def test_safe_bounded_excerpt(self):
  from reader_content import feed_excerpt
  text=feed_excerpt({'description':'<script>unsafe()</script><p>Bitcoin developers published a new update for the network today.</p>'},'Bitcoin update','coindesk')
  self.assertNotIn('unsafe',text);self.assertNotIn('<',text);self.assertIn('developers',text)
  long=feed_excerpt({'description':' '.join(['word']*200)},'Bitcoin','test')
  self.assertLessEqual(len(long.split()),55)
  self.assertEqual(feed_excerpt({'description':'Bitcoin update'},'Bitcoin update','test'),'')
 def test_reader_opens_from_headline(self):
  import pathlib
  app=pathlib.Path('src/App.tsx').read_text()
  self.assertIn('onClick={onDetails} aria-haspopup="dialog"',app)
  self.assertIn('aria-label="Nyhetstext"',app)
  self.assertNotIn('dangerouslySetInnerHTML',app)

class LocalEditorValidationTests(unittest.TestCase):
 def test_local_summary_does_not_need_model_generated_evidence_quotes(self):
  from local_editor import validate,cache_key
  source='Bitcoin climbed after spot exchange-traded funds recorded net inflows on Tuesday, CoinDesk reported. Analysts said the activity was the strongest in several weeks as market volatility eased. Investors continue to watch demand and trading volumes across major digital assets.'
  draft={'title':'Bitcoin stiger efter ökad efterfrågan på börshandlade fonder','paragraphs':['CoinDesk rapporterar att bitcoin steg efter att börshandlade fonder fått nettoinflöden på tisdagen. Analytiker beskriver aktiviteten som den starkaste på flera veckor när marknadens svängningar minskade.','Investerare fortsätter enligt underlaget att följa efterfrågan och handelsvolymer för större digitala tillgångar. Texten pekar inte ut någon säker riktning för bitcoinpriset.']}
  self.assertTrue(validate(draft,source,'CoinDesk'))
  key=cache_key({'originalTitle':'Bitcoin moves','sourceText':source})
  self.assertNotEqual(key, __import__('hashlib').sha256(('v2:Bitcoin moves\\n'+source).encode()).hexdigest())
