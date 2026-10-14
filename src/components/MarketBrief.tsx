import {MARKET_ORDER_KEY,normalizeMarketOrder} from '../lib/market-preferences';
import type {MarketContext} from '../lib/market-context';
import type {MarketData} from '../lib/market';
import type {NewsItem} from '../lib/types';
import {briefHeading,currentNews,eventTime,possibleDrivers,pulseReading,quoteFresh,upcomingEvents,type UpcomingEvent} from '../lib/pulse';
import events from '../lib/upcoming-events.json';
export const percent=(v:number|null|undefined)=>v==null?'—':`${v>=0?'+':''}${v.toLocaleString('sv-SE',{maximumFractionDigits:1})} %`;
export function Upcoming({now,coins}:{now:number;coins:string[]}){
 const next=upcomingEvents(events as UpcomingEvent[],now,coins);
 return <section className="brief-upcoming" aria-label="Kommande händelser"><h3>Kommande</h3>{next.length?next.map(e=><details key={e.id}><summary><time dateTime={e.startAt}>{eventTime(e)}</time><span>{e.title}</span></summary><p>{e.why}</p><p><a href={e.url} target="_blank" rel="noopener noreferrer">{e.source} ↗</a> · Datum kontrollerat {e.checkedAt} · Kan ändras.</p></details>):<p>Inga källbelagda kommande datum i urvalet.</p>}<small>Utvalda makrodatum. Coin-specifika datum visas när de har verifierats.</small></section>;
}
export default function MarketBrief({context,market,items,hidden,now,onCoin,onArticle}:{context:MarketContext;market:MarketData;items:NewsItem[];hidden:string[];now:number;onCoin:(symbol:string)=>void;onArticle:(item:NewsItem)=>void}){
 const reading=pulseReading(context,market,now);const news=currentNews(items,now).slice(0,3);
 let order:string[]=[];try{order=normalizeMarketOrder(JSON.parse(localStorage.getItem(MARKET_ORDER_KEY)||'[]'),market.quotes.map(q=>q.symbol));}catch{/* Default market order remains usable. */}
 const visible=market.quotes.filter(q=>!hidden.includes(q.symbol)).sort((a,b)=>order.indexOf(a.symbol)-order.indexOf(b.symbol));
 const next=upcomingEvents(events as UpcomingEvent[],now,visible.map(q=>q.symbol))[0];
 const picks=['BTC','ETH',visible.find(q=>!['BTC','ETH'].includes(q.symbol))?.symbol].filter((s):s is string=>!!s).map(s=>market.quotes.find(q=>q.symbol===s)).filter(q=>!!q);
 const drivers=possibleDrivers(items,now);const moving=(reading.btcChange!==null&&Math.abs(reading.btcChange)>=2)||(reading.total!==null&&Math.abs(reading.total)>=2);
 return <section className="market-brief" aria-labelledby="brief-title"><div className="brief-heading"><span>FÖRSTÅ KRYPTOMARKNADEN PÅ 30 SEKUNDER</span><h2 id="brief-title">{briefHeading(now)}</h2><small>Marknaden: {reading.label.toLocaleLowerCase('sv-SE')} · Löpande överblick, inte en avslutad dagsrapport.</small></div>
 <div className="brief-quotes">{picks.map(q=><button key={q.symbol} onClick={()=>onCoin(q.symbol)} aria-label={`Visa diagram för ${q.name}`}><b>{q.symbol}</b><span className={quoteFresh(q,now)?(q.change24h??0)>=0?'up':'down':''}>{percent(q.change24h)}</span><small>{quoteFresh(q,now)?'24h · USD':'Fördröjt · 24h USD'}</small></button>)}</div>
 <div className="brief-news"><h3>Det viktigaste just nu</h3>{news.length?<ul>{news.map(n=><li key={n.id}><button onClick={()=>onArticle(n)}>{n.title} <span>↗</span></button></li>)}</ul>:<p>Inga aktuella granskade nyheter att sammanfatta. Nyhetsflödet nedan visar även inlägg från X.</p>}</div>
 <details className="brief-drivers"><summary><span>Varför rör sig marknaden?</span><small>BTC {percent(reading.btcChange)}</small></summary><h3>{moving?'Möjliga drivkrafter':'Aktuellt sammanhang'}</h3><p>{moving?'Bitcoin eller totalmarknaden rör sig minst 2 % på ett dygn.':'Ingen färsk dygnsrörelse på minst 2 % har registrerats i Bitcoin eller totalmarknaden.'} Ämnesurval ur granskade nyheter, inte ett fastställt orsakssamband.</p>{drivers.length?<ul>{drivers.map(n=><li key={n.id}><button onClick={()=>onArticle(n)}>{n.title} ↗</button><small>{n.status==='confirmed'?'Bekräftat avgränsat besked':'Källuppgift · ej oberoende bekräftad'}</small></li>)}</ul>:<p>Underlaget räcker inte för att ange möjliga drivkrafter. Inga ETF-flöden eller likvideringar antas utan stöd i aktuella nyheter.</p>}</details>
 <details className="brief-calendar"><summary><b>Kommande</b><span>{next?eventTime(next)+' · '+next.title:'Inga verifierade datum i urvalet'}</span></summary><Upcoming now={now} coins={visible.map(q=>q.symbol)}/></details>
 </section>;
}
