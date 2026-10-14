import {useEffect,useMemo,useState} from 'react';
import {ArrowUpRight,Play,RefreshCw,Video} from 'lucide-react';
import {youtubeVideo} from '../lib/video';

type VideoItem={id:string;title:string;originalUrl:string;publishedAt:string;sourceId:string;author:string};
type VideoFeed={generatedAt:string;items:VideoItem[]};
const BASE=import.meta.env.BASE_URL;
const channels=[
 {id:'all',name:'Alla kanaler',url:''},
 {id:'moon-video',name:'The Moon Show',url:'https://www.youtube.com/@TheMoonShow'},
 {id:'diary-video',name:'The Diary of a CEO',url:'https://www.youtube.com/@TheDiaryOfACEO'},
 {id:'pbd-video',name:'PBD Podcast',url:'https://www.youtube.com/@PBDPodcast'},
 {id:'mmcrypto-video',name:'MMCrypto',url:'https://www.youtube.com/@MMCryptoTube'},
 {id:'cryptokid-video',name:'CryptoKid',url:'https://www.youtube.com/@CryptoKid'},
 {id:'cryptocurrently-video',name:'CryptoCurrently',url:'https://www.youtube.com/@CryptoCurrently'},
 {id:'altcoin-daily-video',name:'Altcoin Daily',url:'https://www.youtube.com/@AltcoinDaily'},
 {id:'rover-video',name:'CryptoRover',url:'https://www.youtube.com/@CryptoRover'},
 {id:'felix-video',name:'Felix Nordqvist',url:'https://www.youtube.com/@FelixNordqvist'},
];
const featured:VideoItem[]=[
 {id:'1aGpJQ8BMLI',title:'Michael Saylor om Bitcoin, AI och långsiktigt tänkande',originalUrl:'https://www.youtube.com/watch?v=1aGpJQ8BMLI',publishedAt:'2026-08-06T00:00:00Z',sourceId:'diary-video',author:'The Diary of a CEO'},
 {id:'49FhysfWX1M',title:'Michael Saylor: Bitcoinens förkämpe · PBD Podcast, avsnitt 128',originalUrl:'https://www.youtube.com/watch?v=49FhysfWX1M',publishedAt:'2022-03-01T00:00:00Z',sourceId:'pbd-video',author:'PBD Podcast'},
];
function validFeed(value:unknown):value is VideoFeed{
 if(!value||typeof value!=='object')return false;
 const feed=value as VideoFeed;
 return Array.isArray(feed.items)&&feed.items.every(v=>typeof v.id==='string'&&typeof v.title==='string'&&typeof v.originalUrl==='string'&&typeof v.publishedAt==='string'&&typeof v.sourceId==='string'&&typeof v.author==='string');
}
function date(value:string){return new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',day:'numeric',month:'short',year:'numeric'}).format(new Date(value));}
export default function YouTubeHub(){
 const [feed,setFeed]=useState<VideoFeed>({generatedAt:'',items:[]});const [selected,setSelected]=useState('all');const [loading,setLoading]=useState(true);const [failed,setFailed]=useState(false);
 async function refresh(){try{const response=await fetch(BASE+'data/youtube.json?t='+Date.now(),{cache:'no-store',signal:AbortSignal.timeout(12000)});if(!response.ok)throw new Error('Flödet kunde inte hämtas');const data:unknown=await response.json();if(!validFeed(data))throw new Error('Ogiltigt videoflöde');setFeed(data);setFailed(false);}catch{setFailed(true);}finally{setLoading(false);}}
 useEffect(()=>{void refresh();const timer=window.setInterval(()=>{if(!document.hidden)void refresh();},300000);return()=>window.clearInterval(timer);},[]);
 const videos=useMemo(()=>[...featured,...feed.items].filter((item,index,all)=>all.findIndex(value=>value.id===item.id)===index).filter(item=>selected==='all'||item.sourceId===selected).sort((a,b)=>Date.parse(b.publishedAt)-Date.parse(a.publishedAt)),[feed.items,selected]);
 return <section className="youtube-hub" id="news-feed" aria-labelledby="youtube-title">
  <div className="youtube-heading"><span className="youtube-kicker"><Video size={15}/> KRYPTO PÅ YOUTUBE</span><h1 id="youtube-title">Kryptovideor, samlade på ett ställe.</h1><p>Färska videor om Bitcoin, kryptomarknaden och större kryptovalutor. Videornas rubriker och innehåll kommer från respektive kanal; Kryptopuls rekommenderar inte kanalernas analyser eller råd.</p></div>
  <div className="youtube-toolbar"><div className="youtube-channels" role="group" aria-label="Filtrera efter YouTube-kanal">{channels.map(channel=><button key={channel.id} className={selected===channel.id?'selected':''} aria-pressed={selected===channel.id} onClick={()=>setSelected(channel.id)}>{channel.name}</button>)}</div><button className="youtube-refresh" onClick={()=>{setLoading(true);void refresh();}} disabled={loading}><RefreshCw size={14}/>{loading?'Hämtar':'Uppdatera'}</button></div>
  {failed&&<p className="youtube-notice" role="status">Videoflödet kunde inte uppdateras. Senast hämtade videor visas.</p>}
  {loading&&!feed.items.length?<div className="youtube-empty" role="status">Hämtar de senaste videorna…</div>:videos.length?<div className="youtube-grid">{videos.map(item=>{const id=youtubeVideo(item);if(!id)return null;return <article className="youtube-card" key={item.id}><a className="youtube-thumbnail" href={item.originalUrl} target="_blank" rel="noopener noreferrer" aria-label={'Spela '+item.title+' på YouTube'}><img src={'https://i.ytimg.com/vi/'+id+'/hqdefault.jpg'} width="480" height="360" loading="lazy" alt=""/><span><Play size={21} fill="currentColor"/></span></a><div className="youtube-card-copy"><div className="youtube-card-meta"><span>{item.author.replace(/\s+–\s+(?:krypto)?videor$/i,'')}</span><time dateTime={item.publishedAt}>{date(item.publishedAt)}</time></div><h2><a href={item.originalUrl} target="_blank" rel="noopener noreferrer">{item.title}</a></h2><a className="youtube-open" href={item.originalUrl} target="_blank" rel="noopener noreferrer">Se videon på YouTube <ArrowUpRight size={14}/></a></div></article>;})}</div>:<div className="youtube-empty"><Video size={27}/><h2>{selected==='all'?'Inga nya videor i urvalet ännu':'Inga nya videor från den här kanalen ännu'}</h2><p>Urvalet uppdateras automatiskt när kanalerna publicerar kryptorelaterade videor.</p>{selected!=='all'&&<button onClick={()=>setSelected('all')}>Visa alla kanaler</button>}</div>}
  <p className="youtube-disclaimer">Videorna visas på originalspråket. Tillgängliga svenska undertexter kan väljas i YouTubes spelare. Innehållet är skapat av fristående kanaler och kan innehålla åsikter, prognoser eller marknadsföring. Kontrollera alltid uppgifter mot primärkällor.</p>
 </section>;
}
