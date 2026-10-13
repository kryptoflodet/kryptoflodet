import type {MarketContext} from '../lib/market-context';
import {altcoinSeasonLabel} from '../lib/market-context';

const moodStops=['EXTREMT RÄDD','RÄDD','NEUTRAL','GIRIG','EXTREMT GIRIG'];

function fearName(value:string|null):string{
 if(!value)return 'Väntar på index';
 const map:Record<string,string>={'Extreme Fear':'Extrem rädsla',Fear:'Rädsla',Neutral:'Neutral',Greed:'Girighet','Extreme Greed':'Extrem girighet'};
 return map[value]||value;
}

export default function MarketPulse({context}:{context:MarketContext}){
 const fear=context.fearGreed.value;
 const alt=context.altcoinSeason.value;
 return <section className="market-pulse" aria-label="Fear & Greed och Altcoin Season">
  <div className="pulse-grid">
   <section className="sentiment-card" aria-labelledby="fear-greed-title">
    <div className="pulse-card-heading"><span id="fear-greed-title">FEAR &amp; GREED INDEX</span></div>
    <div className="fear-reading"><b>{fear===null?'—':fear}<small>/100</small></b><span>{fearName(context.fearGreed.classification)}</span></div>
    <div className="mood-meter" role="meter" aria-label="Fear and Greed Index" aria-valuemin={0} aria-valuemax={100} aria-valuenow={fear??undefined} aria-valuetext={fear===null?'Index saknas':`${fear} av 100, ${fearName(context.fearGreed.classification).toLocaleLowerCase('sv')}`}><div className="mood-gradient"/>{fear!==null&&<span className="mood-needle" style={{left:`${fear}%`}}/>}</div>
    <div className="mood-labels">{moodStops.map(label=><span key={label}>{label}</span>)}</div>
   </section>
   <section className="altseason-card" aria-labelledby="altseason-title">
    <div className="pulse-card-heading"><span id="altseason-title">ALTCOIN SEASON INDEX</span></div>
    <div className="altseason-score"><b>{alt===null?'—':alt}<small>/100</small></b><span>{altcoinSeasonLabel(alt)}</span></div>
    <div className="altseason-meter" role="meter" aria-label="Altcoin Season Index" aria-valuemin={0} aria-valuemax={100} aria-valuenow={alt??undefined} aria-valuetext={alt===null?'Index saknas':`${alt} av 100, ${altcoinSeasonLabel(alt).toLocaleLowerCase('sv')}`}><div className="altseason-zones"><i/><i/><i/></div>{alt!==null&&<span className="altseason-needle" style={{left:`${alt}%`}}/>}</div>
    <div className="altseason-labels"><span>BITCOIN SEASON</span><span>NEUTRAL</span><span>ALTCOIN SEASON</span></div>
   </section>
  </div>
 </section>;
}
