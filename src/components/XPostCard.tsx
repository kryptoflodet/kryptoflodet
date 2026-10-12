import {useState} from 'react';
import {Bookmark} from 'lucide-react';
import type {XPost} from '../lib/x-feed';
export default function XCard({post,saved,toggle,onCoin}:{post:XPost;saved:boolean;toggle:()=>void;onCoin:(coin:string)=>void}){
 const [expanded,setExpanded]=useState(false);
 const original=post.originalLanguage==='sv';const method=original?'original':post.swedish?.method;const text=original?post.text:post.swedish?.text;
 if(!text)return null;
 return <article className="x-post" aria-label={'X · '+post.author}>
  <div className="x-post-meta"><b>X · {post.author}</b><span>@{post.handle}</span><time dateTime={post.publishedAt}>{new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(post.publishedAt))}</time><button className={'icon-button save '+(saved?'saved':'')} onClick={toggle} aria-label={saved?'Ta bort sparat X-inlägg':'Spara X-inlägg'} aria-pressed={saved}><Bookmark size={17} fill={saved?'currentColor':'none'}/></button></div>
  <div className="x-swedish"><small>{method==='original'?'Svenskt original':method==='summary'?'Sammanfattat på svenska':'Översatt till svenska'}</small>{!original&&<p className="x-attribution">{post.author} skriver:</p>}<p lang="sv">{text}</p></div>
  {post.coins.length>0&&<div className="x-coins">{post.coins.map(c=><button key={c} className="coin-tag" onClick={()=>onCoin(c)}>{c}</button>)}</div>}
  <div className="x-post-actions">{!original&&<button aria-expanded={expanded} aria-controls={'x-original-'+post.id} onClick={()=>setExpanded(!expanded)}>{expanded?'Dölj original':'Visa original'}</button>}<a href={post.url} target="_blank" rel="noopener noreferrer">Visa på X →</a></div>
  {!original&&expanded&&<div id={'x-original-'+post.id} className="x-original"><blockquote lang={post.originalLanguage==='en'?'en':undefined}>{post.text}</blockquote>{post.media?.filter(m=>{try{return new URL(m.url).protocol==='https:'&&new URL(m.url).hostname==='pbs.twimg.com';}catch{return false;}}).slice(0,4).map(m=><img key={m.url} src={m.url} alt={m.alt||'Bild från originalinlägget'} loading="lazy"/>)}</div>}
  <small className="x-claim-note">Kontots uppgifter · inte oberoende bekräftade</small>
 </article>;
}
