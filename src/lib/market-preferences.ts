import type {LiveQuote} from './market';
export type MarketSort='rank'|'name'|'price-high'|'price-low'|'change-high'|'change-low'|'cap-high'|'cap-low'|'volume-high'|'volume-low';
export const MARKET_HIDDEN_KEY='kryptokollen-market-hidden-v1';
function metric(q:LiveQuote,sort:MarketSort,currency:string):number|null {
 if(sort==='price-high'||sort==='price-low')return currency==='SEK'?q.priceSek:q.price;
 if(sort==='change-high'||sort==='change-low')return currency==='SEK'?q.changeSek24h:q.change24h;
 if(sort==='cap-high'||sort==='cap-low')return currency==='SEK'?q.marketCapSek:q.marketCap;
 if(sort==='volume-high'||sort==='volume-low')return currency==='SEK'?q.volume24hSek:q.volume24h;
 return null;
}
export function sortMarketQuotes(quotes:LiveQuote[],sort:MarketSort,currency='USD'):LiveQuote[]{
 return [...quotes].sort((a,b)=>{
  if(sort==='name')return a.name.localeCompare(b.name,'sv')||((a.marketCapRank??Infinity)-(b.marketCapRank??Infinity));
  if(sort==='rank')return (a.marketCapRank??Infinity)-(b.marketCapRank??Infinity);
  const left=metric(a,sort,currency),right=metric(b,sort,currency);
  if(left===null)return right===null?(a.marketCapRank??Infinity)-(b.marketCapRank??Infinity):1;
  if(right===null)return -1;
  return (left-right)*(sort.endsWith('-low')?1:-1)||((a.marketCapRank??Infinity)-(b.marketCapRank??Infinity));
 });
}
export function normalizeHiddenSymbols(raw:unknown):string[]{
 if(!Array.isArray(raw))return [];
 return [...new Set(raw.filter((value):value is string=>typeof value==='string'&&/^[A-Z0-9._-]{1,20}$/i.test(value)).map(value=>value.toUpperCase()))];
}
export function toggleHiddenSymbol(hidden:string[],symbol:string,hide:boolean):string[]{
 const current=new Set(normalizeHiddenSymbols(hidden));if(hide)current.add(symbol.toUpperCase());else current.delete(symbol.toUpperCase());return [...current];
}
