"""Refresh free, public market indicators while preserving the last good snapshot."""
from __future__ import annotations

import json
import os
import pathlib
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'public/data/market-context.json'
CACHE = ROOT / '.cache/market-context/context.json'
PUBLIC_STATE_URL = os.environ.get('MARKET_CONTEXT_STATE_URL', 'https://kryptopuls.se/data/market-context.json')
FNG_URL = 'https://api.alternative.me/fng/?limit=1&format=json'
GLOBAL_URL = 'https://api.coingecko.com/api/v3/global'
ALT_URL = 'https://pro-api.coinmarketcap.com/public-api/v1/altcoin-season-index/latest'
BLOCKCHAIN_CENTER_URL = 'https://www.blockchaincenter.net/altcoin-season-index/'
FRESH_FOR = {'fearGreed': 6 * 60 * 60, 'market': 60 * 60, 'altcoinSeason': 60 * 60}


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def iso_from_unix(value: Any) -> str | None:
    try:
        stamp = float(value)
        if stamp > 1e12:
            stamp /= 1000
        return datetime.fromtimestamp(stamp, timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def iso_value(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    except ValueError:
        return None


def as_number(value: Any, minimum: float, maximum: float) -> float | None:
    try:
        number = float(value)
        return number if minimum <= number <= maximum else None
    except (TypeError, ValueError, OverflowError):
        return None


def empty_snapshot() -> dict[str, Any]:
    return {
        'schemaVersion': 1,
        'generatedAt': None,
        'fearGreed': {'value': None, 'classification': None, 'checkedAt': None, 'observedAt': None},
        'market': {'btcDominance': None, 'ethDominance': None, 'marketCapChange24h': None,
                   'btcChange24h': None, 'ethChange24h': None, 'totalMarketCapUsd': None, 'volume24hUsd': None, 'checkedAt': None, 'observedAt': None},
        'altcoinSeason': {'value': None, 'source': 'CoinMarketCap', 'checkedAt': None, 'observedAt': None},
    }


def normalize_snapshot(raw: Any) -> dict[str, Any]:
    base = empty_snapshot()
    if not isinstance(raw, dict) or raw.get('schemaVersion') != 1:
        return base
    base['generatedAt'] = iso_value(raw.get('generatedAt'))
    for key, fields in {
        'fearGreed': ('value', 'classification', 'checkedAt', 'observedAt'),
        'market': ('btcDominance', 'ethDominance', 'marketCapChange24h', 'btcChange24h', 'ethChange24h', 'totalMarketCapUsd', 'volume24hUsd', 'checkedAt', 'observedAt'),
        'altcoinSeason': ('value', 'source', 'checkedAt', 'observedAt'),
    }.items():
        value = raw.get(key)
        if not isinstance(value, dict):
            continue
        for field in fields:
            if field in ('checkedAt', 'observedAt'):
                base[key][field] = iso_value(value.get(field))
            elif field in ('classification', 'source'):
                base[key][field] = value.get(field).strip() if isinstance(value.get(field), str) and value.get(field).strip() else base[key][field]
            elif field == 'value' and key == 'fearGreed':
                base[key][field] = as_number(value.get(field), 0, 100)
            elif field == 'value' and key == 'altcoinSeason':
                base[key][field] = as_number(value.get(field), 0, 100)
            elif field in ('totalMarketCapUsd', 'volume24hUsd'):
                base[key][field] = as_number(value.get(field), 0, 1e18)
            elif field in ('btcDominance', 'ethDominance'):
                base[key][field] = as_number(value.get(field), 0, 100)
            else:
                base[key][field] = as_number(value.get(field), -1000, 1000)
    return base


def parse_fear_greed(payload: Any) -> tuple[int, str, str]:
    entries = payload.get('data') if isinstance(payload, dict) else None
    if not isinstance(entries, list) or not entries or not isinstance(entries[0], dict):
        raise ValueError('Fear & Greed saknar datapost')
    row = entries[0]
    value = as_number(row.get('value'), 0, 100)
    classification = row.get('value_classification')
    observed = iso_from_unix(row.get('timestamp'))
    if value is None or not isinstance(classification, str) or not observed:
        raise ValueError('Fear & Greed innehåller ogiltiga fält')
    return round(value), classification, observed


def parse_global_market(payload: Any, market_data: Any) -> dict[str, Any]:
    data = payload.get('data') if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise ValueError('CoinGecko Global saknar data')
    percentages = data.get('market_cap_percentage')
    if not isinstance(percentages, dict):
        raise ValueError('CoinGecko Global saknar marknadsdominans')
    observed = iso_from_unix(data.get('updated_at')) or iso_now()
    quotes = market_data if isinstance(market_data, dict) else {}
    rows = quotes.get('coins') if isinstance(quotes.get('coins'), list) else quotes.get('quotes') if isinstance(quotes.get('quotes'), list) else None
    by_id = {row.get('id'): row for row in rows if isinstance(row, dict) and isinstance(row.get('id'), str)} if isinstance(rows, list) else {}
    btc = quotes.get('bitcoin') if isinstance(quotes.get('bitcoin'), dict) else by_id.get('bitcoin', {})
    eth = quotes.get('ethereum') if isinstance(quotes.get('ethereum'), dict) else by_id.get('ethereum', {})
    result = {
        'totalMarketCapUsd': as_number((data.get('total_market_cap') or {}).get('usd'), 0, 1e18),
        'volume24hUsd': as_number((data.get('total_volume') or {}).get('usd'), 0, 1e18),
        'btcDominance': as_number(percentages.get('btc'), 0, 100),
        'ethDominance': as_number(percentages.get('eth'), 0, 100),
        'marketCapChange24h': as_number(data.get('market_cap_change_percentage_24h_usd'), -1000, 1000),
        'btcChange24h': as_number(btc.get('usd_24h_change', btc.get('price_change_percentage_24h', btc.get('change24h'))), -1000, 1000),
        'ethChange24h': as_number(eth.get('usd_24h_change', eth.get('price_change_percentage_24h', eth.get('change24h'))), -1000, 1000),
        'observedAt': observed,
    }
    if result['btcDominance'] is None or result['ethDominance'] is None or result['marketCapChange24h'] is None:
        raise ValueError('CoinGecko Global innehåller ofullständiga marknadsdata')
    return result


def parse_altcoin_season(payload: Any) -> tuple[int, str]:
    if not isinstance(payload, dict):
        raise ValueError('CoinMarketCap svarade inte med ett objekt')
    status = payload.get('status')
    if isinstance(status, dict) and str(status.get('error_code', '0')) != '0':
        raise ValueError(f"CoinMarketCap API-fel {status.get('error_code')}: {status.get('error_message', 'okänt fel')}")
    data = payload.get('data')
    if isinstance(data, list):
        data = data[0] if data else None
    if not isinstance(data, dict):
        raise ValueError('CoinMarketCap Altcoin Season saknar data')
    value = as_number(data.get('altcoin_index'), 0, 100)
    observed = iso_value(data.get('snapshot_time')) or (iso_value(status.get('timestamp')) if isinstance(status, dict) else None) or iso_now()
    if value is None:
        raise ValueError('CoinMarketCap Altcoin Season saknar ett index mellan 0 och 100')
    return round(value), observed


def parse_blockchaincenter_html(payload: Any) -> tuple[int, str]:
    if not isinstance(payload, str):
        raise ValueError('BlockchainCenter svarade inte med HTML-text')
    match = re.search(r'Altcoin Season Snapshot:\s*(\d{1,3})(?:\.\d+)?%', payload, re.IGNORECASE)
    if not match:
        raise ValueError('BlockchainCenter-sidan saknar indexvärde')
    value = as_number(match.group(1), 0, 100)
    if value is None:
        raise ValueError('BlockchainCenter-indexet är utanför 0–100')
    day = re.search(r'altcoin-season-snapshot/\?d=(\d{4}-\d{2}-\d{2})', payload, re.IGNORECASE)
    observed = iso_value(day.group(1) + 'T00:00:00Z') if day else iso_now()
    return round(value), observed


def should_refresh(metric: dict[str, Any], ttl_seconds: int, now: float | None = None) -> bool:
    checked = iso_value(metric.get('checkedAt'))
    if not checked:
        return True
    try:
        checked_epoch = datetime.fromisoformat(checked.replace('Z', '+00:00')).timestamp()
        return (now if now is not None else time.time()) - checked_epoch >= ttl_seconds
    except (ValueError, OverflowError):
        return True


def fetch_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={'User-Agent': 'Kryptopuls/1.0 (+https://kryptopuls.se)', 'Accept': 'application/json'})
    with urllib.request.urlopen(request, timeout=18) as response:
        if response.status != 200:
            raise RuntimeError(f'HTTP {response.status}')
        return json.loads(response.read().decode('utf-8'))


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={'User-Agent': 'Kryptopuls/1.0 (+https://kryptopuls.se)', 'Accept': 'text/html,application/xhtml+xml'})
    with urllib.request.urlopen(request, timeout=18) as response:
        if response.status != 200:
            raise RuntimeError(f'HTTP {response.status}')
        return response.read(2_000_000).decode('utf-8', errors='replace')


