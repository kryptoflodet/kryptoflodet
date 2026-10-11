"""Refresh a same-origin fallback without inventing timestamps or prices."""
import json,pathlib,re,urllib.request,urllib.parse
root=pathlib.Path(__file__).resolve().parents[1]
ids=re.findall(r"\['([^']+)','[A-Z]+','[^']+'\]",(root/'src/lib/market.ts').read_text())
url='https://api.coingecko.com/api/v3/simple/price?'+urllib.parse.urlencode(dict(ids=','.join(ids),vs_currencies='usd,sek',include_24hr_change='true',include_last_updated_at='true'))
try:
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Kryptoflodet/1.0','Accept':'application/json'}),timeout=20) as r:data=json.load(r)
 if not isinstance(data,dict) or not any(isinstance(data.get(i),dict) and data[i].get('last_updated_at') and data[i].get('usd',0)>0 for i in ids):raise ValueError('Tomma kursdata')
 target=root/'public/data/market.json';target.write_text(json.dumps(data,ensure_ascii=False)+'\n')
 print('Marknadsögonblicksbild uppdaterad för',len(data),'valutor')
except Exception as e:
 print('Kurskällan kunde inte nås; tidigare ögonblicksbild behålls:',e)
