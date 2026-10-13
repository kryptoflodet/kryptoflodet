import {trackedCoins} from './market';
export type RangeKey='24h'|'today'|'week'|'month'|'quarter'|'ytd'|'year'|'3y'|'5y'|'max';
export const chartRanges: {key:RangeKey;label:string}[]=[{key:'24h',label:'24 timmar'},{key:'today',label:'I dag'},{key:'week',label:'1 vecka'},{key:'month',label:'1 månad'},{key:'quarter',label:'3 månader'},{key:'ytd',label:'I år'},{key:'year',label:'1 år'},{key:'3y',label:'3 år'},{key:'5y',label:'5 år'},{key:'max',label:'All historik'}];
export interface ChartData {points:[number,number][];source:string;unit:string;fetchedAt:number;note:string;}
export function rangeStart(range:RangeKey,now=Date.now()){
 const d=new Date(now);
 if(range==='max')return 0;
 if(range==='today'){
  const parts=Object.fromEntries(new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',year:'numeric',month:'2-digit',day:'2-digit',timeZoneName:'longOffset'}).formatToParts(d).map(p=>[p.type,p.value]));
  return Date.parse(`${parts.year}-${parts.month}-${parts.day}T00:00:00${parts.timeZoneName.replace('GMT','')||'+00:00'}`);
 }
 if(range==='ytd')return Date.UTC(Number(new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',year:'numeric'}).format(d)),0,1)-3600000;
 return now-({ '24h':1,week:7,month:30,quarter:90,year:365,'3y':1095,'5y':1825}[range]||1)*86400000;
}
export function normalizePoints(raw:unknown,now=Date.now()):[number,number][]{
 if(!Array.isArray(raw))throw new Error('Felaktigt diagramsvar');
 const unique=new Map<number,number>();
 for(const p of raw)if(Array.isArray(p)&&typeof p[0]==='number'&&typeof p[1]==='number'&&Number.isFinite(p[0])&&Number.isFinite(p[1])&&p[0]>0&&p[0]<=now+60000&&p[1]>0)unique.set(p[0],p[1]);
 const points=[...unique].sort((a,b)=>a[0]-b[0]) as [number,number][];
 if(points.length<2)throw new Error('För lite kurshistorik för perioden');return points;
}
const cache=new Map<string,ChartData>();
export async function fetchChart(symbol:string,range:RangeKey,currency:string,signal:AbortSignal,coinId?:string):Promise<ChartData>{
 const id=coinId||trackedCoins.find(c=>c[1]===symbol)?.[0];if(!id)throw new Error('Okänd valuta');
 const key=[id,range,currency].join(':');const saved=cache.get(key);if(saved&&Date.now()-saved.fetchedAt<60000)return saved;
 const now=Date.now(),start=rangeStart(range,now);const long=['3y','5y','max'].includes(range);
 if(!long){
  try{
   const days=Math.min(365,Math.max(1,Math.ceil((now-start)/86400000)));
   const r=await fetch(`https://api.coingecko.com/api/v3/coins/${encodeURIComponent(id)}/market_chart?vs_currency=${currency.toLowerCase()}&days=${days}`,{signal:AbortSignal.any([signal,AbortSignal.timeout(12000)])});
   if(!r.ok)throw new Error('Kurskälla tillfälligt otillgänglig');
   const raw=await r.json();const points=normalizePoints(raw.prices).filter(p=>p[0]>=start);
   if(points.length<2)throw new Error('Historik saknas');
   const data={points,source:'CoinGecko',unit:currency,fetchedAt:now,note:'Sammanvägda marknadspriser. Diagrammets senaste datapunkt kan ligga efter det aktuella priset.'};cache.set(key,data);return data;
  }catch(e){if(signal.aborted)throw e;}
 }
 const interval=long?'1w':range==='24h'||range==='today'?'5m':range==='week'?'1h':range==='month'?'4h':'1d';
 const params=new URLSearchParams({symbol:symbol+'USDT',interval,limit:'1000'});
 if(start)params.set('startTime',String(start));
 const response=await fetch('https://data-api.binance.vision/api/v3/klines?'+params,{signal:AbortSignal.any([signal,AbortSignal.timeout(12000)])});
 if(!response.ok)throw new Error('Historik kunde inte hämtas för denna valuta och period. Välj en kortare period eller försök igen.');
 const rows=await response.json();if(!Array.isArray(rows))throw new Error('Historiken saknas hos kurskällan');
 const points=normalizePoints(rows.map((r:unknown[])=>[Math.min(Number(r[6]),now),Number(r[4])]));
 const data={points,source:'Binance',unit:'USDT',fetchedAt:now,note:'Handelsparet '+symbol+'/USDT. USDT är inte USD eller SEK. Historiken börjar när paret noterades på Binance, inte när kryptovalutan skapades. Veckopunkter används för långa perioder.'};cache.set(key,data);return data;
}
