export const trackedCoins = [
 ['bitcoin','BTC','Bitcoin'],['ethereum','ETH','Ethereum'],['solana','SOL','Solana'],['sui','SUI','Sui'],['hedera-hashgraph','HBAR','Hedera'],['ondo-finance','ONDO','Ondo'],['ripple','XRP','XRP'],['cardano','ADA','Cardano'],['dogecoin','DOGE','Dogecoin'],['stellar','XLM','Stellar'],['avalanche-2','AVAX','Avalanche'],['chainlink','LINK','Chainlink'],['binancecoin','BNB','BNB'],['hyperliquid','HYPE','Hyperliquid'],['litecoin','LTC','Litecoin'],
] as const;
export interface LiveQuote {symbol:string;name:string;price:number|null;priceSek:number|null;change24h:number|null;changeSek24h:number|null;updatedAt:string|null;}
export interface MarketData {mode:'live'|'stale'|'unavailable';source:'CoinGecko';fetchedAt:string|null;quotes:LiveQuote[];}
export const emptyQuotes:LiveQuote[]=trackedCoins.map(([,symbol,name])=>({symbol,name,price:null,priceSek:null,change24h:null,changeSek24h:null,updatedAt:null}));
const numberOrNull=(v:unknown)=>typeof v==='number'&&Number.isFinite(v)?v:null;
export function normalizeMarket(raw:unknown,now=Date.now()):MarketData {
 if(!raw||typeof raw!=='object'||Array.isArray(raw))throw new Error('Invalid market response');
 const quotes=trackedCoins.map(([id,symbol,name])=>{
 const row=(raw as Record<string,Record<string,unknown>>)[id]||{};
 const seconds=numberOrNull(row.last_updated_at);
 const validTime=seconds!==null&&seconds>0&&seconds*1000<=now+60000;
 return {symbol,name,price:validTime&&Number(row.usd)>0?numberOrNull(row.usd):null,priceSek:validTime&&Number(row.sek)>0?numberOrNull(row.sek):null,change24h:numberOrNull(row.usd_24h_change),changeSek24h:numberOrNull(row.sek_24h_change),updatedAt:validTime?new Date(seconds!*1000).toISOString():null};
 });
 if(quotes.every(q=>q.price===null))throw new Error('No prices returned');
 const fresh=quotes.every(q=>q.price!==null&&q.priceSek!==null&&q.updatedAt&&now-Date.parse(q.updatedAt)<300000);
 return {mode:fresh?'live':'stale',source:'CoinGecko',fetchedAt:new Date(now).toISOString(),quotes};
}
