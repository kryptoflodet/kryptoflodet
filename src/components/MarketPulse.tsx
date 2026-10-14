import type {MarketData} from '../lib/market';
import {metricFresh,pulseReading} from '../lib/pulse';
import {percent} from './MarketBrief';
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

export default function MarketPulse({context,market,now}:{context:MarketContext;market:MarketData;now:number}){
 const reading=pulseReading(context,market,now);
 const global=context.market;
 const stamp=(at:string|null)=>at?new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}).format(new Date(at)):'saknas';
 const compact=(v:number|null|undefined)=>v==null?'—':new Intl.NumberFormat('sv-SE',{notation:'compact',maximumFractionDigits:2}).format(v)+' USD';
 const fear=context.fearGreed.value;
 const alt=context.altcoinSeason.value;
 const fearLabel=fearName(context.fearGreed.classification,fear);
 const altLabel=altcoinSeasonLabel(alt);

 return <section className="market-pulse" aria-label="Marknadspuls">
  <div className="pulse-head"><h2>Pulsen just nu</h2><span>24h · USD</span></div>
  <div className="pulse-overview"><div className="pulse-score"><span>MARKNADSPULS</span><b>{reading.score??'—'}<small>/100</small></b><strong>{reading.label}</strong></div><div className="pulse-key-facts"><div><span>Totalmarknad 24h</span><b className={reading.total===null?'':reading.total>=0?'up':'down'}>{percent(global.marketCapChange24h)}</b></div><div><span>BTC-dominans</span><b>{global.btcDominance===null?'—':global.btcDominance.toLocaleString('sv-SE',{maximumFractionDigits:1})+' %'}</b></div><div><span>Totalt marknadsvärde</span><b>{compact(global.totalMarketCapUsd)}</b></div><div><span>Handelsvolym 24h</span><b>{compact(global.volume24hUsd)}</b></div></div></div>
  <p className="pulse-freshness">Globala data: {stamp(global.observedAt)} svensk tid{!reading.globalFresh?' · Fördröjt eller saknas':''}.</p>
  <details className="pulse-details"><summary>Sentiment, index och metodik <span>Fear &amp; Greed {fear??'—'} · Altcoin Season {alt??'—'}</span></summary>
  <div className="pulse-grid">
   <section className="sentiment-card" aria-labelledby="fear-greed-title">
    <div className="pulse-card-heading"><span id="fear-greed-title">RÄDSLA OCH GIRIGHET</span></div>
    <div className="fear-reading"><b>{fear===null?'—':fear}<small>/100</small></b><span>{fearLabel}</span></div>
    <div className="mood-meter" role="meter" aria-label="Index för rädsla och girighet" aria-valuemin={0} aria-valuemax={100} aria-valuenow={fear??undefined} aria-valuetext={fear===null?'Index saknas':`${fear} av 100, ${fearLabel.toLocaleLowerCase('sv')}`}><div className="mood-gradient"/>{fear!==null&&<span className="mood-needle" style={{left:`${Math.max(2,Math.min(98,fear))}%`}}/>}</div>
    <div className="mood-labels">{moodStops.map(label=><span key={label}>{label}</span>)}</div>
   </section>
   <section className="altseason-card" aria-labelledby="altseason-title">
    <div className="pulse-card-heading"><span id="altseason-title">ALTCOIN-SÄSONG</span></div>
    <div className="altseason-score"><b>{alt===null?'—':alt}<small>/100</small></b><span>{altLabel}</span></div>
    <div className="altseason-meter" role="meter" aria-label="Altcoin-säsongsindex" aria-valuemin={0} aria-valuemax={100} aria-valuenow={alt??undefined} aria-valuetext={alt===null?'Index saknas':`${alt} av 100, ${altLabel.toLocaleLowerCase('sv')}`}><div className="altseason-zones"><i/><i/><i/></div>{alt!==null&&<span className="altseason-needle" style={{left:`${Math.max(2,Math.min(98,alt))}%`}}/>}</div>
    <div className="altseason-labels"><span>BITCOIN-SÄSONG</span><span>NEUTRAL</span><span>ALTCOIN-SÄSONG</span></div>
   </section>
  </div>
  <div className="pulse-method"><h3>Så beräknas marknadspulsen</h3><p>50 % Fear &amp; Greed + 25 % Bitcoins dygnsrörelse + 25 % totalmarknadens dygnsrörelse. Rörelse omvandlas till 0–100 med 50 + förändring i procent × 5, begränsat till 0–100. Resultatet avrundas. Alla tre faktorer krävs; saknade eller för gamla data ger inget värde. Globaldata får vara högst 2 timmar gamla, Bitcoin-kursen 10 minuter (eller rörelsen från färska globaldata) och Fear &amp; Greed 36 timmar.</p><p>0–20 extremt negativ · 21–40 negativ · 41–60 neutral · 61–80 positiv · 81–100 extremt positiv. Detta beskriver momentum och sentiment, inte ett köp- eller säljråd. Dominans och Altcoin Season visas separat och ingår inte i poängen.</p><p><a href="https://www.coingecko.com/" target="_blank" rel="noopener noreferrer">CoinGecko ↗</a> · <a href="https://alternative.me/crypto/fear-and-greed-index/" target="_blank" rel="noopener noreferrer">Alternative.me ↗</a>: Bitcoin-baserat sentiment, observation {stamp(context.fearGreed.observedAt)}{!metricFresh(context.fearGreed,36*3600_000,now)?' · Fördröjt eller saknas':''}.</p><p><a href={context.altcoinSeason.source==='BlockchainCenter'?'https://www.blockchaincenter.net/altcoin-season-index/':'https://coinmarketcap.com/charts/altcoin-season-index/'} target="_blank" rel="noopener noreferrer">{context.altcoinSeason.source||'Altcoin Season'} ↗</a>: observation {stamp(context.altcoinSeason.observedAt)}{!metricFresh(context.altcoinSeason,48*3600_000,now)?' · Fördröjt eller saknas':''}. Leverantörernas index kan ha olika urval.</p></div>
  </details>
 </section>;
}
