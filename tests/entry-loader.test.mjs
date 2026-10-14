import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {JSDOM} from 'jsdom';
const fragment=readFileSync('scripts/entry-loader.html','utf8');
const code=fragment.match(/<script>([\s\S]*?)<\/script>/)[1];
const themeCode=readFileSync('index.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const session=new Map();
function visit({theme='dark',reduced=false,type='navigate',storage=true,width=390}={}){
 const dom=new JSDOM('<!doctype html><meta name="theme-color"><body><main>Nyhetsflödet</main></body>',{url:'https://kryptopuls.se',runScripts:'outside-only',pretendToBeVisual:true});const w=dom.window;let timer;const listeners=new Map();
 w.matchMedia=q=>({matches:q.includes('reduced-motion')?reduced:theme==='light',addEventListener:(n,fn)=>listeners.set(q,fn),removeEventListener:()=>{}});
 Object.defineProperty(w,'innerWidth',{value:width});
 Object.defineProperty(w,'sessionStorage',{value:{getItem:k=>{if(!storage)throw Error('blocked');return session.get(k)},setItem:(k,v)=>{if(!storage)throw Error('blocked');session.set(k,v)}}});
 w.localStorage.setItem('kryptopuls-theme',theme);w.performance.getEntriesByType=()=>[{type}];w.setTimeout=fn=>{timer=fn;return 1};w.clearTimeout=()=>{};
 w.eval(themeCode);w.eval(code);
 return {dom,w,finish:()=>timer?.(),motionChange:()=>listeners.get('(prefers-reduced-motion: reduce)')?.()};
}
for(const theme of ['dark','light']){session.clear();const v=visit({theme});const el=v.w.document.querySelector('.kp-entry-loader');assert.ok(el);assert.equal(v.w.document.documentElement.dataset.theme,theme);assert.equal(el.getAttribute('aria-hidden'),'true');assert.match(el.innerHTML,/<svg/);assert.doesNotMatch(el.innerHTML,/<img|src=/);assert.ok(parseFloat(el.style.getPropertyValue('--roll-angle'))>360);assert.equal(v.w.document.querySelector('main').textContent,'Nyhetsflödet');v.finish();assert.equal(v.w.document.querySelector('.kp-entry-loader'),null);v.dom.window.close();const next=visit({theme});assert.equal(next.w.document.querySelector('.kp-entry-loader'),null);next.dom.window.close();}
for(const options of [{reduced:true},{type:'reload'},{storage:false}]){session.clear();const v=visit(options);assert.equal(v.w.document.querySelector('.kp-entry-loader'),null);v.dom.window.close();}
session.clear();const v=visit({width:1440});const overlay=v.w.document.querySelector('.kp-entry-loader');const event=new v.w.Event('animationend',{bubbles:true});Object.defineProperty(event,'animationName',{value:'kp-entry-reveal'});overlay.dispatchEvent(event);assert.equal(v.w.document.querySelector('.kp-entry-loader'),null);v.dom.window.close();
session.clear();const motion=visit();motion.motionChange();assert.equal(motion.w.document.querySelector('.kp-entry-loader'),null);motion.dom.window.close();
const home=readFileSync('dist/index.html','utf8');assert.match(home,/kp-entry-loader/);assert.ok(home.indexOf("dataset.theme = theme")<home.indexOf('kp-entry-loader'));
const staticFile=readFileSync('scripts/build-pages.py','utf8');assert.match(staticFile,/<body>\{ENTRY_LOADER\}/);
assert.match(fragment,/overflow:hidden;pointer-events:none/);assert.match(fragment,/900ms linear/);assert.match(fragment,/120ms ease-out 900ms/);assert.match(fragment,/prefers-reduced-motion:reduce/);
console.log('Entry loader checks passed: local SVG, early theme, responsive rotation, session-only display, reload/reduced-motion/storage skips, timeout/event cleanup and unchanged content.');
