import {useEffect,useRef,useState} from 'react';
import seed from '../../public/data/x.json';
interface XPost{id:string;handle:string;author:string;url:string;publishedAt:string;text:string;coins:string[];categories:string[];kind:string;verified:boolean;media?:{url:string;alt:string}[];}
interface XSource{id:string;name:string;handle:string;connection:string;count:number;message?:string;}
interface XData{generatedAt:string;posts:XPost[];sources:XSource[];}
interface Widgets{widgets:{createTweet:(id:string,node:HTMLElement,options:Record<string,unknown>)=>Promise<HTMLElement|undefined>};}
declare global{interface Window{twttr?:Widgets;}}
let widgetRequest:Promise<Widgets>|undefined;
function widgets(){
 if(window.twttr?.widgets)return Promise.resolve(window.twttr);
 if(!widgetRequest)widgetRequest=new Promise<Widgets>((resolve,reject)=>{
  const script=document.createElement('script');script.src='https://platform.twitter.com/widgets.js';script.async=true;
  const timer=window.setTimeout(()=>reject(new Error('X timeout')),12000);
  script.onload=()=>{clearTimeout(timer);window.twttr?.widgets?resolve(window.twttr):reject(new Error('X unavailable'));};
  script.onerror=()=>{clearTimeout(timer);reject(new Error('X unavailable'));};document.head.appendChild(script);
 });
 return widgetRequest;
}
function validPost(n:XPost){return /^\d{15,22}$/.test(n.id)&&/^[A-Za-z0-9_]{1,15}$/.test(n.handle)&&n.url===`https://x.com/${n.handle}/status/${n.id}`&&typeof n.text==='string'&&n.text.length<=5000&&Array.isArray(n.coins)&&Array.isArray(n.categories)&&Number.isFinite(Date.parse(n.publishedAt))&&n.kind==='original-x-post';}
function OriginalPost({post}:{post:XPost}){
 const root=useRef<HTMLDivElement>(null);const [loaded,setLoaded]=useState(false);const [failed,setFailed]=useState(false);
 useEffect(()=>{
  const node=root.current;if(!node)return;let cancelled=false;let started=false;
  const render=()=>{if(started)return;started=true;void widgets().then(api=>{if(cancelled)return;return api.widgets.createTweet(post.id,node,{theme:'dark',lang:'sv',dnt:true,conversation:'none',align:'center'});}).then(el=>{if(!cancelled){setLoaded(Boolean(el));setFailed(!el);}}).catch(()=>{if(!cancelled)setFailed(true);});};
  if(!('IntersectionObserver' in window)){render();return()=>{cancelled=true;node.replaceChildren();};}
  const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){observer.disconnect();render();}},{rootMargin:'200px'});observer.observe(node);
  return()=>{cancelled=true;observer.disconnect();node.replaceChildren();};
 },[post.id]);
 return <article className="x-post"><div className="x-post-meta"><b>{post.author}</b><span>@{post.handle}</span><time dateTime={post.publishedAt}>{new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(post.publishedAt))}</time></div><div ref={root} className="x-native-embed"/>{!loaded&&<div className="x-original"><span>ORIGINALINLÄGG · ORIGINALSPRÅK</span><blockquote>{post.text}</blockquote>{post.media?.filter(m=>{try{return new URL(m.url).protocol==='https:'&&new URL(m.url).hostname==='pbs.twimg.com';}catch{return false;}}).slice(0,4).map(m=><img key={m.url} src={m.url} alt={m.alt||'Bild från originalinlägget'} loading="lazy"/>)}</div>}<div className="x-post-footer"><small>{failed?'X:s inbäddning kunde inte laddas. Senast hämtade originaltext visas.':'Kontots eget inlägg · inte oberoende bekräftat'}</small><a href={post.url} target="_blank" rel="noopener noreferrer">Original på X ↗</a></div></article>;
}
export default function XFeed({category,coin,query}:{category:string;coin:string;query:string}){
 const [data,setData]=useState<XData>(seed as XData);const [handle,setHandle]=useState('all');const [limit,setLimit]=useState(3);const [error,setError]=useState(false);
 useEffect(()=>{let stopped=false;let pending=false;const refresh=async()=>{if(pending)return;pending=true;try{const r=await fetch(import.meta.env.BASE_URL+'data/x.json?t='+Date.now(),{cache:'no-store',signal:AbortSignal.timeout(12000)});if(!r.ok)throw new Error('X data');const next=await r.json() as XData;if(!Array.isArray(next.posts)||!Array.isArray(next.sources)||!next.posts.every(validPost)||!Number.isFinite(Date.parse(next.generatedAt)))throw new Error('Invalid X data');if(!stopped){setData(next);setError(false);}}catch{if(!stopped)setError(true);}finally{pending=false;}};void refresh();const timer=setInterval(()=>{if(!document.hidden)void refresh();},60000);return()=>{stopped=true;clearInterval(timer);};},[]);
 useEffect(()=>{setLimit(3);},[handle,category,coin,query]);
 const posts=data.posts.filter(p=>(handle==='all'||p.handle===handle)&&(!coin||p.coins.includes(coin))&&(category==='Senaste'||p.categories.includes(category))&&(!query||(p.text+' '+p.author).toLocaleLowerCase('sv').includes(query.toLocaleLowerCase('sv'))));
 const source=data.sources.find(s=>s.handle===handle);const stale=Date.now()-Date.parse(data.generatedAt)>30*60000;
 return <section className="x-feed" aria-labelledby="x-feed-title"><div className="x-feed-heading"><h2 id="x-feed-title">Från X</h2><span>Originalinlägg</span></div><p className="x-feed-description">Inlägg från kontona, läsbara här på originalspråket. De är inte granskade svenska nyhetsartiklar. X lämnar ut ett begränsat urval – alla nya inlägg kan inte garanteras.</p><div className="x-account-tabs" role="group" aria-label="Välj X-konto"><button onClick={()=>setHandle('all')} aria-pressed={handle==='all'}>Alla</button>{data.sources.map(s=><button key={s.id} onClick={()=>setHandle(s.handle)} aria-pressed={handle===s.handle}>{s.name.replace(' – X','')}</button>)}</div>{source?.message&&<p className="x-source-notice" role="status">{source.message}</p>}{(error||stale)&&<p className="x-source-notice">Senast hämtade urval visas. Senaste kontroll: {new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',dateStyle:'short',timeStyle:'short'}).format(new Date(data.generatedAt))}.</p>}<div className="x-posts">{posts.slice(0,limit).map(p=><OriginalPost key={p.id} post={p}/>)}{!posts.length&&<p className="x-source-notice">Inga aktuella inlägg matchar detta urval.</p>}</div>{posts.length>limit&&<button className="x-more" onClick={()=>setLimit(limit+3)}>Visa fler X-inlägg ({posts.length-limit})</button>}<p className="x-privacy-note">Inbäddningar och bilder hämtas från X när inläggen visas.</p></section>;
}
