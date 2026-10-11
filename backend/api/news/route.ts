import {readFeed} from '@/lib/repository';
import {filterNews,deduplicate} from '@/lib/feed';
import {sources} from '@/lib/demo';
export async function GET(request:Request){
 try{const data=await readFeed();const p=new URL(request.url).searchParams;const query=Object.fromEntries(p);const items=filterNews(deduplicate(data.items,sources),query);return Response.json({...data,items,total:items.length},{headers:{'Cache-Control':'private, max-age=30'}});}
 catch{return Response.json({error:'Nyhetsflödet kunde inte hämtas. Försök igen.'},{status:503});}
}
