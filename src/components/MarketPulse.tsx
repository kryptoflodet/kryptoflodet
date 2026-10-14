import type {MarketContext} from '../lib/market-context';
import {altcoinSeasonLabel} from '../lib/market-context';

const moodStops=['EXTREM RÄDSLA','RÄDSLA','NEUTRAL','GIRIGHET','EXTREM GIRIGHET'];

function fearName(value:string|null,score:number|null):string{
 const map:Record<string,string>={'extreme fear':'Extrem rädsla',fear:'Rädsla',neutral:'Neutral',greed:'Girighet','extreme greed':'Extrem girighet'};
 const translated=value?.trim().toLocaleLowerCase('en-US');
 if(translated&&map[translated])return map[translated];
 if(score===null)return 'Väntar på index';
 if(score<=24)return 'Extrem rädsla';
 if(score<=44)return 'Rädsla';
 if(score<=55)return 'Neutral';
 if(score<=74)return 'Girighet';
 return 'Extrem girighet';
}

export default function MarketPulse({context}:{context:MarketContext}){
 const fear=context.fearGreed.value;
 const alt=context.altcoinSeason.value;
 const fearLabel=fearName(context.fearGreed.classification,fear);
 const altLabel=altcoinSeasonLabel(alt);

 return <section className="market-pulse" aria-label="Marknadspuls">
  <div className="pulse-grid">
   <section className="sentiment-card" aria-labelledby="fear-greed-title">
    <div className="pulse-card-heading"><span id="fear-greed-title">FEAR AND GREED INDEX</span></div>
    <div className="fear-reading"><b>{fear===null?'—':fear}<small>/100</small></b><span>{fearLabel}</span></div>
    <div className="mood-meter" role="meter" aria-label="Fear and Greed Index" aria-valuemin={0} aria-valuemax={100} aria-valuenow={fear??undefined} aria-valuetext={fear===null?'Index saknas':`${fear} av 100, ${fearLabel.toLocaleLowerCase('sv')}`}><div className="mood-gradient"/>{fear!==null&&<span className="mood-needle" style={{left:`${Math.max(2,Math.min(98,fear))}%`}}/>}</div>
    <div className="mood-labels">{moodStops.map(label=><span key={label}>{label}</span>)}</div>
   </section>
   <section className="altseason-card" aria-labelledby="altseason-title">
    <div className="pulse-card-heading"><span id="altseason-title">ALTCOIN SEASON</span></div>
    <div className="altseason-score"><b>{alt===null?'—':alt}<small>/100</small></b><span>{altLabel}</span></div>
    <div className="altseason-meter" role="meter" aria-label="Altcoin Season" aria-valuemin={0} aria-valuemax={100} aria-valuenow={alt??undefined} aria-valuetext={alt===null?'Index saknas':`${alt} av 100, ${altLabel.toLocaleLowerCase('sv')}`}><div className="altseason-zones"><i/><i/><i/></div>{alt!==null&&<span className="altseason-needle" style={{left:`${Math.max(2,Math.min(98,alt))}%`}}/>}</div>
    <div className="altseason-labels"><span>BITCOIN SEASON</span><span>NEUTRAL</span><span>ALTCOIN SEASON</span></div>
   </section>
  </div>
 </section>;
}