def load_published_snapshot() -> dict[str, Any]:
    if not PUBLIC_STATE_URL:
        return empty_snapshot()
    try:
        url = PUBLIC_STATE_URL + ('&' if '?' in PUBLIC_STATE_URL else '?') + 't=' + str(int(time.time()))
        return normalize_snapshot(fetch_json(url))
    except Exception as exc:  # The published fallback may not exist on a first deployment.
        print(f'Föregående publicerade marknadsdata kunde inte läsas: {exc}')
        return empty_snapshot()


def update_from_sources(snapshot: dict[str, Any], market_data: Any, now: float | None = None, fetcher=fetch_json, text_fetcher=fetch_text) -> dict[str, Any]:
    checked_now = iso_now()
    if should_refresh(snapshot['fearGreed'], FRESH_FOR['fearGreed'], now):
        try:
            value, classification, observed = parse_fear_greed(fetcher(FNG_URL))
            snapshot['fearGreed'].update(value=value, classification=classification, observedAt=observed, checkedAt=checked_now)
            print(f"Fear & Greed hämtat: {value}/100 ({classification}), observation {observed}")
        except Exception as exc:
            print(f"Fear & Greed misslyckades; sparat värde behålls: {exc}")
    if should_refresh(snapshot['market'], FRESH_FOR['market'], now):
        try:
            market = parse_global_market(fetcher(GLOBAL_URL), market_data)
            snapshot['market'].update({key: value for key, value in market.items() if value is not None}, checkedAt=checked_now)
            print('CoinGecko global marknad uppdaterad: BTC-dominans', market['btcDominance'], 'ETH-dominans', market['ethDominance'], 'marknad 24h', market['marketCapChange24h'])
        except Exception as exc:
            print(f"CoinGecko Global misslyckades; sparat värde behålls: {exc}")
    if should_refresh(snapshot['altcoinSeason'], FRESH_FOR['altcoinSeason'], now):
        try:
            value, observed = parse_altcoin_season(fetcher(ALT_URL))
            snapshot['altcoinSeason'].update(value=value, source='CoinMarketCap', observedAt=observed, checkedAt=checked_now)
            print(f'CoinMarketCap Altcoin Season Index hämtat: {value}/100, observation {observed}')
        except Exception as exc:
            print(f"CoinMarketCap Altcoin Season-index misslyckades; testar BlockchainCenter: {exc}")
            try:
                value, observed = parse_blockchaincenter_html(text_fetcher(BLOCKCHAIN_CENTER_URL))
                snapshot['altcoinSeason'].update(value=value, source='BlockchainCenter', observedAt=observed, checkedAt=checked_now)
                print(f'BlockchainCenter Altcoin Season Index hämtat: {value}/100, observation {observed}')
            except Exception as fallback_exc:
                print(f"BlockchainCenter Altcoin Season-index misslyckades; senast sparat värde behålls: {fallback_exc}")
    snapshot['generatedAt'] = checked_now
    return snapshot


