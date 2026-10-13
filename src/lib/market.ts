export const trackedCoins = [
 ['bitcoin','BTC','Bitcoin'],['ethereum','ETH','Ethereum'],['solana','SOL','Solana'],['sui','SUI','Sui'],['hedera-hashgraph','HBAR','Hedera'],['ondo-finance','ONDO','Ondo'],['ripple','XRP','XRP'],['cardano','ADA','Cardano'],['dogecoin','DOGE','Dogecoin'],['stellar','XLM','Stellar'],['avalanche-2','AVAX','Avalanche'],['chainlink','LINK','Chainlink'],['binancecoin','BNB','BNB'],['hyperliquid','HYPE','Hyperliquid'],['litecoin','LTC','Litecoin'],
] as const;

export const TOP_MARKET_COUNT=50;
export interface LiveQuote {
 id:string;symbol:string;name:string;marketCapRank:number|null;
 price:number|null;priceSek:number|null;change24h:number|null;changeSek24h:number|null;
 marketCap:number|null;marketCapSek:number|null;volume24h:number|null;volume24hSek:number|null;updatedAt:string|null;
}
export interface MarketData {mode:'live'|'stale'|'unavailable';source:'CoinGecko';fetchedAt:string|null;quotes:LiveQuote[];}
export const emptyQuotes:LiveQuote[]=trackedCoins.map(([id,symbol,name],index)=>({id,symbol,name,marketCapRank:index+1,price:null,priceSek:null,change24h:null,changeSek24h:null,marketCap:null,marketCapSek:null,volume24h:null,volume24hSek:null,updatedAt:null}));
const numberOrNull=(v:unknown):number|null=>typeof v==='number'&&Number.isFinite(v)?v:null;
const textOrNull=(v:unknown):string|null=>typeof v==='string'&&v.trim()?v.trim():null;
const dateOrNull=(v:unknown):string|null=>typeof v==='string'&&Number.isFinite(Date.parse(v))?new Date(v).toISOString():null;

function normalizeRows(usdRows:unknown,sekRows:unknown,now:number):MarketData {
 if(!Array.isArray(usdRows))throw new Error('CoinGecko market response is not a list');
 if(usdRows.length<TOP_MARKET_COUNT-5)throw new Error(`CoinGecko returned only ${usdRows.length} of the top ${TOP_MARKET_COUNT} coins`);
 const sekById=new Map<string,Record<string,unknown>>();
 if(Array.isArray(sekRows))for(const candidate of sekRows){if(candidate&&typeof candidate==='object'&&!Array.isArray(candidate)){const row=candidate as Record<string,unknown>;const id=textOrNull(row.id);if(id)sekById.set(id,row);}}
 const quotes=usdRows.flatMap((candidate,index)=>{
  if(!candidate||typeof candidate!=='object'||Array.isArray(candidate))return [];
  const row=candidate as Record<string,unknown>;const id=textOrNull(row.id);const name=textOrNull(row.name);const symbol=textOrNull(row.symbol)?.toUpperCase();if(!id||!name||!symbol)return [];
  const sek=sekById.get(id)||{};const rank=numberOrNull(row.market_cap_rank);
  return [{id,symbol,name,marketCapRank:rank&&rank>0?rank:index+1,price:numberOrNull(row.current_price),priceSek:numberOrNull(sek.current_price),change24h:numberOrNull(row.price_change_percentage_24h),changeSek24h:numberOrNull(sek.price_change_percentage_24h),marketCap:numberOrNull(row.market_cap),marketCapSek:numberOrNull(sek.market_cap),volume24h:numberOrNull(row.total_volume),volume24hSek:numberOrNull(sek.total_volume),updatedAt:dateOrNull(row.last_updated)||dateOrNull(sek.last_updated)} satisfies LiveQuote];
 }).sort((a,b)=>(a.marketCapRank??Infinity)-(b.marketCapRank??Infinity)).slice(0,TOP_MARKET_COUNT);
 if(quotes.length<TOP_MARKET_COUNT-5||quotes.every(q=>q.price===null))throw new Error('CoinGecko top 50 response contains too little usable market data');
 const fresh=quotes.filter(q=>q.price!==null&&q.updatedAt&&now-Date.parse(q.updatedAt)<300000&&now-Date.parse(q.updatedAt)>=-60000).length>=TOP_MARKET_COUNT-5;
 return {mode:fresh?'live':'stale',source:'CoinGecko',fetchedAt:new Date(now).toISOString(),quotes};
}

