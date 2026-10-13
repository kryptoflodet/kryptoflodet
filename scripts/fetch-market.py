"""Refresh a free CoinGecko snapshot for the fifty largest ranked coins."""
from __future__ import annotations

import json
import pathlib
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'public/data/market.json'
BASE_URL = 'https://api.coingecko.com/api/v3/coins/markets'
TOP_COUNT = 50
MIN_COUNT = 45


def market_url(currency: str, ids: list[str] | None = None) -> str:
    params = {'vs_currency': currency, 'order': 'market_cap_desc', 'per_page': str(TOP_COUNT), 'page': '1', 'sparkline': 'false', 'price_change_percentage': '24h'}
    if ids:
        params['ids'] = ','.join(ids)
    return BASE_URL + '?' + urllib.parse.urlencode(params)


def fetch_rows(url: str) -> list[dict[str, Any]]:
    request = urllib.request.Request(url, headers={'User-Agent': 'Kryptokollen/1.0 (+https://kryptokollen.online)', 'Accept': 'application/json'})
    with urllib.request.urlopen(request, timeout=24) as response:
        if response.status != 200:
            raise RuntimeError(f'CoinGecko svarade med HTTP {response.status}')
        data = json.loads(response.read().decode('utf-8'))
    if not isinstance(data, list) or len(data) < MIN_COUNT:
        count = len(data) if isinstance(data, list) else 0
        raise ValueError(f'CoinGecko returnerade bara {count} av de {TOP_COUNT} största valutorna')
    rows = [row for row in data if isinstance(row, dict) and isinstance(row.get('id'), str) and isinstance(row.get('current_price'), (int, float))]
    if len(rows) < MIN_COUNT:
        raise ValueError(f'För få användbara kursrader: {len(rows)}')
    return rows[:TOP_COUNT]


def old_sek_rows(previous: Any, ids: list[str]) -> list[dict[str, Any]]:
    if not isinstance(previous, dict):
        return []
    old_rows = previous.get('sekCoins')
    old_by_id = {row.get('id'): row for row in old_rows if isinstance(row, dict)} if isinstance(old_rows, list) else {}
    if old_by_id:
        return [old_by_id[coin_id] for coin_id in ids if coin_id in old_by_id]
    result = []
    for coin_id in ids:
        old = previous.get(coin_id)
        if not isinstance(old, dict) or not isinstance(old.get('sek'), (int, float)):
            continue
        stamp = old.get('last_updated_at')
        try:
            updated = datetime.fromtimestamp(stamp, timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z') if isinstance(stamp, (int, float)) and stamp > 0 else None
        except (OverflowError, OSError, ValueError):
            updated = None
        result.append({'id': coin_id, 'current_price': old['sek'], 'price_change_percentage_24h': old.get('sek_24h_change'), 'last_updated': updated})
    return result


def main() -> None:
    try:
        usd_rows = fetch_rows(market_url('usd'))
        ids = [row['id'] for row in usd_rows]
        try:
            sek_rows = fetch_rows(market_url('sek', ids))
        except Exception as exc:
            try:
                previous = json.loads(OUTPUT.read_text(encoding='utf-8'))
            except Exception:
                previous = {}
            sek_rows = old_sek_rows(previous, ids)
            print(f'SEK-kurserna kunde inte uppdateras; behåller {len(sek_rows)} tidigare valutakurser: {exc}')
        snapshot = {'schemaVersion': 2, 'generatedAt': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'), 'coins': usd_rows, 'sekCoins': sek_rows}
        OUTPUT.write_text(json.dumps(snapshot, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
        print(f'CoinGecko marknadsdata uppdaterades: {len(usd_rows)} mynt i USD och {len(sek_rows)} i SEK')
    except Exception as exc:
        print(f'Marknadsdatan kunde inte uppdateras; den senast fungerande snapshoten behålls: {exc}')


if __name__ == '__main__':
    main()
