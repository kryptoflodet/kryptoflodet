import {normalizeMarket,trackedCoins,type MarketData} from './market';
const cacheKey='kryptoflodet-market-v1';
export function loadCachedMarket():MarketData|null{
 try{
  const saved=JSON.parse(localStorage.getItem(cacheKey)||'null') as MarketData|null;
  if(!saved||saved.source!=='CoinGecko'||saved.quotes?.length!==trackedCoins.length||!saved.fetchedAt)return null;
  if(!saved.quotes.every((q,i)=>q.symbol===trackedCoins[i][1]&&(q.price===null||typeof q.price==='number')&&(q.priceSek===null||typeof q.priceSek==='number')))return null;
  return {...saved,mode:'stale'};
 }catch{return null;}
}
export async function fetchMarket():Promise<MarketData>{
 const params=new URLSearchParams({ids:trackedCoins.map(c=>c[0]).join(','),vs_currencies:'usd,sek',include_24hr_change:'true',include_last_updated_at:'true'});
 const response=await fetch('https://api.coingecko.com/api/v3/simple/price?'+params,{headers:{Accept:'application/json'},signal:AbortSignal.timeout(15000)});
 if(!response.ok)throw new Error('Kurskällan svarade med status '+response.status);
 const data=normalizeMarket(await response.json());
 try{localStorage.setItem(cacheKey,JSON.stringify(data));}catch{/* Browsing remains available without local storage. */}
 return data;
}
