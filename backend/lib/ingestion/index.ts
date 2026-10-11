import type {NewsItem,Source} from '../types';
import {assessEvidence,deduplicate} from '../feed';
export type ConnectorKind='x'|'instagram'|'rss'|'news-api'|'official-api'|'market';
export interface Connector {kind:ConnectorKind;status:'disconnected'|'connected'; fetch():Promise<NewsItem[]>;}
export interface SwedishEditor {summarize(item:NewsItem):Promise<Pick<NewsItem,'title'|'translation'|'summary'|'why'|'sentiment'>>;}
export const connectorRegistry:Connector[]=['x','instagram','rss','news-api','official-api','market'].map(kind=>({kind:kind as ConnectorKind,status:'disconnected',async fetch(){return [];}}));
// Intentionally no scraping and no automatic trust escalation. Adapters must preserve origin IDs.
export async function ingest(connector:Connector,sources:Source[],editor:SwedishEditor){
 if(connector.status!=='connected')return {status:'disconnected',items:[]};
 const imported=await connector.fetch();
 const eligible=imported.filter(n=>sources.some(s=>s.id===n.sourceId&&s.enabled)&&/^https:\/\//.test(n.originalUrl));
 const grouped=deduplicate(eligible,sources);
 const items=await Promise.all(grouped.map(async n=>({...n,...await editor.summarize(n),...assessEvidence(n,sources),importedAt:new Date().toISOString(),demo:false,analysisMethod:'automated' as const})));
 return {status:'ok',items};
}
