import {initialMarket} from '@/lib/market-initial';
import {trackedCoins,normalizeMarket,emptyQuotes,type MarketData} from '@/lib/market';
let cached:MarketData|null=null;
let pending:Promise<MarketData>|null=null;
async function fetchPrices():Promise<MarketData>{
 const params=new URLSearchParams({ids:trackedCoins.map(c=>c[0]).join(','),vs_currencies:'usd,sek',include_24hr_change:'true',include_last_updated_at:'true'});
 const response=await fetch('https://api.coingecko.com/api/v3/simple/price?'+params,{headers:{Accept:'application/json'},signal:AbortSignal.timeout(12000)});
 if(!response.ok)throw new Error('Market provider HTTP '+response.status);
 return normalizeMarket(await response.json());
}
export async function GET(request:Request){
 const cache=typeof caches!=='undefined'?(caches as unknown as {default?:Cache}).default:undefined;
 const key=new Request(new URL('/api/market-cache-v1',request.url));
 let previous=cached;
 try{
  if(!previous&&cache){try{const hit=await cache.match(key);if(hit)previous=await hit.json() as MarketData;}catch(error){console.warn('Market cache read skipped',String(error));}}
  if(previous?.fetchedAt&&Date.now()-Date.parse(previous.fetchedAt)<60000)return Response.json(previous,{headers:{'Cache-Control':'private, max-age=15'}});
  pending??=fetchPrices().finally(()=>{pending=null;});
  const data=await pending;cached=data;
  if(cache)try{await cache.put(key,Response.json(data,{headers:{'Cache-Control':'public, max-age=86400'}}));}catch{}
  return Response.json(data,{headers:{'Cache-Control':'private, max-age=15'}});
 }catch(error){
  console.error('Market fetch failed',String(error));
  return Response.json({...previous||initialMarket,mode:'stale'},{headers:{'Cache-Control':'no-store'}});
 }
}
