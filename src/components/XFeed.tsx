import {useCallback,useEffect,useRef,useState} from 'react';
import seed from '../../public/data/x.json';
import {validXPost,type XPost} from '../lib/x-feed';
export function useXPosts(){
 const [posts,setPosts]=useState<XPost[]>(seed.posts.filter(validXPost) as XPost[]);
 const [error,setError]=useState(false);const pending=useRef(false);
 const refresh=useCallback(async()=>{
  if(pending.current)return;pending.current=true;
  try{
   const response=await fetch(import.meta.env.BASE_URL+'data/x.json?t='+Date.now(),{cache:'no-store',signal:AbortSignal.timeout(12000)});
   if(!response.ok)throw new Error('X data unavailable');
   const data=await response.json();
   if(!Array.isArray(data.posts)||!data.posts.every(validXPost))throw new Error('Invalid X data');
   setPosts(data.posts);setError(false);
  }catch{setError(true);}finally{pending.current=false;}
 },[]);
 useEffect(()=>{void refresh();const timer=setInterval(()=>{if(!document.hidden)void refresh();},60000);return()=>clearInterval(timer);},[refresh]);
 return {posts,error,refresh};
}
export {default} from './XPostCard';
