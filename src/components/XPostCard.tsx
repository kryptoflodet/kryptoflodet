import {useState} from 'react';
import ShareNews,{xPostShareUrl} from './ShareNews';
import type {XPost} from '../lib/x-feed';
import {swedishText} from '../lib/x-feed';
import {isBitcoinStory,isEthereumStory} from '../lib/crypto-story';
function XText({text}:{text:string}){
 return <>{text.split(/(https?:\/\/[^\s<>]+)/g).map((part,i)=>{let safe=false;try{const url=new URL(part);safe=url.protocol==='https:'&&['x.com','twitter.com','t.co'].includes(url.hostname)&&!url.username&&!url.password&&!url.port;}catch{}return safe?<a key={i} href={part} target="_blank" rel="noopener noreferrer">{part}</a>:part;})}</>;
}
function XImage({post}:{post:XPost}){
 const [failedUrl,setFailedUrl]=useState('');
 const media=post.media?.find(m=>{try{const u=new URL(m.url);return u.protocol==='https:'&&u.hostname==='pbs.twimg.com';}catch{return false;}});
 const original=media&&media.url!==failedUrl;
 const art=isBitcoinStory(post.coins,post.categories)?'bitcoin':post.categories.some(c=>['Reglering','Institutionellt'].includes(c))?'institutions':isEthereumStory(post.coins,post.categories)?'ethereum':'network';
 const imageName=art;
 const alt={bitcoin:'Orange Bitcoin-symbol mot svart bakgrund',ethereum:'Illustration av ethereum',institutions:'Illustration av en finansiell institution',network:'Illustration av ett blockkedjenätverk'}[art];
 return <figure className={'x-card-image '+(original?'is-original':'is-illustration')}><img src={original?media.url:imageName==='bitcoin'?'./images/bitcoin.svg':`./images/${imageName}-640.webp`} srcSet={original||imageName==='bitcoin'?undefined:`./images/${imageName}-640.webp 640w, ./images/${imageName}-1280.webp 1280w`} sizes="(max-width:600px) 90vw, 220px" alt={original?(media.alt||`Bild från ${post.author}s originalinlägg på X`):alt} width="640" height="400" loading="lazy" decoding="async" onError={original?()=>setFailedUrl(media.url):undefined}/><figcaption>{original?'Bild från originalinlägget':'Illustrationsbild'}</figcaption></figure>;
}
export default function XCard({post,onCoin,highlighted=false}:{post:XPost;onCoin:(coin:string)=>void;highlighted?:boolean}){
 const [expanded,setExpanded]=useState(false);
 const original=post.originalLanguage==='sv';const translated=original?post.text:swedishText(post);const pending=!original&&!translated;const method=original?'original':pending?undefined:post.swedish?.method;const text=translated||post.text;
 return <article id={'x-post-'+post.id} className={'x-post '+(highlighted?'is-shared':'')} aria-label={'X · '+post.author}>
  <div className="x-post-meta"><b>X · {post.author}</b><span>@{post.handle}</span><time dateTime={post.publishedAt}>{new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(post.publishedAt))}</time></div>
  <div className="x-post-content"><XImage post={post}/><div className="x-swedish"><small>{pending?'X-inlägg · Original':method==='original'?'Svenskt original':method==='summary'?'Sammanfattat på svenska':'Översatt till svenska'}</small>{!original&&!pending&&<p className="x-attribution">{post.author} skriver:</p>}<p lang={pending?post.originalLanguage:'sv'}>{original?<XText text={text||''}/>:text}</p></div></div>
  {post.coins.length>0&&<div className="x-coins">{post.coins.map(c=><button key={c} className="coin-tag" onClick={()=>onCoin(c)}>{c}</button>)}</div>}
  <div className="x-post-actions">{!original&&<button aria-expanded={expanded} aria-controls={'x-original-'+post.id} onClick={()=>setExpanded(!expanded)}>{expanded?'Dölj original':post.originalLanguage==='en'?'Visa original på engelska':'Visa original'}</button>}<ShareNews title={`X · ${post.author}`} url={xPostShareUrl(post.id)}/><a href={post.url} target="_blank" rel="noopener noreferrer">Visa på X →</a></div>
  {!original&&expanded&&<div id={'x-original-'+post.id} className="x-original"><blockquote lang={post.originalLanguage==='en'?'en':undefined}><XText text={post.text}/></blockquote>{post.media?.filter(m=>{try{return new URL(m.url).protocol==='https:'&&new URL(m.url).hostname==='pbs.twimg.com';}catch{return false;}}).slice(0,4).map(m=><img key={m.url} src={m.url} alt={m.alt||'Bild från originalinlägget'} loading="lazy"/>)}</div>}
  <small className="x-claim-note">Kontots uppgifter · inte oberoende bekräftade</small>
 </article>;
}
