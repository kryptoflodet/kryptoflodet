import unittest,sys,tempfile,pathlib
sys.path.insert(0,'scripts')
from unittest.mock import patch
from x_translate import translate_posts,ENGINE,normalize_translation,amounts,valid_translation,input_text,cache_key,ordered_candidates,load_history
from importlib.machinery import SourceFileLoader
fx=SourceFileLoader('fetch_x_translation_tests','scripts/fetch-x.py').load_module()

class TranslationTests(unittest.TestCase):
 def test_automatic_model_output_is_published_and_cached_without_review(self):
  import json
  from types import SimpleNamespace
  p={'id':'2109000000000000000','handle':'example','url':'https://x.com/example/status/2109000000000000000','text':'Bitcoin could rise.','originalLanguage':'en','publishedAt':'2026-10-13T00:00:00Z'};memo={'items':{}}
  result=SimpleNamespace(stdout=json.dumps([{'id':p['id'],'text':'Bitcoin skulle kunna stiga.','checked':True}]))
  with patch('x_translate.subprocess.run',return_value=result) as run:
   counts=translate_posts([p],memo);self.assertEqual(counts['local'],1);self.assertEqual(counts['pending'],0);self.assertEqual(p['swedish']['engine'],ENGINE)
  p.pop('swedish')
  with patch('x_translate.subprocess.run') as run:
   counts=translate_posts([p],memo);self.assertEqual(counts['cached'],1);run.assert_not_called()
 def test_unchecked_or_failed_model_output_is_not_published_and_retries(self):
  p={'id':'2109000000000000000','handle':'example','url':'https://x.com/example/status/2109000000000000000','text':'Bitcoin could rise.','originalLanguage':'en','publishedAt':'2026-10-13T00:00:00Z'};memo={'items':{}}
  from types import SimpleNamespace
  import json
  result=SimpleNamespace(stdout=json.dumps([{'id':p['id'],'text':'Bitcoin skulle kunna stiga.','checked':False}]))
  with patch('x_translate.subprocess.run',return_value=result):
   counts=translate_posts([p],memo);self.assertEqual(counts['pending'],1);self.assertNotIn('swedish',p)
  with patch('x_translate.subprocess.run',side_effect=RuntimeError):
   counts=translate_posts([p],memo);self.assertEqual(counts['pending'],1);self.assertNotIn('swedish',p);self.assertNotIn('rejectedUntil',str(memo))
 def test_financial_terms_and_numeric_format_are_normalized(self):
  self.assertEqual(normalize_translation('Bitcoin rises to $82,000.', 'Bitcoin stiger till $82,000.'),'Bitcoin stiger till $82 000.')
  self.assertEqual(normalize_translation('Bitcoin is bullish.', 'Bitcoin är bullish.'),'Bitcoin är positiv till marknaden.')
 def test_old_profile_ids_cannot_block_recent_discovery(self):
  import datetime as dt
  now=dt.datetime.now(dt.timezone.utc);pid=str((int(now.timestamp()*1000)-1288834974657)<<22)
  self.assertEqual(fx.recent_post_links([['saylor','1234567890123456789'],['saylor',pid]],now),[['saylor',pid]])
 def test_trading_slang_and_english_remnants_are_rejected(self):
  self.assertFalse(valid_translation('Why are the bears waiting?','Varför väntar björnarna?'))
  self.assertFalse(valid_translation('Ethereum leads tokenized ETF market cap.','Ethereum leder tokenized ETF marknadskapital.'))
  self.assertTrue(valid_translation('Peter Schiff says sell Bitcoin.','Peter Schiff uppmanar till att sälja Bitcoin.'))
 def test_full_note_tweet_is_used_instead_of_clipped_excerpt(self):
  import datetime as dt
  now=dt.datetime.now(dt.timezone.utc)
  account={'handle':'example','userId':'123','id':'example','name':'Example'}
  tweet={'id_str':'2109000000000000000','created_at':now.isoformat(),'user':{'id_str':'123','screen_name':'example','name':'Example'},'text':'Bitcoin could rise.','truncated':True,'note_tweet':{'note_tweet_results':{'result':{'text':'Bitcoin could rise, but this is not confirmed.'}}},'lang':'en'}
  result=fx.parse_post(tweet,account,now)
  self.assertEqual(result['text'],'Bitcoin could rise, but this is not confirmed.')
  self.assertFalse(result['sourceTruncated'])
 def test_asset_quantity_cannot_turn_into_money(self):
  source=input_text('The government could keep 61,000 seized $BTC worth over $5 billion.')
  self.assertNotIn('$BTC',source)
  self.assertTrue(valid_translation(source,'Regeringen kan behålla 61 000 beslagtagna BTC värda över 5 miljarder dollar.'))
  self.assertFalse(valid_translation(source,'Regeringen kan behålla 61 000 dollar värda över 5 miljarder dollar.'))
  self.assertFalse(valid_translation(source,'Regeringen kan behålla 61 000 beslagtagna BTC-dollar värda över 5 miljarder dollar.'))
 def test_fiat_currency_cannot_be_relabelled_as_bitcoin(self):
  self.assertFalse(valid_translation('Bitcoin is worth $82,000.','Bitcoin är värt 82 000 BTC.'))
  self.assertTrue(valid_translation('Bitcoin is worth $82,000.','Bitcoin är värt 82 000 dollar.'))
 def test_court_name_cannot_become_a_different_institution(self):
  self.assertFalse(valid_translation('The High Court has ruled on Bitcoin.','Högsta domstolen har beslutat om Bitcoin.'))
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
