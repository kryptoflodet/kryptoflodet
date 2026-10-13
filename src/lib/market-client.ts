import {isMarketFresh,normalizeMarket,TOP_MARKET_COUNT,trackedCoins,type MarketData} from './market';
const cacheKey='kryptoflodet-market-v2';
const base=import.meta.env.BASE_URL;
const API='https://api.coingecko.com/api/v3';

export function loadCachedMarket():MarketData|null{
 try{const data=normalizeMarket(JSON.parse(localStorage.getItem(cacheKey)||'null') as unknown);if(data.quotes.length<TOP_MARKET_COUNT-5)return null;return {...data,mode:'stale'};}catch{return null;}
}
async function getJson(url:string,timeout=15000):Promise<unknown>{
 const response=await fetch(url,{headers:{Accept:'application/json'},cache:'no-store',signal:AbortSignal.timeout(timeout)});
 if(!response.ok)throw new Error('Kurskällan svarade med status '+response.status);
 return response.json();
}
function marketUrl(currency:string,ids?:string[]){
 const params=new URLSearchParams({vs_currency:currency,order:'market_cap_desc',per_page:String(TOP_MARKET_COUNT),page:'1',sparkline:'false',price_change_percentage:'24h'});
 if(ids?.length)params.set('ids',ids.join(','));
 return `${API}/coins/markets?${params}`;
}
function usableRows(value:unknown):value is Record<string,unknown>[] {return Array.isArray(value)&&value.length>=TOP_MARKET_COUNT-5&&value.every(row=>row&&typeof row==='object'&&!Array.isArray(row));}

export async function fetchMarket():Promise<MarketData>{
 // CoinGecko refreshes market data about once a minute; reuse a fresh same-device response between polls.
 try{const cached=normalizeMarket(JSON.parse(localStorage.getItem(cacheKey)||'null') as unknown);const age=cached.fetchedAt?Date.now()-Date.parse(cached.fetchedAt):Infinity;if(age>=0&&age<60000&&isMarketFresh(cached))return {...cached,mode:'live'};}catch{/* Continue with the public source or published snapshot. */}
 let data:MarketData;
 try{
  const usdRows=await getJson(marketUrl('usd'));if(!usableRows(usdRows))throw new Error('CoinGecko returned fewer than 45 market rows');
  const ids=usdRows.map(row=>typeof row.id==='string'?row.id:'').filter(Boolean);if(ids.length<TOP_MARKET_COUNT-5)throw new Error('CoinGecko top-50 response has too few coin IDs');
  let sekRows:unknown=[];
  try{const candidate=await getJson(marketUrl('sek',ids));if(usableRows(candidate))sekRows=candidate;}
  catch{
   try{
    const previous=await getJson(base+'data/market.json?t='+Date.now(),10000) as Record<string,unknown>;
    if(Array.isArray(previous.sekCoins))sekRows=previous.sekCoins;
    else sekRows=trackedCoins.flatMap(([id])=>{const row=previous[id];if(!row||typeof row!=='object'||Array.isArray(row))return [];const legacy=row as Record<string,unknown>;if(typeof legacy.sek!=='number')return [];const updatedAt=typeof legacy.last_updated_at==='number'?new Date(legacy.last_updated_at*1000).toISOString():null;return [{id,current_price:legacy.sek,price_change_percentage_24h:legacy.sek_24h_change,last_updated:updatedAt}];});
   }catch{/* USD market data can still be shown if SEK is rate-limited. */}
  }
  data=normalizeMarket({coins:usdRows,sekCoins:sekRows,fetchedAt:new Date().toISOString()});
 }catch{
  const snapshot=await getJson(base+'data/market.json?t='+Date.now(),10000);data=normalizeMarket(snapshot);
  if(data.quotes.length<TOP_MARKET_COUNT-5)throw new Error('CoinGecko and the published top-50 snapshot are unavailable');
 }
 try{localStorage.setItem(cacheKey,JSON.stringify(data));}catch{/* Browsing remains available without local storage. */}
 return data;
}
