import type {NewsItem} from './types';
const videoSources=new Set(['moon-video','altcoin-daily-video','rover-video']);
/** Derive embeds from trusted source URLs; also supports previously published items. */
export function youtubeVideo(item:Pick<NewsItem,'sourceId'|'originalUrl'>):string|null{
 if(!videoSources.has(item.sourceId))return null;
 try{
  const url=new URL(item.originalUrl);if(url.protocol!=='https:'||url.username||url.password||url.port)return null;
  let id:string|null=null;
  if(url.hostname==='youtu.be')id=url.pathname.slice(1);
  else if(['youtube.com','www.youtube.com','m.youtube.com'].includes(url.hostname)){
   if(url.pathname==='/watch')id=url.searchParams.get('v');
   else {const match=url.pathname.match(/^\/(?:shorts|live|embed)\/([^/]+)\/?$/);if(match)id=match[1];}
  }
  return id&&/^[A-Za-z0-9_-]{11}$/.test(id)?id:null;
 }catch{return null;}
}
