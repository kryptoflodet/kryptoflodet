import sys,unittest
sys.path.insert(0,'scripts')
from x_archive import archive_posts,readable_post
from x_language import source_hash

class XArchiveTranslationTests(unittest.TestCase):
 def post(self,engine='reviewed'):
  text='The Bitcoin market is moving.'
  return {'id':'2109000000000000000','handle':'example','author':'Example','url':'https://x.com/example/status/2109000000000000000','publishedAt':'2026-10-13T10:00:00Z','text':text,'coins':['BTC'],'categories':['Bitcoin'],'kind':'original-x-post','originalLanguage':'en','swedish':{'text':'Bitcoinmarknaden rör sig.','method':'translation','engine':engine,'sourceHash':source_hash(text)}}
 def test_only_reviewed_or_exact_rule_translations_are_readable(self):
  self.assertTrue(readable_post(self.post('reviewed')))
  self.assertTrue(readable_post(self.post('x-sv-rules-v1')))
  self.assertFalse(readable_post(self.post('nllb-200-600m-q8-v2')))
  self.assertFalse(readable_post(self.post('mymemory-free-v1')))
  self.assertFalse(readable_post(self.post('nllb-200-600m-q8-v3')))
  self.assertFalse(readable_post(self.post('mymemory-free-v2')))
 def test_matching_checked_translation_survives_an_outage(self):
  import copy
  prior=self.post()
  prior['swedish'].update(engine='qwen3-4b-sv-checked-v1',qualityVersion='x-swedish-v4')
  incoming=copy.deepcopy(prior);incoming.pop('swedish')
  rows=archive_posts([prior],[incoming],'2026-10-14T00:00:00Z')
  self.assertEqual(rows[0]['swedish']['text'],prior['swedish']['text'])
  incoming['text']='Bitcoin could fall.'
  rows=archive_posts([prior],[incoming],'2026-10-14T00:00:00Z')
  self.assertNotIn('swedish',rows[0])
 def test_old_machine_translation_is_removed_but_original_is_preserved(self):
  item=self.post('nllb-200-600m-q8-v2')
  result=archive_posts([item],[], '2026-10-13T12:00:00Z')
  self.assertEqual(len(result),1)
  self.assertEqual(result[0]['text'],item['text'])
  self.assertNotIn('swedish',result[0])
 def test_new_machine_translation_is_not_archived_as_swedish(self):
  item=self.post('mymemory-free-v1')
  result=archive_posts([], [item], '2026-10-13T12:00:00Z')
  self.assertNotIn('swedish',result[0])

if __name__=='__main__':unittest.main()
