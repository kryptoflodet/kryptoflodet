import type {MarketContext} from '../lib/market-context';
import {altcoinSeasonLabel,calculateSentiment,isMetricStale,sentimentLabel} from '../lib/market-context';
import {Activity,ArrowDownRight,ArrowUpRight,BarChart3,Bitcoin,Globe2,ShieldAlert} from 'lucide-react';

const moodStops=['EXTREMT RÄDD','RÄDD','NEUTRAL','GIRIG','EXTREMT GIRIG'];
function percent(value:number|null){return value===null?'—':`${value>0?'+':''}${value.toLocaleString('sv-SE',{minimumFractionDigits:2,maximumFractionDigits:2})}%`;}
function sharePercent(value:number|null){return value===null?'—':`${value.toLocaleString('sv-SE',{minimumFractionDigits:1,maximumFractionDigits:1})}%`;}
function compactDate(value:string|null){return value?new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',hour:'2-digit',minute:'2-digit'}).format(new Date(value)):'—';}
function fearName(value:string|null){if(!value)return 'Väntar på index';const map:Record<string,string>={'Extreme Fear':'Extrem rädsla',Fear:'Rädsla',Neutral:'Neutral',Greed:'Girighet','Extreme Greed':'Extrem girighet'};return map[value]||value;}
function movementIcon(value:number|null){if(value===null)return <Activity size={14}/>;return value>=0?<ArrowUpRight size={14}/>:<ArrowDownRight size={14}/>;}

export default function MarketPulse({context}:{context:MarketContext}){
 const fear=context.fearGreed.value;const alt=context.altcoinSeason.value;const combined=calculateSentiment(context);
 const marketStale=isMetricStale(context.market.checkedAt,2*60*60_000);const fearStale=isMetricStale(context.fearGreed.checkedAt,36*60*60_000);const altStale=isMetricStale(context.altcoinSeason.checkedAt,3*60*60_000);
 const comparison=context.market.btcChange24h===null||context.market.ethChange24h===null?null:context.market.btcChange24h-context.market.ethChange24h;
 const freshest=[context.fearGreed.checkedAt,context.market.checkedAt,context.altcoinSeason.checkedAt].filter((x):x is string=>!!x).sort().at(-1)||null;
 const current=!fearStale&&!marketStale&&!altStale;
 const altSource=context.altcoinSeason.source==='BlockchainCenter'?'https://www.blockchaincenter.net/altcoin-season-index/':'https://coinmarketcap.com/charts/altcoin-season-index/';
 return <section className="market-pulse" aria-labelledby="market-pulse-title">
  <div className="market-pulse-heading"><div><span className="pulse-kicker"><Activity size={14}/> MARKNADENS KÄNSLOR</span><h2 id="market-pulse-title">Fear &amp; Greed och altcoin season</h2></div><span className={'pulse-update '+(current?'is-current':'is-stale')}><i/>{freshest?`Senast kontrollerad ${compactDate(freshest)}`:'Väntar på marknadsdata'}</span></div>
  <div className="pulse-grid">
   <section className="sentiment-card" aria-labelledby="fear-greed-title">
    <div className="pulse-card-heading"><span id="fear-greed-title"><ShieldAlert size={16}/> FEAR &amp; GREED INDEX <a href="https://alternative.me/crypto/fear-and-greed-index/" target="_blank" rel="noopener noreferrer">Källa ↗</a></span><span className={'pulse-fresh '+(fearStale?'fact-stale':'')}>{fearStale&&fear!==null?'FÖRDRÖJT':''}</span></div>
    <div className="fear-reading"><b>{fear===null?'—':fear}<small>/100</small></b><span>{fearName(context.fearGreed.classification)}</span></div>
    <div className="mood-meter" role="meter" aria-label="Fear and Greed Index" aria-valuemin={0} aria-valuemax={100} aria-valuenow={fear??undefined} aria-valuetext={fear===null?'Index saknas':`${fear} av 100, ${fearName(context.fearGreed.classification).toLocaleLowerCase('sv')}`}><div className="mood-gradient"/>{fear!==null&&<span className="mood-needle" style={{left:`${fear}%`}}/>}</div>
    <div className="mood-labels">{moodStops.map(label=><span key={label}>{label}</span>)}</div>
    <div className="market-facts" aria-label="Marknadstrend och dominans">
     <div className="pulse-fact"><span><Bitcoin size={13}/> BTC · 24 H</span><b className={context.market.btcChange24h===null?'':context.market.btcChange24h>=0?'fact-up':'fact-down'}>{percent(context.market.btcChange24h)}{movementIcon(context.market.btcChange24h)}</b></div>
     <div className="pulse-fact"><span><Globe2 size={13}/> MARKNADEN · 24 H</span><b className={context.market.marketCapChange24h===null?'':context.market.marketCapChange24h>=0?'fact-up':'fact-down'}>{percent(context.market.marketCapChange24h)}{movementIcon(context.market.marketCapChange24h)}</b></div>
     <div className="pulse-fact"><span><BarChart3 size={13}/> DOMINANS · BTC / ETH</span><b><em>{sharePercent(context.market.btcDominance)}</em> / <em>{sharePercent(context.market.ethDominance)}</em></b></div>
     <div className="pulse-fact"><span>BTC MOT ETH · 24 H</span><b className={comparison===null?'':comparison>=0?'fact-up':'fact-down'}>{comparison===null?'—':`${comparison>=0?'BTC leder':'ETH leder'} ${Math.abs(comparison).toLocaleString('sv-SE',{minimumFractionDigits:2,maximumFractionDigits:2})} pp`}</b></div>
    </div>
    <div className="pulse-summary"><span>SAMMANSATT MARKNADSBILD</span><b>{combined===null?'—':`${combined}/100 · ${sentimentLabel(combined)}`}</b><small>{marketStale?'BTC- och marknadstrenden är fördröjd. ':''}Väger Fear &amp; Greed, BTC-rörelse och hela marknadens 24 h-trend.</small></div>
   </section>
   <section className="altseason-card" aria-labelledby="altseason-title">
    <div className="pulse-card-heading"><span id="altseason-title"><Activity size={16}/> ALTCOIN SEASON INDEX <a href={altSource} target="_blank" rel="noopener noreferrer">Källa ↗</a></span><span className={'pulse-fresh '+(altStale?'fact-stale':'')}>{altStale&&alt!==null?'FÖRDRÖJT':''}</span></div>
    <div className="altseason-score"><b>{alt===null?'—':alt}<small>/100</small></b><span>{altcoinSeasonLabel(alt)}</span></div>
    <div className="altseason-meter" role="meter" aria-label="Altcoin Season Index" aria-valuemin={0} aria-valuemax={100} aria-valuenow={alt??undefined} aria-valuetext={alt===null?'Index saknas':`${alt} av 100, ${altcoinSeasonLabel(alt).toLocaleLowerCase('sv')}`}><div className="altseason-zones"><i/><i/><i/></div>{alt!==null&&<span className="altseason-needle" style={{left:`${alt}%`}}/>}</div>
    <div className="altseason-labels"><span>BITCOIN SEASON</span><span>NEUTRAL</span><span>ALTCOIN SEASON</span></div>
    <div className="altseason-description"><b>När börjar altcoin season?</b><p>{context.altcoinSeason.source==='BlockchainCenter'?'Indexet följer hur många av de 50 största altcoinen som slagit Bitcoin under de senaste 90 dagarna.':'CoinMarketCaps index jämför de största altcoinen med Bitcoin under de senaste 90 dagarna.'} Från 75 räknas det som altcoin season.</p></div>
    <small className={'altseason-status '+(altStale?'fact-stale':'')}>{altStale&&alt!==null?'Senast sparade index visas. ':''}Senast kontrollerad {compactDate(context.altcoinSeason.checkedAt)} · indikator, inte prognos.</small>
   </section>
  </div>
 </section>;
}
