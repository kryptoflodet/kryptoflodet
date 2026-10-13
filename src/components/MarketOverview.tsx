import {useMemo,useRef,useState} from 'react';
import type {DragEvent,KeyboardEvent} from 'react';
import {ChartNoAxesCombined,Info,Search,SlidersHorizontal} from 'lucide-react';
import {TOP_MARKET_COUNT,type LiveQuote,type MarketData} from '@/lib/market';
import {MARKET_ORDER_KEY,moveMarketSymbol,normalizeHiddenSymbols,normalizeMarketOrder,toggleHiddenSymbol} from '@/lib/market-preferences';

const marks:Record<string,string>={BTC:'₿',ETH:'Ξ',SOL:'≋',SUI:'◈',XRP:'×',HBAR:'ℏ',ONDO:'◎',ADA:'₳',DOGE:'Ð',XLM:'✦',AVAX:'▲',LINK:'⬡',BNB:'◇',HYPE:'H',LTC:'Ł'};
function formatPrice(value:number|null,currency:string):string{if(value===null)return '—';const digits=value>=10?2:value>=1?4:value>=0.01?6:value>=0.0001?8:10;return new Intl.NumberFormat('sv-SE',{style:'currency',currency,maximumFractionDigits:digits}).format(value);}
function formatChange(value:number|null):string{return value===null?'—':`${value>=0?'+':''}${value.toLocaleString('sv-SE',{minimumFractionDigits:2,maximumFractionDigits:2})}%`;}
function CoinMark({quote}:{quote:LiveQuote}){return <span className={`coin c-${quote.symbol}`} aria-hidden="true">{marks[quote.symbol]||quote.symbol.slice(0,1)}</span>;}
function readSavedOrder():string[]{try{return normalizeHiddenSymbols(JSON.parse(window.localStorage.getItem(MARKET_ORDER_KEY)||'[]'));}catch{return [];}}

