export type ContextMetric<T extends Record<string,unknown>>=T&{checkedAt:string|null;observedAt:string|null};
export type MarketContext={
 schemaVersion:1;
 generatedAt:string|null;
 fearGreed:ContextMetric<{value:number|null;classification:string|null}>;
 market:ContextMetric<{btcDominance:number|null;ethDominance:number|null;marketCapChange24h:number|null;btcChange24h:number|null;ethChange24h:number|null}>;
 altcoinSeason:ContextMetric<{value:number|null;source:string|null}>;
};
export const emptyMarketContext:MarketContext={schemaVersion:1,generatedAt:null,fearGreed:{value:null,classification:null,checkedAt:null,observedAt:null},market:{btcDominance:null,ethDominance:null,marketCapChange24h:null,btcChange24h:null,ethChange24h:null,checkedAt:null,observedAt:null},altcoinSeason:{value:null,source:null,checkedAt:null,observedAt:null}};
const numberOrNull=(value:unknown,min=-Infinity,max=Infinity):number|null=>typeof value==='number'&&Number.isFinite(value)&&value>=min&&value<=max?value:null;
const dateOrNull=(value:unknown):string|null=>typeof value==='string'&&Number.isFinite(Date.parse(value))?new Date(value).toISOString():null;
const textOrNull=(value:unknown):string|null=>typeof value==='string'&&value.trim()?value.trim():null;
export function normalizeMarketContext(input:unknown):MarketContext|null{
 if(!input||typeof input!=='object')return null;
 const root=input as Record<string,unknown>;if(root.schemaVersion!==1)return null;
 const fear=root.fearGreed&&typeof root.fearGreed==='object'?root.fearGreed as Record<string,unknown>:{};
 const market=root.market&&typeof root.market==='object'?root.market as Record<string,unknown>:{};
 const alt=root.altcoinSeason&&typeof root.altcoinSeason==='object'?root.altcoinSeason as Record<string,unknown>:{};
 return {schemaVersion:1,generatedAt:dateOrNull(root.generatedAt),fearGreed:{value:numberOrNull(fear.value,0,100),classification:textOrNull(fear.classification),checkedAt:dateOrNull(fear.checkedAt),observedAt:dateOrNull(fear.observedAt)},market:{btcDominance:numberOrNull(market.btcDominance,0,100),ethDominance:numberOrNull(market.ethDominance,0,100),marketCapChange24h:numberOrNull(market.marketCapChange24h,-1000,1000),btcChange24h:numberOrNull(market.btcChange24h,-1000,1000),ethChange24h:numberOrNull(market.ethChange24h,-1000,1000),checkedAt:dateOrNull(market.checkedAt),observedAt:dateOrNull(market.observedAt)},altcoinSeason:{value:numberOrNull(alt.value,0,100),source:textOrNull(alt.source),checkedAt:dateOrNull(alt.checkedAt),observedAt:dateOrNull(alt.observedAt)}};
}
export function movementToScore(change24h:number):number{return Math.max(0,Math.min(100,50+change24h*5));}
export function calculateSentiment(context:MarketContext):number|null{
 const parts:{value:number;weight:number}[]=[];
 if(context.fearGreed.value!==null)parts.push({value:context.fearGreed.value,weight:.5});
 if(context.market.btcChange24h!==null)parts.push({value:movementToScore(context.market.btcChange24h),weight:.25});
 if(context.market.marketCapChange24h!==null)parts.push({value:movementToScore(context.market.marketCapChange24h),weight:.25});
 const weight=parts.reduce((sum,item)=>sum+item.weight,0);
 return weight?Math.round(parts.reduce((sum,item)=>sum+item.value*item.weight,0)/weight):null;
}
export function sentimentLabel(value:number|null):string{
 if(value===null)return 'INVÄNTAR DATA';if(value<=24)return 'EXTREMT RÄDD';if(value<=44)return 'RÄDD';if(value<=55)return 'NEUTRAL';if(value<=74)return 'GIRIG';return 'EXTREMT GIRIG';
}
export function altcoinSeasonLabel(value:number|null):string{
 if(value===null)return 'INDEX SAKNAS';if(value<=25)return 'BITCOIN SEASON';if(value<75)return 'NEUTRAL';return 'ALTCOIN SEASON';
}
export function isMetricStale(checkedAt:string|null,maxAgeMs:number,now=Date.now()):boolean{
 if(!checkedAt)return true;const age=now-Date.parse(checkedAt);return !Number.isFinite(age)||age>maxAgeMs||age< -5*60_000;
}