function normalizeCachedQuotes(rows:unknown,now:number,fetchedAt:unknown):MarketData {
 if(!Array.isArray(rows))throw new Error('Invalid cached market quotes');
 const quotes=rows.flatMap((candidate,index)=>{
  if(!candidate||typeof candidate!=='object'||Array.isArray(candidate))return [];
  const row=candidate as Record<string,unknown>;const symbol=textOrNull(row.symbol)?.toUpperCase();const name=textOrNull(row.name);const id=textOrNull(row.id)||(trackedCoins.find(c=>c[1]===symbol)?.[0]||'');
  if(!id||!symbol||!name)return [];
  const rank=numberOrNull(row.marketCapRank);
  return [{id,symbol,name,marketCapRank:rank&&rank>0?rank:index+1,price:numberOrNull(row.price),priceSek:numberOrNull(row.priceSek),change24h:numberOrNull(row.change24h),changeSek24h:numberOrNull(row.changeSek24h),marketCap:numberOrNull(row.marketCap),marketCapSek:numberOrNull(row.marketCapSek),volume24h:numberOrNull(row.volume24h),volume24hSek:numberOrNull(row.volume24hSek),updatedAt:dateOrNull(row.updatedAt)} satisfies LiveQuote];
 }).sort((a,b)=>(a.marketCapRank??Infinity)-(b.marketCapRank??Infinity)).slice(0,TOP_MARKET_COUNT);
 if(!quotes.length)throw new Error('Cached market data contains no usable quotes');
 const savedAt=dateOrNull(fetchedAt);const fresh=quotes.length>=TOP_MARKET_COUNT-5&&quotes.filter(q=>q.price!==null&&q.updatedAt&&now-Date.parse(q.updatedAt)<300000&&now-Date.parse(q.updatedAt)>=-60000).length>=TOP_MARKET_COUNT-5;
 return {mode:fresh?'live':'stale',source:'CoinGecko',fetchedAt:savedAt||new Date(now).toISOString(),quotes};
}

export function normalizeMarket(raw:unknown,now=Date.now()):MarketData {
 if(!raw||typeof raw!=='object')throw new Error('Invalid market response');
 if(Array.isArray(raw))return normalizeRows(raw,[],now);
 const input=raw as Record<string,unknown>;
 if(Array.isArray(input.quotes))return normalizeCachedQuotes(input.quotes,now,input.fetchedAt);
 if(Array.isArray(input.coins))return normalizeRows(input.coins,input.sekCoins,now);
 // Read older Pages snapshots until the scheduled fetch has replaced them with top-50 data.
 const quotes=trackedCoins.map(([id,symbol,name],index)=>{
  const row=input[id]&&typeof input[id]==='object'&&!Array.isArray(input[id])?input[id] as Record<string,unknown>:{};const seconds=numberOrNull(row.last_updated_at);
  const updatedAt=seconds!==null&&seconds>0&&seconds*1000<=now+60000?new Date(seconds*1000).toISOString():null;
  return {id,symbol,name,marketCapRank:index+1,price:typeof row.usd==='number'&&row.usd>0?row.usd:null,priceSek:typeof row.sek==='number'&&row.sek>0?row.sek:null,change24h:numberOrNull(row.usd_24h_change),changeSek24h:numberOrNull(row.sek_24h_change),marketCap:null,marketCapSek:null,volume24h:null,volume24hSek:null,updatedAt} satisfies LiveQuote;
 });
 if(quotes.every(q=>q.price===null))throw new Error('No prices returned');
 const fresh=quotes.every(q=>q.price!==null&&q.priceSek!==null&&q.updatedAt&&now-Date.parse(q.updatedAt)<300000);
 return {mode:fresh?'live':'stale',source:'CoinGecko',fetchedAt:new Date(now).toISOString(),quotes};
}

export function isMarketFresh(data:MarketData,now=Date.now()):boolean {
 const fresh=data.quotes.filter(q=>q.price!==null&&q.updatedAt&&now-Date.parse(q.updatedAt)<300000&&now-Date.parse(q.updatedAt)>=-60000).length;
 return data.quotes.length>=TOP_MARKET_COUNT-5&&fresh>=TOP_MARKET_COUNT-5;
}