export default function MarketOverview({marketData,currency,marketStatus,marketTime,hiddenSymbols,onHiddenSymbolsChange,onCoin}:{marketData:MarketData;currency:string;marketStatus:string;marketTime:string;hiddenSymbols:string[];onHiddenSymbolsChange:(symbols:string[])=>void;onCoin:(symbol:string)=>void}){
 const {quotes}=marketData;const [savedOrder,setSavedOrder]=useState(readSavedOrder);const [draggingSymbol,setDraggingSymbol]=useState<string|null>(null);const [dropIndicator,setDropIndicator]=useState<{symbol:string;after:boolean}|null>(null);const [query,setQuery]=useState('');const draggingRef=useRef<string|null>(null);const ignoreClick=useRef(false);
 const allSymbols=useMemo(()=>quotes.map(q=>q.symbol),[quotes]);const availableSymbols=useMemo(()=>new Set(allSymbols),[allSymbols]);const selectedCount=quotes.filter(q=>!hiddenSymbols.includes(q.symbol)).length;
 const orderedSymbols=useMemo(()=>normalizeMarketOrder(savedOrder,allSymbols),[savedOrder,allSymbols]);const orderPosition=useMemo(()=>new Map(orderedSymbols.map((symbol,index)=>[symbol,index])),[orderedSymbols]);
 const visible=useMemo(()=>quotes.filter(q=>!hiddenSymbols.includes(q.symbol)).sort((a,b)=>(orderPosition.get(a.symbol)??Infinity)-(orderPosition.get(b.symbol)??Infinity)),[quotes,hiddenSymbols,orderPosition]);
 const chooser=useMemo(()=>quotes.filter(q=>!query||q.name.toLocaleLowerCase('sv').includes(query.toLocaleLowerCase('sv'))||q.symbol.toLowerCase().includes(query.toLowerCase())).sort((a,b)=>(a.marketCapRank??Infinity)-(b.marketCapRank??Infinity)),[quotes,query]);
 const priceChange=(q:LiveQuote)=>currency==='SEK'?q.changeSek24h:q.change24h;const priceValue=(q:LiveQuote)=>currency==='SEK'?q.priceSek:q.price;
 function saveOrder(next:string[]){setSavedOrder(next);try{window.localStorage.setItem(MARKET_ORDER_KEY,JSON.stringify(next));}catch{/* Display preferences are optional. */}}
 function handleDragStart(event:DragEvent<HTMLButtonElement>,symbol:string){draggingRef.current=symbol;setDraggingSymbol(symbol);event.dataTransfer.effectAllowed='move';event.dataTransfer.setData('text/plain',symbol);}
 function handleDragOver(event:DragEvent<HTMLButtonElement>,symbol:string){const source=draggingRef.current||event.dataTransfer.getData('text/plain');if(!source||source===symbol)return;event.preventDefault();event.dataTransfer.dropEffect='move';const rect=event.currentTarget.getBoundingClientRect();const after=event.clientY>=rect.top+rect.height/2;setDropIndicator(current=>current?.symbol===symbol&&current.after===after?current:{symbol,after});}
 function handleDrop(event:DragEvent<HTMLButtonElement>,symbol:string){event.preventDefault();const source=event.dataTransfer.getData('text/plain')||draggingRef.current;if(source&&source!==symbol){const rect=event.currentTarget.getBoundingClientRect();const after=event.clientY>=rect.top+rect.height/2;saveOrder(moveMarketSymbol(orderedSymbols,source,symbol,after));ignoreClick.current=true;window.setTimeout(()=>{ignoreClick.current=false;},100);}draggingRef.current=null;setDraggingSymbol(null);setDropIndicator(null);}
 function handleDragEnd(){draggingRef.current=null;setDraggingSymbol(null);setDropIndicator(null);}
 function handleRowKeyDown(event:KeyboardEvent<HTMLButtonElement>,symbol:string){if(!event.altKey||(event.key!=='ArrowUp'&&event.key!=='ArrowDown'))return;const index=orderedSymbols.indexOf(symbol);const direction=event.key==='ArrowDown'?1:-1;const target=orderedSymbols[index+direction];if(!target)return;event.preventDefault();saveOrder(moveMarketSymbol(orderedSymbols,symbol,target,direction>0));}
 return <section className="side-panel market-panel" aria-labelledby="market-overview-title">
  <div className="panel-heading"><h2 id="market-overview-title"><ChartNoAxesCombined size={17}/>Marknadsöversikt</h2><span className="subtle-label">{marketStatus} · {currency}</span></div>
  <div className="market-controls">
   <details className="market-selection"><summary aria-label={`Välj vilka valutor som visas. ${selectedCount} valda`}><SlidersHorizontal size={14}/>Urval <b>{selectedCount}/{quotes.length}</b></summary>
    <div className="market-selection-panel"><div className="market-selection-title"><b>Visa i översikten</b><div><button type="button" onClick={()=>onHiddenSymbolsChange([])}>Visa alla</button><button type="button" onClick={()=>onHiddenSymbolsChange([...availableSymbols])}>Dölj alla</button></div></div>
     <label className="market-selection-search"><Search size={14}/><input value={query} onChange={event=>setQuery(event.target.value)} placeholder="Sök valuta" aria-label="Sök i topp 50"/></label>
     <div className="market-selection-list">{chooser.map(q=><label className="market-selection-option" key={q.id}><input type="checkbox" checked={!hiddenSymbols.includes(q.symbol)} onChange={event=>onHiddenSymbolsChange(toggleHiddenSymbol(hiddenSymbols,q.symbol,!event.target.checked))}/><span className="market-option-rank">#{q.marketCapRank??'—'}</span><CoinMark quote={q}/><span className="market-option-name"><b>{q.name}</b><small>{q.symbol}</small></span></label>)}</div>
     {!chooser.length&&<p className="market-selection-empty">Ingen valuta matchar sökningen.</p>}
    </div>
   </details>
  </div>
  <div className="market-table-heading"><span>TILLGÅNG · RANK</span><span>PRIS · 24 H</span></div>
  <div className="market-table-scroll" aria-label="Valutor i marknadsöversikten">{visible.map(q=>{const isDropTarget=dropIndicator?.symbol===q.symbol;return <button className={`market-row${draggingSymbol===q.symbol?' is-dragging':''}${isDropTarget?` is-drop-${dropIndicator.after?'after':'before'}`:''}`} onClick={()=>{if(ignoreClick.current){ignoreClick.current=false;return;}onCoin(q.symbol);}} onKeyDown={event=>handleRowKeyDown(event,q.symbol)} onDragStart={event=>handleDragStart(event,q.symbol)} onDragOver={event=>handleDragOver(event,q.symbol)} onDrop={event=>handleDrop(event,q.symbol)} onDragEnd={handleDragEnd} draggable aria-keyshortcuts="Alt+ArrowUp Alt+ArrowDown" title="Dra för att ändra ordning" key={q.id} aria-label={`Visa diagram för ${q.name}. Dra för att ändra ordning; Alt+upp eller Alt+ned för att flytta.`}><span className="market-rank">{q.marketCapRank?`#${q.marketCapRank}`:'—'}</span><CoinMark quote={q}/><span className="market-name"><b>{q.name}</b><small>{q.symbol}</small></span><span className="market-values"><b>{formatPrice(priceValue(q),currency)}</b><small className={(priceChange(q)??0)>=0?'up':'down'}>{formatChange(priceChange(q))}</small></span></button>;})}
   {!visible.length&&<div className="market-empty">Inga valutor visas. Välj vilka du vill se under <b>Urval</b>.</div>}
  </div>
  <div className="market-foot"><Info size={12}/><span>CoinGecko · {quotes.length} av topp {TOP_MARKET_COUNT} efter marknadsvärde · {marketTime}{quotes.length<TOP_MARKET_COUNT?` · väntar på komplett topp ${TOP_MARKET_COUNT}`:''}</span></div>
 </section>;
}
