"""Once-per-version regression check against the real local model, never fake feed data."""
import hashlib,json,pathlib,time
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
]
def main():
 version=ENGINE+':'+CHECK_VERSION+':'+MODEL_HASH+':'+hashlib.sha256((SYSTEM+EDIT+REVIEW+str(FIXTURES)).encode()).hexdigest()
 if STAMP.exists() and json.loads(STAMP.read_text()).get('version')==version:
  print('Local Swedish regression already passed for this pinned version.');return
 translator=Translator();rows=[];deadline=time.monotonic()+900
 for source in FIXTURES:
  text=translator.translate(source,deadline)
  if not text:raise RuntimeError('Local Swedish regression failed: '+source)
  print('Verified Swedish:',text,flush=True);rows.append({'original':source,'translation':text})
 result={'version':version,'items':rows}
 state=ROOT/'state';state.mkdir(exist_ok=True);(state/'x-translation-smoke.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 STAMP.parent.mkdir(parents=True,exist_ok=True);STAMP.write_text(json.dumps(result,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
