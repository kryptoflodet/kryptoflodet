import type {MarketContext} from '../lib/market-context';
import {altcoinSeasonLabel} from '../lib/market-context';

const moodStops=['EXTREMT RÄDD','RÄDD','NEUTRAL','GIRIG','EXTREMT GIRIG'];

function fearName(value:string|null):string{
 if(!value)return 'Väntar på index';
 const map:Record<string,string>={'Extreme Fear':'Extrem rädsla',Fear:'Rädsla',Neutral:'Neutral',Greed:'Girighet','Extreme Greed':'Extrem girighet'};
 return map[value]||value;
}

function formatPercent(value:number|null,digits=2):string{
 return value===null?'—':`${value>0?'+':''}${value.toLocaleString('sv-SE',{minimumFractionDigits:digits,maximumFractionDigits:digits})}%`;
}

function formatDominance(value:number|null):string{
 return value===null?'—':`${value.toLocaleString('sv-SE',{minimumFractionDigits:1,maximumFractionDigits:1})}%`;
}

export default function MarketPulse({context}:{context:MarketContext}){
 const fear=context.fearGreed.value;
 const alt=context.altcoinSeason.value;
 const btcChange=context.market.btcChange24h;
 const ethChange=context.market.ethChange24h;
 const relativeChange=btcChange===null||ethChange===null?null:btcChange-ethChange;
 const marketChange=context.market.marketCapChange24h;
 const marketTrend=marketChange===null?'Inväntar data':marketChange>0.25?'Stigande':marketChange< -0.25?'Fallande':'Sidledes';
 const trendClass=marketChange===null?'':marketChange>0.25?'up':marketChange< -0.25?'down':'';

 return <section className="market-pulse" aria-labelledby="market-pulse-title">
  <div className="market-pulse-heading">
   <div>
    <div className="pulse-kicker"><span className="pulse-live-dot" aria-hidden="true"/>MARKNADSPULS</div>
    <h2 id="market-pulse-title">Kryptomarknaden just nu</h2>
   </div>
   <span className="pulse-update"><span className="pulse-update-dot" aria-hidden="true"/>Data uppdateras automatiskt</span>
  </div>
  <div className="pulse-grid">
   <section className="sentiment-card" aria-labelledby="fear-greed-title">
    <div className="pulse-card-heading"><span id="fear-greed-title">FEAR &amp; GREED INDEX</span></div>
    <div className="fear-reading"><b>{fear===null?'—':fear}<small>/100</small></b><span>{fearName(context.fearGreed.classification)}</span></div>
    <div className="mood-meter" role="meter" aria-label="Fear and Greed Index" aria-valuemin={0} aria-valuemax={100} aria-valuenow={fear??undefined} aria-valuetext={fear===null?'Index saknas':`${fear} av 100, ${fearName(context.fearGreed.classification).toLocaleLowerCase('sv')}`}><div className="mood-gradient"/>{fear!==null&&<span className="mood-needle" style={{left:`${Math.max(2,Math.min(98,fear))}%`}}/>}</div>
    <div className="mood-labels">{moodStops.map(label=><span key={label}>{label}</span>)}</div>
   </section>
   <section className="altseason-card" aria-labelledby="altseason-title">
    <div className="pulse-card-heading"><span id="altseason-title">ALTCOIN SEASON INDEX</span></div>
    <div className="altseason-score"><b>{alt===null?'—':alt}<small>/100</small></b><span>{altcoinSeasonLabel(alt)}</span></div>
    <div className="altseason-meter" role="meter" aria-label="Altcoin Season Index" aria-valuemin={0} aria-valuemax={100} aria-valuenow={alt??undefined} aria-valuetext={alt===null?'Index saknas':`${alt} av 100, ${altcoinSeasonLabel(alt).toLocaleLowerCase('sv')}`}><div className="altseason-zones"><i/><i/><i/></div>{alt!==null&&<span className="altseason-needle" style={{left:`${Math.max(2,Math.min(98,alt))}%`}}/>}</div>
    <div className="altseason-labels"><span>BITCOIN SEASON</span><span>NEUTRAL</span><span>ALTCOIN SEASON</span></div>
   </section>
  </div>
  <div className="market-pulse-facts" role="group" aria-label="Marknadens nyckeltal">
   <div className="pulse-fact"><span>BTC-DOMINANS</span><b>{formatDominance(context.market.btcDominance)}</b><small>Bitcoins andel av marknaden</small></div>
   <div className="pulse-fact"><span>BTC VS ETH · 24 H</span><div className="pulse-comparison"><b className={(btcChange??0)>=0?'up':'down'}>BTC {formatPercent(btcChange)}</b><b className={(ethChange??0)>=0?'up':'down'}>ETH {formatPercent(ethChange)}</b></div><small>{relativeChange===null?'Jämförelse saknas':relativeChange>0.05?`BTC leder med ${formatPercent(relativeChange)}`:relativeChange< -0.05?`ETH leder med ${formatPercent(Math.abs(relativeChange))}`:'De rör sig ungefär lika'}</small></div>
   <div className="pulse-fact"><span>MARKNADSTREND · 24 H</span><b className={trendClass}>{marketTrend}{marketChange===null?'':` · ${formatPercent(marketChange)}`}</b><small>Total kryptomarknad</small></div>
  </div>
 </section>;
}
