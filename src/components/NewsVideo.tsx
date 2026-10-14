import {ExternalLink,Play} from 'lucide-react';
import type {NewsItem} from '../lib/types';
import {youtubeVideo} from '../lib/video';
export default function NewsVideo({item}:{item:NewsItem}){
 const id=youtubeVideo(item);if(!id)return null;
 return <section className="news-video" aria-label="Nyhetens video"><div className="video-label"><Play size={16}/>SE VIDEON DIREKT</div><div className="video-frame"><iframe key={id} src={`https://www.youtube-nocookie.com/embed/${id}?playsinline=1&hl=sv&cc_lang_pref=sv&cc_load_policy=1&rel=0`} title={'Spela video: '+item.title} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowFullScreen referrerPolicy="strict-origin-when-cross-origin"/></div><p>{item.originalLanguage==='sv'?'Video på svenska.':'Videon visas på originalspråket. Svenska undertexter kan väljas i spelaren om de finns tillgängliga.'}</p><a href={'https://www.youtube.com/watch?v='+id} target="_blank" rel="noopener noreferrer">Går videon inte att spela? Öppna på YouTube <ExternalLink size={14}/></a></section>;
}
