import runpy
import unittest
import contextlib
import io
from datetime import datetime, timezone

M = runpy.run_path('scripts/fetch-market-context.py')


class MarketContextTests(unittest.TestCase):
    def test_fear_and_greed_parsing(self):
        value, label, observed = M['parse_fear_greed']({'data': [{'value': '63', 'value_classification': 'Greed', 'timestamp': '1791900000'}]})
        self.assertEqual(value, 63)
        self.assertEqual(label, 'Greed')
        self.assertTrue(observed.endswith('Z'))

    def test_global_metrics_and_bitcoin_ethereum_changes(self):
        parsed = M['parse_global_market'](
            {'data': {'market_cap_percentage': {'btc': 59.2, 'eth': 10.8}, 'market_cap_change_percentage_24h_usd': -1.25, 'updated_at': 1791900000}},
            {'bitcoin': {'usd_24h_change': 2.4}, 'ethereum': {'usd_24h_change': 1.2}},
        )
        self.assertEqual(parsed['btcDominance'], 59.2)
        self.assertEqual(parsed['ethDominance'], 10.8)
        self.assertEqual(parsed['btcChange24h'], 2.4)
        self.assertEqual(parsed['ethChange24h'], 1.2)

    def test_keyless_cmc_envelope_and_index_bounds(self):
        value, observed = M['parse_altcoin_season']({'data': {'altcoin_index': 77, 'snapshot_time': '2026-10-13T12:00:00Z'}, 'status': {'error_code': '0'}})
        self.assertEqual(value, 77)
        self.assertEqual(observed, '2026-10-13T12:00:00Z')
        with self.assertRaises(ValueError):
            M['parse_altcoin_season']({'data': {'altcoin_index': 101}, 'status': {'error_code': 0}})
        with self.assertRaises(ValueError):
            M['parse_altcoin_season']({'data': {'altcoin_index': 50}, 'status': {'error_code': '429'}})

    def test_refresh_windows_use_checked_time_and_preserve_old_snapshot(self):
        now = datetime(2026, 10, 13, 15, 0, tzinfo=timezone.utc).timestamp()
        recent = {'checkedAt': '2026-10-13T14:30:00Z'}
        old = {'checkedAt': '2026-10-13T13:00:00Z'}
        self.assertFalse(M['should_refresh'](recent, 3600, now))
        self.assertTrue(M['should_refresh'](old, 3600, now))
        snap = M['normalize_snapshot']({'schemaVersion': 1, 'fearGreed': {'value': 58, 'checkedAt': '2026-10-13T14:00:00Z'}})
        self.assertEqual(snap['fearGreed']['value'], 58)
        self.assertEqual(snap['market']['btcDominance'], None)

    def test_provider_outage_keeps_last_good_values(self):
        snap = M['normalize_snapshot']({
            'schemaVersion': 1,
            'fearGreed': {'value': 62, 'classification': 'Greed', 'checkedAt': '2020-01-01T00:00:00Z', 'observedAt': '2020-01-01T00:00:00Z'},
            'market': {'btcDominance': 58.1, 'ethDominance': 11.2, 'marketCapChange24h': 1.4, 'btcChange24h': 2.2, 'ethChange24h': 1.1, 'checkedAt': '2020-01-01T00:00:00Z'},
            'altcoinSeason': {'value': 44, 'source': 'CoinMarketCap', 'checkedAt': '2020-01-01T00:00:00Z'},
        })
        with contextlib.redirect_stdout(io.StringIO()):
            updated = M['update_from_sources'](snap, {}, now=datetime(2026, 10, 13, 15, 0, tzinfo=timezone.utc).timestamp(), fetcher=lambda _: (_ for _ in ()).throw(TimeoutError('offline')))
        self.assertEqual(updated['fearGreed']['value'], 62)
        self.assertEqual(updated['market']['btcDominance'], 58.1)
        self.assertEqual(updated['altcoinSeason']['value'], 44)


if __name__ == '__main__':
    unittest.main()
