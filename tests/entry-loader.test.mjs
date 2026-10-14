import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {JSDOM} from 'jsdom';
const fragment=readFileSync('scripts/entry-loader.html','utf8');
const themeCode=readFileSync('index.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const session=new Map();
function visit({theme='dark',reduced=false,type='navigate',storage=true,referrer=''}={}){
 let finish;const dom=new JSDOM('<!doctype html><head><meta name="theme-color"><script>'+themeCode+'</script></head><body>'+fragment+'<main>Nyhetsflödet</main></body>',{url:'https://kryptopuls.se',runScripts:'dangerously',pretendToBeVisual:true,...(referrer?{referrer}:{}),beforeParse(w){
 w.matchMedia=q=>({matches:q.includes('reduced-motion')?reduced:theme==='light'});
 Object.defineProperty(w,'sessionStorage',{value:{getItem:k=>{if(!storage)throw Error('blocked');return session.get(k)},setItem:(k,v)=>{if(!storage)throw Error('blocked');session.set(k,v)}}});
 w.performance.getEntriesByType=()=>[{type}];w.setTimeout=fn=>{finish=fn;return 1};w.clearTimeout=()=>{};w.localStorage.setItem('kryptopuls-theme',theme);
 }});return {dom,w:dom.window,finish:()=>finish?.()};
}
for(const theme of ['dark','light']){session.clear();const v=visit({theme});const el=v.w.document.querySelector('.kp-entry-loader');assert.ok(el);assert.equal(v.w.document.documentElement.dataset.kpEntry,'show');assert.equal(v.w.document.documentElement.dataset.theme,theme);assert.equal(el.getAttribute('aria-hidden'),'true');assert.equal(el.querySelectorAll('svg').length,1);assert.equal(el.querySelectorAll('img').length,0);assert.equal(v.w.document.querySelector('main').textContent,'Nyhetsflödet');v.finish();assert.equal(v.w.document.querySelector('.kp-entry-loader'),null);v.dom.window.close();const next=visit({theme});assert.equal(next.w.document.querySelector('.kp-entry-loader'),null);next.dom.window.close();}
for(const type of ['reload','reload']){const v=visit({type});assert.ok(v.w.document.querySelector('.kp-entry-loader'),'Every explicit refresh plays even after previous view');v.finish();v.dom.window.close();}
for(const type of ['navigate','back_forward']){const v=visit({type});assert.equal(v.w.document.querySelector('.kp-entry-loader'),null,'Internal/full-page navigation does not replay');v.dom.window.close();}
session.clear();const reduced=visit({reduced:true});assert.equal(reduced.w.document.querySelector('.kp-entry-loader'),null);assert.equal(session.size,0);reduced.dom.window.close();
const noStorage=visit({storage:false});assert.ok(noStorage.w.document.querySelector('.kp-entry-loader'),'Blocked storage cannot hide first animation');noStorage.finish();noStorage.dom.window.close();
const internal=visit({storage:false,referrer:'https://kryptopuls.se/nyheter/example/'});assert.equal(internal.w.document.querySelector('.kp-entry-loader'),null);internal.dom.window.close();
session.clear();const v=visit();const event=new v.w.Event('animationend',{bubbles:true});Object.defineProperty(event,'animationName',{value:'kp-entry-reveal'});v.w.document.querySelector('.kp-entry-loader').dispatchEvent(event);assert.equal(v.w.document.querySelector('.kp-entry-loader'),null);v.dom.window.close();
const home=readFileSync('dist/index.html','utf8');assert.match(home,/kp-entry-bounce-x/);assert.match(home,/kp-entry-bounce-y/);assert.ok(home.indexOf('dataset.theme = theme')<home.indexOf('kp-entry-loader'));
assert.match(fragment,/100vw - var\(--coin-size\)/);assert.match(fragment,/100dvh - var\(--coin-size\)/);assert.match(fragment,/480ms linear 3 alternate/);assert.match(fragment,/360ms linear 4 alternate/);assert.match(fragment,/rotate\(1080deg\)/);assert.doesNotMatch(fragment,/requestAnimationFrame|createElement|innerHTML/);assert.match(fragment,/prefers-reduced-motion:reduce/);
console.log('Bitcoin bounce checks passed: declarative SVG, correct initial theme, first visit/reloads, internal navigation suppression, blocked storage, reduced motion, edge reflection, spin and bounded cleanup.');