def main() -> None:
    local = normalize_snapshot(json.loads(OUTPUT.read_text(encoding='utf-8'))) if OUTPUT.exists() else empty_snapshot()
    published = load_published_snapshot()
    try:
        cached = normalize_snapshot(json.loads(CACHE.read_text(encoding='utf-8')))
    except Exception:
        cached = empty_snapshot()
    # Keep whichever valid snapshot is freshest so provider outages cannot erase known-good values.
    snapshot = empty_snapshot()
    for key in ('fearGreed', 'market', 'altcoinSeason'):
        candidates = [local.get(key, {}), published.get(key, {}), cached.get(key, {})]
        snapshot[key] = max(candidates, key=lambda item: item.get('checkedAt') or '')
    market_path = ROOT / 'public/data/market.json'
    try:
        market_data = json.loads(market_path.read_text(encoding='utf-8'))
    except Exception as exc:
        print(f'BTC/ETH-rörelser kunde inte läsas ur kursögonblicksbilden: {exc}')
        market_data = {}
    snapshot = update_from_sources(snapshot, market_data)
    OUTPUT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    nonempty = sum(value is not None for key in ('fearGreed', 'market', 'altcoinSeason') for field, value in snapshot[key].items() if field not in ('checkedAt', 'observedAt', 'classification', 'source'))
    print(f'Marknadskontext sparad ({nonempty} mätvärden; fil: {OUTPUT.relative_to(ROOT)}).')


if __name__ == '__main__':
    main()
