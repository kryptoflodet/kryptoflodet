import type {MarketContext} from '../lib/market-context';
import {altcoinSeasonLabel,calculateSentiment,isMetricStale,sentimentLabel} from '../lib/market-context';
import {Activity,ArrowDownRight,ArrowUpRight,BarChart3,Bitcoin,Globe2,ShieldAlert} from 'lucide-react';

const moodStops=['EXTREMT RÄDD','RÄDD','NEUTRAL','GIRIG','EXTREMT GIRIG'];
function percent(value:number|null,digits=2){return value===null?'—':`${value>0?'+':''}${value.toLocaleString('sv-SE',{minimumFractionDigits:digits,maximumFractionDigits:digits})}%`;}
function compactDate(value:string|null){return value?new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',hour:'2-digit',minute:'2-digit'}).format(new Date(value)):'—';}
function fearName(value:string|null){if(!value)return 'Saknas';const map:Record<string,string>={'Extreme Fear':'Extrem rädsla',Fear:'Rädsla',Neutral:'Neutral',Greed:'Girighet','Extreme Greed':'Extrem girighet'};return map[value]||value;}
function movementIcon(value:number|null){if(value===null)return <Activity size={15}/>;return value>=0?<ArrowUpRight size={15}/>:<ArrowDownRight size={15}/>;}

export default function MarketPulse({context}:{context:MarketContext}){
 const score=calculateSentiment(context);const mood=sentimentLabel(score);const alt=context.altcoinSeason.value;const altLabel=altcoinSeasonLabel(alt);
 const now=Date.now();const marketStale=isMetricStale(context.market.checkedAt,2*60*60_000,now);const fearStale=isMetricStale(context.fearGreed.checkedAt,36*60*60_000,now);const altStale=isMetricStale(context.altcoinSeason.checkedAt,3*60*60_000,now);
 const comparison=context.market.btcChange24h===null||context.market.ethChange24h===null?null:context.market.btcChange24h-context.market.ethChange24h;
 const freshest=[context.fearGreed.checkedAt,context.market.checkedAt,context.altcoinSeason.checkedAt].filter((x):x is string=>!!x).sort().at(-1)||null;
 return <section className="market-pulse" aria-labelledby="market-pulse-title">
  <div className="market-pulse-heading"><div><span className="pulse-kicker"><Activity size={14}/> MARKNADENS KÄNSLOR</span><h2 id="market-pulse-title">Läs av marknaden</h2></div><span className={'pulse-update '+(!marketStale||!fearStale||!altStale?'is-current':'is-stale')}><i/>{freshest?`Senast kontrollerad ${compactDate(freshest)}`:'Väntar på marknadsdata'}</span></div>
  <div className="pulse-grid">
   <div className="sentiment-card">
    <div className="pulse-card-heading"><span><ShieldAlert size={16}/> SAMMANSATT SENTIMENT</span><b>{score===null?'—':score}<small>/100</small></b></div>
    <div className="mood-result">{mood}</div>
    <div className="mood-meter" role="meter" aria-label="Sammansatt rädsla och girighet" aria-valuemin={0} aria-valuemax={100} aria-valuenow={score??undefined} aria-valuetext={score===null?'Data saknas':`${score} av 100, ${mood.toLocaleLowerCase('sv')}`}>
     <div className="mood-gradient"/><span className="mood-needle" style={{left:`${score??50}%`}}/>
    </div>
    <div className="mood-labels">{moodStops.map(label=><span key={label}>{label}</span>)}</div>
    <p className="pulse-method">Viktat eget index: Fear &amp; Greed 50% · BTC 24 h 25% · total marknad 24 h 25%. Rörelser skalas till 0–100 vid ±10%.</p>
   </div>
   <div className="market-facts" aria-label="Marknadsdata">
    <div className="pulse-fact"><span>FEAR &amp; GREED <a href="https://alternative.me/crypto/fear-and-greed-index/" target="_blank" rel="noopener noreferrer">↗</a></span><b>{context.fearGreed.value===null?'—':`${context.fearGreed.value}/100`}</b><small className={fearStale?'fact-stale':''}>{fearName(context.fearGreed.classification)}{fearStale&&context.fearGreed.value!==null?' · fördröjt':''}</small></div>
    <div className="pulse-fact"><span><Bitcoin size={13}/> BTC · 24 H</span><b className={context.market.btcChange24h===null?'':context.market.btcChange24h>=0?'fact-up':'fact-down'}>{percent(context.market.btcChange24h)}{movementIcon(context.market.btcChange24h)}</b><small>Bitcoinrörelse</small></div>
    <div className="pulse-fact"><span><Globe2 size={13}/> HELA MARKNADEN · 24 H</span><b className={context.market.marketCapChange24h===null?'':context.market.marketCapChange24h>=0?'fact-up':'fact-down'}>{percent(context.market.marketCapChange24h)}{movementIcon(context.market.marketCapChange24h)}</b><small className={marketStale?'fact-stale':''}>Total marknadsvärdering{marketStale?' · fördröjt':''}</small></div>
    <div className="pulse-fact"><span><BarChart3 size={13}/> MARKNADS­DOMINANS</span><b><em>BTC</em> {percent(context.market.btcDominance,1)} <em>ETH</em> {percent(context.market.ethDominance,1)}</b><small>Andel av kryptomarknaden</small></div>
    <div className="pulse-fact"><span>BTC JÄMFÖRT MED ETH · 24 H</span><b className={comparison===null?'':comparison>=0?'fact-up':'fact-down'}>{comparison===null?'—':`${comparison>0?'BTC leder':'ETH leder'} ${Math.abs(comparison).toLocaleString('sv-SE',{minimumFractionDigits:2,maximumFractionDigits:2})} pp`}</b><small>Skillnad i procentenheter</small></div>
   </div>
  </div>
  <div className="altseason-card">
   <div className="altseason-heading"><div><span><Activity size={15}/> ALTCOIN SEASON INDEX <a href="https://coinmarketcap.com/charts/altcoin-season-index/" target="_blank" rel="noopener noreferrer">Källa ↗</a></span><small>Andel av de 100 största altcoinen som slagit Bitcoin senaste 90 dagarna</small></div><div className="altseason-score"><b>{alt===null?'—':alt}</b><span>/100 · {altLabel}</span></div></div>
   <div className="altseason-meter" role="meter" aria-label="Altcoin Season Index" aria-valuemin={0} aria-valuemax={100} aria-valuenow={alt??undefined} aria-valuetext={alt===null?'Index saknas':`${alt} av 100, ${altLabel.toLocaleLowerCase('sv')}`}>
    <div className="altseason-zones"><i/><i/><i/></div>{alt!==null&&<span className="altseason-needle" style={{left:`${alt}%`}}/>}
   </div>
   <div className="altseason-labels"><span>0 · BITCOIN SEASON</span><span>26–74 · NEUTRAL</span><span>75–100 · ALTCOIN SEASON</span></div>
   <small className={'altseason-status '+(altStale?'fact-stale':'')}>{altStale&&alt!==null?'Senast lagrat index visas. ':''}Källa uppdateras automatiskt · {compactDate(context.altcoinSeason.checkedAt)} · ingen prognos eller köp-/säljrekommendation.</small>
  </div>
 </section>;
}
