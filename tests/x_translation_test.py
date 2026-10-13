import unittest,sys,tempfile,pathlib
sys.path.insert(0,'scripts')
from x_translate import amounts,valid_translation,input_text,cache_key,ordered_candidates,load_history
from importlib.machinery import SourceFileLoader
fx=SourceFileLoader('fetch_x_translation_tests','scripts/fetch-x.py').load_module()

class TranslationTests(unittest.TestCase):
 def test_bad_or_missing_cache_cannot_stop_the_feed(self):
  with tempfile.TemporaryDirectory() as temp:
   path=pathlib.Path(temp)/'cache.json';self.assertEqual(load_history(path),{'items':{}})
   path.write_text('{interrupted');self.assertEqual(load_history(path),{'items':{}})
   path.write_text('[]');self.assertEqual(load_history(path),{'items':{}})
 def test_numbers_and_scale_are_preserved(self):
  source='Bitcoin rises to $82,000. Liquidations total $814M.'
  self.assertTrue(valid_translation(source,'Bitcoin stiger till 82 000 dollar. Likvidationerna uppgår till 814 miljoner dollar.'))
  self.assertFalse(valid_translation(source,'Bitcoin stiger till 82 000 dollar. Likvidationerna uppgår till 814 miljarder dollar.'))
  self.assertFalse(valid_translation(source,'Bitcoin stiger till 83 000 dollar. Likvidationerna uppgår till 814 miljoner dollar.'))
  self.assertEqual(amounts('170K and 18.9 million'),amounts('170 tusen och 18,9 miljoner',True))
 def test_qualifiers_names_and_negation_survive(self):
  self.assertTrue(valid_translation('Bitcoin could rise, but this is not confirmed.','Bitcoin skulle kunna stiga, men detta är inte bekräftat.'))
  self.assertFalse(valid_translation('Bitcoin could rise, but this is not confirmed.','Bitcoin stiger och är nu bekräftat.'))
  self.assertFalse(valid_translation('Strategy purchased 250 BTC.','Strategin köpte 250 BTC.'))
  self.assertFalse(valid_translation('Coinbase partnered with Singapore authorities.','En börs samarbetade med myndigheterna i Singapore.'))
  self.assertFalse(valid_translation('Bitcoin rises above $80M+.','Bitcoin stiger till 80 miljoner dollar.'))
 def test_raw_english_and_model_garbage_are_rejected(self):
  for text in [None,'','Bitcoin could rise.','Cry-opti plungade 43%.','<script>unsafe</script>']:
   self.assertFalse(valid_translation('Bitcoin could rise.',text))
 def test_cache_is_bound_to_url_and_exact_original(self):
  a={'url':'https://x.com/example/status/2109000000000000000','text':'Bitcoin could rise.'}
  self.assertNotEqual(cache_key(a),cache_key({**a,'text':'Bitcoin could not rise.'}))
  self.assertNotEqual(cache_key(a),cache_key({**a,'url':a['url']+'x'}))
 def test_newest_first_with_one_place_for_each_account(self):
  posts=[{'id':str(i),'handle':h,'publishedAt':date,'originalLanguage':'en','text':'Bitcoin'} for i,h,date in [(1,'busy','2026-10-13'),(2,'busy','2026-10-12'),(3,'quiet','2026-10-01')]]
  self.assertEqual([p['id'] for p in ordered_candidates(posts)],['1','3','2'])
 def test_profile_discovery_does_not_attach_next_cards_text(self):
  payload='''<a href="/CryptoKid/status/2109000000000000001">date</a><div class="activity-descp"><p>I went on holiday.</p></div><a href="/CryptoKid/status/2109000000000000001">footer</a><a href="/CryptoKid/status/2109000000000000002">date</a><div class="activity-descp"><p>Bitcoin could rise.</p></div><a href="/impostor/status/2109000000000000003">date</a><div class="activity-descp"><p>Bitcoin rises.</p></div>'''
  self.assertEqual(fx.profile_references(payload,'CryptoKid'),['2109000000000000002'])
 def test_new_account_cannot_evict_quieter_accounts(self):
  accounts=[{'id':str(i)} for i in range(7)];posts={str(i*30+j):{'id':str(i*30+j),'sourceId':str(i),'publishedAt':f'2026-10-{i+1:02}'} for i in range(7) for j in range(30)}
  self.assertEqual(len(fx.balanced_posts(posts,accounts)),210)
  self.assertEqual({p['sourceId'] for p in fx.balanced_posts(posts,accounts)},set(str(i) for i in range(7)))

if __name__=='__main__':unittest.main()
