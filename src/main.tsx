import React from 'react';
import {createRoot} from 'react-dom/client';
import App from './App';
import './styles.css';
import './design-v2.css';
class ErrorBoundary extends React.Component<React.PropsWithChildren,{failed:boolean}>{
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true};}
 render(){return this.state.failed?<main><h1>Kryptopuls kunde inte starta.</h1><p>Ladda om sidan för att hämta den senaste versionen.</p><button onClick={()=>window.location.reload()}>Ladda om</button></main>:this.props.children;}
}
createRoot(document.getElementById('root')!).render(<ErrorBoundary><App/></ErrorBoundary>);

// Refresh old application code after a deployment, without interrupting reading.
const currentRevision=document.querySelector('meta[name="site-revision"]')?.getAttribute('content');
async function checkRevision(){
 if(!currentRevision||document.hidden||document.querySelector('dialog[open]')||document.activeElement?.tagName==='INPUT')return;
 try{const r=await fetch(import.meta.env.BASE_URL+'version.json?t='+Date.now(),{cache:'no-store',signal:AbortSignal.timeout(8000)});if(!r.ok)return;const next=await r.json();if(typeof next.revision!=='string'||next.revision===currentRevision)return;const key='revision-reload-'+next.revision;if(sessionStorage.getItem(key))return;sessionStorage.setItem(key,'1');location.reload();}catch{}
}
setInterval(()=>void checkRevision(),60000);
document.addEventListener('visibilitychange',()=>void checkRevision());
