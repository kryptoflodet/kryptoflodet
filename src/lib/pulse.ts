import {isMetricStale,movementToScore,type MarketContext} from './market-context';
import type {MarketData,LiveQuote} from './market';
import type {NewsItem} from './types';
const HOUR=3600_000;
export function metricFresh(metric:{checkedAt:string|null;observedAt:string|null},maxAge:number,now:number){return !isMetricStale(metric.checkedAt,maxAge,now)&&!isMetricStale(metric.observedAt,maxAge,now);}
export function pulseLabel(value:number|null){if(value===null)return 'Inväntar data';if(value<=20)return 'Extremt negativ';if(value<=40)return 'Negativ';if(value<=60)return 'Neutral';if(value<=80)return 'Positiv';return 'Extremt positiv';}
export function quoteFresh(q:LiveQuote|undefined,now:number){return !!q&&!isMetricStale(q.updatedAt,10*60_000,now);}
export function pulseReading(context:MarketContext,market:MarketData,now:number){
 const globalFresh=metricFresh(context.market,2*HOUR,now);
 const btc=market.quotes.find(q=>q.symbol==='BTC');
 const btcChange=quoteFresh(btc,now)?btc!.change24h:globalFresh?context.market.btcChange24h:null;
 const fear=metricFresh(context.fearGreed,36*HOUR,now)?context.fearGreed.value:null;
 const total=globalFresh?context.market.marketCapChange24h:null;
 // Fixed weights: never silently reweight missing inputs.
 const score=fear!==null&&btcChange!==null&&total!==null?Math.round(.5*fear+.25*movementToScore(btcChange)+.25*movementToScore(total)):null;
 return {score,label:pulseLabel(score),btcChange,total,fear,globalFresh};
}
export function briefHeading(now:number){const hour=Number(new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Stockholm',hour:'2-digit',hourCycle:'h23'}).format(now));return hour<11?'God morgon – krypto på 30 sekunder':hour<18?'Marknaden just nu':'Dagen på 30 sekunder';}
export function currentNews(items:NewsItem[],now:number){const seen=new Set<string>();return items.filter(n=>{const age=now-Date.parse(n.publishedAt);return !n.demo&&n.status!=='rumor'&&n.analysisMethod==='editorial'&&age>=0&&age<=48*HOUR&&!/prognos|price prediction|prisprognos/i.test(n.contentType||'');}).sort((a,b)=>b.importance-a.importance||Date.parse(b.publishedAt)-Date.parse(a.publishedAt)).filter(n=>{const key=n.eventKey||n.originalUrl;if(seen.has(key))return false;seen.add(key);return true;});}
export function possibleDrivers(items:NewsItem[],now:number){return currentNews(items,now).filter(n=>/likvider|liquidat|etf|inflation|räntebesked|federal reserve|\bfed\b|hack|intrång|utflöde|inflöde/i.test(n.title+' '+n.summary)).slice(0,3);}
export type UpcomingEvent={id:string;title:string;startAt:string;endAt:string;dateOnly:boolean;source:string;url:string;why:string;coins:string[];checkedAt:string};
export function upcomingEvents(events:UpcomingEvent[],now:number,coins:string[]=[]){return events.filter(e=>Number.isFinite(Date.parse(e.startAt))&&Date.parse(e.endAt)>now&&(!e.coins.length||e.coins.some(c=>coins.includes(c)))).sort((a,b)=>Date.parse(a.startAt)-Date.parse(b.startAt)).slice(0,3);}
export function eventTime(event:UpcomingEvent){return new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',day:'numeric',month:'short',...(event.dateOnly?{}:{hour:'2-digit',minute:'2-digit'})}).format(new Date(event.startAt));}
