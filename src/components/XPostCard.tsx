import {useState} from 'react';
import ShareNews,{xPostShareUrl} from './ShareNews';
import type {XPost} from '../lib/x-feed';
import {swedishText} from '../lib/x-feed';
import {isBitcoinStory,isEthereumStory} from '../lib/crypto-story';
function XImage({post}:{post:XPost}){
 const [failedUrl,setFailedUrl]=useState('');
 const media=post.media?.find(m=>{try{const u=new URL(m.url);return u.protocol==='https:'&&u.hostname==='pbs.twimg.com';}catch{return false;}});
 const original=media&&media.url!==failedUrl;
 const art=isBitcoinStory(post.coins,post.categories)?'bitcoin':post.categories.some(c=>['Reglering','Institutionellt'].includes(c))?'institutions':isEthereumStory(post.coins,post.categories)?'ethereum':'network';
 const imageName=art;
 const alt={bitcoin:'Orange Bitcoin-symbol mot svart bakgrund',ethereum:'Illustration av ethereum',institutions:'Illustration av en finansiell institution',network:'Illustration av ett blockkedjenätverk'}[art];
 return <figure className={'x-card-image '+(original?'is-original':'is-illustration')}><img src={original?media.url:imageName==='bitcoin'?'./images/bitcoin.svg':`./images/${imageName}-640.webp`} srcSet={original||imageName==='bitcoin'?undefined:`./images/${imageName}-640.webp 640w, ./images/${imageName}-1280.webp 1280w`} sizes="(max-width:600px) 90vw, 220px" alt={original?'Bild från originalinlägget på X':alt} width="640" height="400" loading="lazy" decoding="async" onError={original?()=>setFailedUrl(media.url):undefined}/><figcaption>{original?'Bild från originalinlägget':'Illustrationsbild'}</figcaption></figure>;
}
export default function XCard({post,onCoin,highlighted=false}:{post:XPost;onCoin:(coin:string)=>void;highlighted?:boolean}){
 const [expanded,setExpanded]=useState(false);
 const original=post.originalLanguage==='sv';const translated=original?post.text:swedishText(post);const pending=!original&&!translated;const method=original?'original':pending?undefined:post.swedish?.method;const text=translated||'Svensk översättning saknas för det här inlägget.';
 return <article id={'x-post-'+post.id} className={'x-post '+(highlighted?'is-shared':'')} aria-label={'X · '+post.author}>
  <div className="x-post-meta"><b>X · {post.author}</b><span>@{post.handle}</span><time dateTime={post.publishedAt}>{new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(post.publishedAt))}</time></div>
  <div className="x-post-content"><XImage post={post}/><div className="x-swedish"><small>{pending?'Svensk översättning saknas':method==='original'?'Svenskt original':method==='summary'?'Sammanfattat på svenska':post.swedish?.engine==='qwen3-4b-sv-checked-v1'?'Översatt och språkgranskat automatiskt':'Översatt till svenska'}</small>{!original&&!pending&&<p className="x-attribution">{post.author} skriver:</p>}<p lang="sv">{text}</p>{post.sourceTruncated&&<p className="x-attribution">Den insamlade originaltexten är avklippt. Öppna originalinlägget på X för hela texten.</p>}</div></div>
  {post.coins.length>0&&<div className="x-coins">{post.coins.map(c=><button key={c} className="coin-tag" onClick={()=>onCoin(c)}>{c}</button>)}</div>}
  <div className="x-post-actions">{!original&&<button aria-expanded={expanded} aria-controls={'x-original-'+post.id} onClick={()=>setExpanded(!expanded)}>{expanded?'Dölj information':'Om originalinlägget'}</button>}<ShareNews title={`X · ${post.author}`} url={xPostShareUrl(post.id)}/><a href={post.url} target="_blank" rel="noopener noreferrer">Visa på X →</a></div>
  {!original&&expanded&&<div id={'x-original-'+post.id} className="x-original"><p>Originaltexten visas på avsändarens X-sida och återges inte här.</p></div>}
  <small className="x-claim-note">Kontots uppgifter · inte oberoende bekräftade</small>
 </article>;
}
