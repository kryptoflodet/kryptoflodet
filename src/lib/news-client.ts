import seed from '../../public/data/news.json';
import type {NewsItem,Source} from './types';
export interface NewsFeed {generatedAt:string;items:NewsItem[];sources:Source[];intervalMinutes:number;}
export const initialNews=seed as NewsFeed;
export const sources=initialNews.sources;
export async function fetchNews():Promise<NewsFeed>{
 const response=await fetch(import.meta.env.BASE_URL+'data/news.json?t='+Date.now(),{cache:'no-store',signal:AbortSignal.timeout(15000)});
 if(!response.ok)throw new Error('Nyhetsflödet kunde inte hämtas');
 const data=await response.json() as NewsFeed;
 if(!Array.isArray(data.items)||!Array.isArray(data.sources)||!Number.isFinite(Date.parse(data.generatedAt)))throw new Error('Ogiltigt nyhetsflöde');
 if(!data.items.every(n=>n.demo===false&&typeof n.title==='string'&&Array.isArray(n.coins)&&Array.isArray(n.topics)&&Array.isArray(n.evidence)&&Number.isFinite(Date.parse(n.publishedAt))&&/^https?:\/\//.test(n.originalUrl)))throw new Error('Ogiltiga nyhetsposter');
 return data;
}
