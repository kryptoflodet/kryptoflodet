import type {NewsItem, Source} from './types';
export type FeedQuery={q?:string;category?:string;coin?:string;noise?:string;sort?:string};
const swedishCategoryLabels:Record<string,string>={
 Altcoins:'Alternativa kryptovalutor',
 DeFi:'Decentraliserad finans',
 'On-chain':'Händelser i blockkedjan',
 Mining:'Utvinning',
 Stablecoins:'Värdestabila kryptovalutor',
 'Säkerhet / Hacks':'Säkerhet / intrång',
 Börser:'Kryptobörser',
 ETF:'Börshandlade fonder (ETF)',
};
export function categoryLabel(category:string){return swedishCategoryLabels[category]||category;}
export function sourceTypeLabel(type:Source['type']){return ({OFFICIELL:'Officiell källa',MYNDIGHET:'Myndighet',MEDIA:'Nyhetsmedium',JOURNALIST:'Journalist',ANALYTIKER:'Analytiker',INFLUENCER:'Innehållsskapare'} as const)[type]||'Källa';}
export function filterNews(items:NewsItem[],query:FeedQuery){
 const q=(query.q||'').trim().toLocaleLowerCase('sv');
 return items.filter(n=> (!q||[n.title,n.summary,n.author,n.category,...n.coins,...n.topics].join(' ').toLocaleLowerCase('sv').includes(q)) && (!query.coin||n.coins.includes(query.coin.toUpperCase())) && (!query.category||query.category==='Senaste'||n.category===query.category||n.categories?.includes(query.category)||(query.category==='Bitcoin'&&n.coins.includes('BTC'))||(query.category==='Ethereum'&&n.coins.includes('ETH'))||(query.category==='Altcoins'&&n.coins.some(c=>!['BTC','ETH'].includes(c)))) && (query.noise!=='important'||n.importance>=3&&n.status!=='rumor') && (query.noise!=='confirmed'||n.status==='confirmed')).sort((a,b)=>query.sort==='importance'?b.importance-a.importance||Date.parse(b.publishedAt)-Date.parse(a.publishedAt):Date.parse(b.publishedAt)-Date.parse(a.publishedAt));
}
// Only a reviewed event key may join different URLs. Shared tickers/headlines are not enough.
export function deduplicate(items:NewsItem[],sources:Source[]):NewsItem[]{
 const groups=new Map<string,NewsItem>();
 for(const n of items){ const key=n.eventKey||n.originalUrl;const prev=groups.get(key);if(!prev){groups.set(key,{...n,evidence:[...n.evidence]});continue;}
 const trust=(id:string)=>sources.find(s=>s.id===id)?.trust??0;
 const main=trust(n.sourceId)>trust(prev.sourceId)?n:prev;
 const evidence=[...prev.evidence,...n.evidence].filter((e,i,all)=>all.findIndex(v=>v.url===e.url&&v.sourceId===e.sourceId)===i);
 groups.set(key,{...main,evidence}); }
 return [...groups.values()];
}
export function assessEvidence(item:NewsItem,sources:Source[]){
 const verified=item.evidence.filter(e=>e.verified&&e.direct&&(sources.find(s=>s.id===e.sourceId)?.trust??0)>=80);
 const official=verified.some(e=>['OFFICIELL','MYNDIGHET'].includes(sources.find(s=>s.id===e.sourceId)?.type??''));
 const origins=new Set(verified.map(e=>e.originId));
 const owners=new Set(verified.map(e=>sources.find(s=>s.id===e.sourceId)?.independenceGroup));
 const confirmed=official||(origins.size>=2&&owners.size>=2);
 return {status:confirmed?'confirmed':item.status==='rumor'?'rumor':'unconfirmed',confidence:confirmed?Math.min(98,86+verified.length*3):item.status==='rumor'?20:50};
}
export function trending(items:NewsItem[]){const counts=new Map<string,number>();for(const n of items) for(const t of new Set(n.topics)) counts.set(t,(counts.get(t)||0)+1);return [...counts].sort((a,b)=>b[1]-a[1]).slice(0,5);}
