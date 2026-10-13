import type {FeedChannel} from '../lib/x-feed';
export default function FeedChannels({channel,account,accounts,onChange}:{channel:FeedChannel;account:string;accounts:{handle:string;name:string;count:number}[];onChange:(channel:FeedChannel,account?:string)=>void}){
 return <div className="feed-channel-row"><div className="noise-filter" role="group" aria-label="Inläggstyp">
  {([['all','Alla inlägg'],['news','Nyheter'],['x','X-inlägg']] as const).map(([value,label])=><button key={value} aria-pressed={channel===value} className={channel===value?'selected':''} onClick={()=>onChange(value)}>{label}</button>)}
 </div>{channel==='x'&&<label className="category-select"><span className="sr-only">X-konto</span><select aria-label="X-konto" value={account} onChange={e=>onChange('x',e.target.value)}><option value="">Alla X-konton</option>{accounts.map(source=><option key={source.handle} value={source.handle}>{source.name} ({source.count})</option>)}</select></label>}</div>;
}
