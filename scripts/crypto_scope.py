"""Conservative headline-only gate: indirect macro/energy relevance is insufficient."""
import re
DIRECT=re.compile(r'\b(bitcoin|btc|ethereum|ether|eth|solana|sui|hedera|hbar|ondo|xrp|ripple|cardano|ada|dogecoin|doge|stellar|xlm|avalanche|avax|chainlink|bnb|hyperliquid|litecoin|ltc|zcash|monero|usdt|usdc|tether|binance|coinbase|kraken|metamask|uniswap|aave|defi|nfts?|web3|blockchain|blockkedj\w*|krypto\w*|crypto(?:currency|currencies|assets?)?|stablecoins?|tokeni[sz]\w*|memecoins?|altcoins?|testnet|mainnet|staking|on.chain)\b',re.I)
ENERGY=re.compile(r'\b(oil|gas|energy|electricity|power prices|energi\w*|olja|elpris\w*|elnät\w*)\b',re.I)
MINING=re.compile(r'\b(bitcoin|crypto\w*|btc|krypto\w*)\s+(mining|miners|brytning|gruvdrift)|\b(mining|miners|bitcoinbrytning|kryptobrytning)\b',re.I)
MACRO_START=re.compile(r'^(fed\b|federal reserve|inflation\b|interest rates?\b|oil\b|gas\b|energy\b|riksbank\w*|ränt\w*\b|jobs report|employment\b|tariffs?\b)',re.I)
def crypto_only(title):
 title=re.split(r'\s[-–|]\s(?=[^-–|]*$)',title)[0]
 if not DIRECT.search(title):return False
 if ENERGY.search(title) and not MINING.search(title):return False
 if MACRO_START.search(title):return False
 return True
