import {getDb} from '@/db';
import {articles} from '@/db/schema';
import {eq,desc} from 'drizzle-orm';
import {demoNews,snapshot} from './demo';
import type {NewsItem} from './types';
export async function readFeed(){
 const rows=await getDb().select().from(articles).where(eq(articles.visible,true)).orderBy(desc(articles.publishedAt)).limit(300);
 if(!rows.length)return {mode:'demo' as const,asOf:snapshot,items:demoNews};
 return {mode:'live' as const,asOf:rows[0].importedAt,items:rows.map(r=>JSON.parse(r.payload) as NewsItem)};
}
