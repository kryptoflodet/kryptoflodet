import raw from '../../public/data/market-context.json';
import {normalizeMarketContext,type MarketContext} from './market-context';
const cacheKey='kryptoflodet-market-context-v1';
const base=import.meta.env.BASE_URL;
export const initialMarketContext=normalizeMarketContext(raw)||normalizeMarketContext({schemaVersion:1})!;
export function loadCachedMarketContext():MarketContext|null{
 try{return normalizeMarketContext(JSON.parse(localStorage.getItem(cacheKey)||'null'));}catch{return null;}
}
export async function fetchMarketContext():Promise<MarketContext>{
 const response=await fetch(base+'data/market-context.json?t='+Date.now(),{cache:'no-store',signal:AbortSignal.timeout(10000)});
 if(!response.ok)throw new Error('Marknadsöversikten kunde inte hämtas');
 const data=normalizeMarketContext(await response.json());if(!data)throw new Error('Marknadsöversikten har ett ogiltigt format');
 try{localStorage.setItem(cacheKey,JSON.stringify(data));}catch{/* The in-page snapshot remains available without local storage. */}
 return data;
}
