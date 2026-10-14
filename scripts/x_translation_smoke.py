"""Once-per-version regression check against the real local model, never fake feed data."""
import hashlib,json,pathlib,re,time
from x_proofread import Translator,ENGINE,CHECK_VERSION,MODEL_HASH,SYSTEM,EDIT,REVIEW
ROOT=pathlib.Path(__file__).resolve().parents[1]
STAMP=ROOT/'.cache/x-translation/smoke-v1.json'
FIXTURES=[
 'Ethereum holds the top spot in tokenized ETF market cap at $303M. BNB Chain follows at $192.1M and Solana at $91.5M. Together the three chains account for roughly 85% of the $686.5M total. Source: Token Terminal',
 'Peter Schiff is still telling people to "sell Bitcoin and buy gold". Maybe the real question is why the bears are still waiting.',
 'If Bitcoin reaches $200,000 this cycle, I will buy a Bugatti. I think it is possible.',
 'ORANJEBTC\'s CEO says Brazil is "quite advanced" in adopting Bitcoin. Everyone wants in!',
 'Bitcoin could rise if US inflation falls, but this is not confirmed.',
 'A whale moved 1,250 ETH worth $3.4 million to Kraken. The transfer does not prove a sale.',
 'Bitfinex whales are opening longs on BTC and ETH during this market correction. Smart money is going long!',
 '$40B Wellington-Altus says Bitcoin will vastly benefit as the global economy moves on-chain.',
]
EXPECTED=[
 [r'tokeniser',r'(?:marknadsvärd|värde)',r'(?:börshandlad|ETF)'],
 [r'sälj',r'köp',r'guld',r'vänt'],
 [r'om',r'Bugatti',r'möjligt'],
 [r'(?:\bvd\b|verkställande direktör)',r'Brasilien',r'(?:delta|med|delaktig)'],
 [r'(?:kan|skulle)',r'inflation',r'inte'],
 [r'(?:storägare|investerare)',r'Kraken',r'inte',r'försäljning'],
 [r'Bitfinex',r'(?:position|satsar|invester)',r'(?:uppgång|stiger|ökar)'],
 [r'Wellington-Altus',r'(?:gynnas|dra nytta)',r'blockkedj'],
]
def main():
 version=ENGINE+':'+CHECK_VERSION+':'+MODEL_HASH+':'+hashlib.sha256((ROOT/'scripts/x_proofread.py').read_bytes()+(ROOT/'scripts/x_translate.py').read_bytes()+json.dumps([FIXTURES,EXPECTED]).encode()).hexdigest()
 if STAMP.exists() and json.loads(STAMP.read_text()).get('version')==version:
  print('Local Swedish regression already passed for this pinned version.');return
 translator=Translator();rows=[];deadline=time.monotonic()+1500
 for source,expected in zip(FIXTURES,EXPECTED):
  text=translator.translate(source,deadline)
  if not text or any(not re.search(pattern,text,re.I) for pattern in expected):raise RuntimeError('Local Swedish regression failed: '+source+' => '+str(text))
  print('Verified Swedish:',text,flush=True);rows.append({'original':source,'translation':text})
 result={'version':version,'items':rows}
 state=ROOT/'state';state.mkdir(exist_ok=True);(state/'x-translation-smoke.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 STAMP.parent.mkdir(parents=True,exist_ok=True);STAMP.write_text(json.dumps(result,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
