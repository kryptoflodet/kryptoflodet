"""Fast fail-closed checks for obvious English leftovers and known bad crypto terms."""
import re

_BAD_SWEDISH_PATTERNS=tuple(re.compile(pattern,re.I) for pattern in (
 r'\bAustralia\b',
 r'\b(?:lövförlopp|kryptodrivsprodukter|defraudning|krypto-portfolio|bitkoin|bitcoinkaffe|steak and ägg)\b',
 r'\b(?:alltid hög(?:re|sta) nivå|får ny liv|snabbast växt|stabila valutaens|kryptoexchanger|bankstängningar)\b',
 r'\b(?:global watchdog|parent företaget|bitcoin-til|Treasury-secretary|utvidgad målning|slarvigt sammanslagit fixer)\b',
 r'\b(?:kustod|sejka|threatar|walleter|loophole|bullish|bearish|watchdog|defraud\w*|cash out)\b',
 r'\b(?:en förslag|detta skatt|detta veckor|vilket aktie|UK-dom)\b',
 r'\b(?:fixer|blockchain)\b',
 r'\bBitcoin:s\b',
 r'\b(?:kvantförsvar|QSB-utgifter|människans utrymme|Bitcoin-ai-konvergens|öppen källkod AI)\b',
))

def is_swedish_quality(*parts):
 """Reject known mistranslations; unknown language stays in the review queue."""
 text=' '.join(part for part in parts if isinstance(part,str))
 return bool(text.strip()) and not any(pattern.search(text) for pattern in _BAD_SWEDISH_PATTERNS)
