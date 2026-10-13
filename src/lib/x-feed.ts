import type {NewsItem} from './types';
import type {FeedQuery} from './feed';
export interface XPost {
 id:string;handle:string;author:string;url:string;publishedAt:string;text:string;
 coins:string[];categories:string[];kind:'original-x-post';originalLanguage:string;
 swedish?:{text:string;method:'translation'|'summary'|'original';sourceHash:string;engine:string};
 media?:{url:string;alt:string}[];
}
export type FeedEntry={type:'news';id:string;date:string;importance:number;item:NewsItem}|{type:'x';id:string;date:string;importance:number;item:XPost};
export type FeedChannel='all'|'news'|'x';
export function filterFeedChannel(entries:FeedEntry[],channel:FeedChannel,account=''){
 return entries.filter(entry=>(channel==='all'||entry.type===(channel==='news'?'news':'x'))&&(!account||entry.type==='x'&&entry.item.handle.toLowerCase()===account.toLowerCase()));
}
export function sourceConnectionLabel(source:{connection:string;enabled?:boolean}){return source.connection==='connected'?'Ansluten':source.connection==='limited'?'Begränsat urval':source.enabled?'Hämtningsfel':'Ej ansluten';}
export async function archivedXPostUrl(id:string,base:string,request:typeof fetch=fetch){
 if(!/^\d{15,22}$/.test(id))return null;
 const url=new URL(`x/${id}/`,base);
 try{const response=await request(url.href,{method:'HEAD',cache:'force-cache',signal:AbortSignal.timeout(5000)});return response.ok?url.href:null;}catch{return null;}
}
export function validXPost(value:unknown):value is XPost {
 if(!value||typeof value!=='object')return false;
 const n=value as XPost;
 return typeof n.id==='string'&&/^\d{15,22}$/.test(n.id)&&typeof n.handle==='string'&&/^[A-Za-z0-9_]{1,15}$/.test(n.handle)&&n.url===`https://x.com/${n.handle}/status/${n.id}`&&typeof n.author==='string'&&typeof n.originalLanguage==='string'&&typeof n.text==='string'&&n.text.trim().length>0&&n.text.length<=5000&&Array.isArray(n.coins)&&n.coins.every(c=>typeof c==='string')&&Array.isArray(n.categories)&&n.categories.every(c=>typeof c==='string')&&Number.isFinite(Date.parse(n.publishedAt))&&n.kind==='original-x-post'&&(!n.media||(Array.isArray(n.media)&&n.media.every(m=>m&&typeof m.url==='string'&&typeof m.alt==='string')))&&(!n.swedish||(typeof n.swedish.text==='string'&&n.swedish.text.length>0&&n.swedish.text.length<=6000&&['translation','summary','original'].includes(n.swedish.method)));
}
const trustedSwedishEngines=new Set(['reviewed','x-sv-rules-v1','nllb-200-600m-q8-v3','mymemory-free-v2']);
export function swedishText(post:XPost):string|null{
 if(post.originalLanguage==='sv')return post.text;
 const translation=post.swedish;
 return translation?.text&&trustedSwedishEngines.has(translation.engine)?translation.text:null;
}
export function readableX(post:XPost){return Boolean(swedishText(post));}
export function mergeFeed(news:NewsItem[],posts:XPost[],query:FeedQuery,savedOnly=false,saved:string[]=[],now=Date.now()):FeedEntry[]{
 const q=(query.q||'').trim().toLocaleLowerCase('sv');
 const articles:FeedEntry[]=news.map(item=>({type:'news',id:item.id,date:item.publishedAt,importance:item.importance,item}));
 const seen=new Set<string>();
 const social:FeedEntry[]=posts.filter(p=>{
  if(!validXPost(p)||seen.has(p.id))return false;seen.add(p.id);
  const age=now-Date.parse(p.publishedAt);
  return age>=-600000&&age<=14*86400000&&(!query.noise||query.noise==='all')&&(!query.coin||p.coins.includes(query.coin.toUpperCase()))&&(!query.category||query.category==='Senaste'||p.categories.includes(query.category)||(query.category==='Altcoins'&&p.coins.some(c=>!['BTC','ETH'].includes(c))))&&(!q||[p.text,swedishText(p),p.author,p.handle,...p.coins,...p.categories].join(' ').toLocaleLowerCase('sv').includes(q));
 }).map(item=>({type:'x',id:'x:'+item.id,date:item.publishedAt,importance:0,item}));
 return [...articles,...social].filter(n=>!savedOnly||saved.includes(n.id)).sort((a,b)=>(query.sort==='importance'?b.importance-a.importance:0)||Date.parse(b.date)-Date.parse(a.date)||a.id.localeCompare(b.id));
}
