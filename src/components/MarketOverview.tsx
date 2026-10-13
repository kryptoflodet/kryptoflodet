import {useMemo,useState} from 'react';
import {ChartNoAxesCombined,ChevronDown,Info,Search,SlidersHorizontal} from 'lucide-react';
import {TOP_MARKET_COUNT,type LiveQuote,type MarketData} from '@/lib/market';
import {sortMarketQuotes,toggleHiddenSymbol,type MarketSort} from '@/lib/market-preferences';

const marks:Record<string,string>={BTC:'₿',ETH:'Ξ',SOL:'≋',SUI:'◈',XRP:'×',HBAR:'ℏ',ONDO:'◎',ADA:'₳',DOGE:'Ð',XLM:'✦',AVAX:'▲',LINK:'⬡',BNB:'◇',HYPE:'H',LTC:'Ł'};
const sortOptions:{value:MarketSort;label:string}[]=[{value:'rank',label:'Börsvärde · rankordning'},{value:'change-high',label:'24 h · största uppgång'},{value:'change-low',label:'24 h · största nedgång'},{value:'cap-high',label:'Marknadsvärde · högst först'},{value:'cap-low',label:'Marknadsvärde · lägst först'},{value:'volume-high',label:'Handelsvolym · störst först'},{value:'volume-low',label:'Handelsvolym · minst först'},{value:'price-high',label:'Pris · högst först'},{value:'price-low',label:'Pris · lägst först'},{value:'name',label:'Namn · A–Ö'}];
function formatPrice(value:number|null,currency:string):string{if(value===null)return '—';const digits=value>=10?2:value>=1?4:value>=0.01?6:value>=0.0001?8:10;return new Intl.NumberFormat('sv-SE',{style:'currency',currency,maximumFractionDigits:digits}).format(value);}
function formatChange(value:number|null):string{return value===null?'—':`${value>=0?'+':''}${value.toLocaleString('sv-SE',{minimumFractionDigits:2,maximumFractionDigits:2})}%`;}
function CoinMark({quote}:{quote:LiveQuote}){return <span className={`coin c-${quote.symbol}`} aria-hidden="true">{marks[quote.symbol]||quote.symbol.slice(0,1)}</span>;}

export default function MarketOverview({marketData,currency,marketStatus,marketTime,hiddenSymbols,onHiddenSymbolsChange,onCoin}:{marketData:MarketData;currency:string;marketStatus:string;marketTime:string;hiddenSymbols:string[];onHiddenSymbolsChange:(symbols:string[])=>void;onCoin:(symbol:string)=>void}){
 const {quotes}=marketData;const [sort,setSort]=useState<MarketSort>('rank');const [query,setQuery]=useState('');
 const availableSymbols=useMemo(()=>new Set(quotes.map(q=>q.symbol)),[quotes]);const selectedCount=quotes.filter(q=>!hiddenSymbols.includes(q.symbol)).length;
 const visible=useMemo(()=>sortMarketQuotes(quotes.filter(q=>!hiddenSymbols.includes(q.symbol)),sort,currency),[quotes,hiddenSymbols,sort,currency]);
 const chooser=useMemo(()=>quotes.filter(q=>!query||q.name.toLocaleLowerCase('sv').includes(query.toLocaleLowerCase('sv'))||q.symbol.toLowerCase().includes(query.toLowerCase())).sort((a,b)=>(a.marketCapRank??Infinity)-(b.marketCapRank??Infinity)),[quotes,query]);
 const priceChange=(q:LiveQuote)=>currency==='SEK'?q.changeSek24h:q.change24h;const priceValue=(q:LiveQuote)=>currency==='SEK'?q.priceSek:q.price;
 return <section className="side-panel market-panel" aria-labelledby="market-overview-title">
  <div className="panel-heading"><h2 id="market-overview-title"><ChartNoAxesCombined size={17}/>Marknadsöversikt</h2><span className="subtle-label">{marketStatus} · {currency}</span></div>
  <div className="market-controls">
   <label className="market-sort"><span>Sortera</span><select value={sort} onChange={event=>setSort(event.target.value as MarketSort)} aria-label="Sortera kryptovalutor">{sortOptions.map(option=><option key={option.value} value={option.value}>{option.label}</option>)}</select><ChevronDown size={13}/></label>
   <details className="market-selection"><summary aria-label={`Välj vilka valutor som visas. ${selectedCount} valda`}><SlidersHorizontal size={14}/>Urval <b>{selectedCount}/{quotes.length}</b></summary>
    <div className="market-selection-panel"><div className="market-selection-title"><b>Visa i översikten</b><div><button type="button" onClick={()=>onHiddenSymbolsChange([])}>Visa alla</button><button type="button" onClick={()=>onHiddenSymbolsChange([...availableSymbols])}>Dölj alla</button></div></div>
     <label className="market-selection-search"><Search size={14}/><input value={query} onChange={event=>setQuery(event.target.value)} placeholder="Sök valuta" aria-label="Sök i topp 50"/></label>
     <div className="market-selection-list">{chooser.map(q=><label className="market-selection-option" key={q.id}><input type="checkbox" checked={!hiddenSymbols.includes(q.symbol)} onChange={event=>onHiddenSymbolsChange(toggleHiddenSymbol(hiddenSymbols,q.symbol,!event.target.checked))}/><span className="market-option-rank">#{q.marketCapRank??'—'}</span><CoinMark quote={q}/><span className="market-option-name"><b>{q.name}</b><small>{q.symbol}</small></span></label>)}</div>
     {!chooser.length&&<p className="market-selection-empty">Ingen valuta matchar sökningen.</p>}
    </div>
   </details>
  </div>
  <div className="market-table-heading"><span>TILLGÅNG · RANK</span><span>PRIS · 24 H</span></div>
  <div className="market-table-scroll" aria-label="Valutor i marknadsöversikten">{visible.map(q=><button className="market-row" onClick={()=>onCoin(q.symbol)} key={q.id} aria-label={`Visa diagram för ${q.name}`}><span className="market-rank">{q.marketCapRank?`#${q.marketCapRank}`:'—'}</span><CoinMark quote={q}/><span className="market-name"><b>{q.name}</b><small>{q.symbol}</small></span><span className="market-values"><b>{formatPrice(priceValue(q),currency)}</b><small className={(priceChange(q)??0)>=0?'up':'down'}>{formatChange(priceChange(q))}</small></span></button>)}
   {!visible.length&&<div className="market-empty">Inga valutor visas. Välj vilka du vill se under <b>Urval</b>.</div>}
  </div>
  <div className="market-foot"><Info size={12}/><span>CoinGecko · {quotes.length} av topp {TOP_MARKET_COUNT} efter marknadsvärde · {marketTime}{quotes.length<TOP_MARKET_COUNT?` · väntar på komplett topp ${TOP_MARKET_COUNT}`:''}</span></div>
 </section>;
}
