import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,copyFileSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {createRequire} from 'node:module';
import ts from 'typescript';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import React,{act} from 'react';
import {createRoot} from 'react-dom/client';
const dir=mkdtempSync(join(process.cwd(),'node_modules/.pulse-ui-'));mkdirSync(join(dir,'lib'));mkdirSync(join(dir,'components'));
for(const [folder,names] of [['lib',['pulse','market-context','market-preferences']],['components',['MarketPulse','MarketBrief']]])for(const name of names){const ext=folder==='components'?'tsx':'ts';writeFileSync(join(dir,folder,name+'.js'),ts.transpileModule(readFileSync(`src/${folder}/${name}.${ext}`,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true}}).outputText);}
copyFileSync('src/lib/upcoming-events.json',join(dir,'lib/upcoming-events.json'));
const req=createRequire(import.meta.url),Pulse=req(join(dir,'components/MarketPulse.js')).default,Brief=req(join(dir,'components/MarketBrief.js')).default,{emptyMarketContext}=req(join(dir,'lib/market-context.js'));
const dom=new JSDOM('<div id="root"></div>',{url:'https://kryptopuls.se'});Object.assign(globalThis,{window:dom.window,document:dom.window.document,localStorage:dom.window.localStorage,IS_REACT_ACT_ENVIRONMENT:true});const root=createRoot(document.getElementById('root')),now=Date.parse('2026-10-14T10:00:00Z');let clicked='';
try{
 const props={context:emptyMarketContext,market:{quotes:[{symbol:'BTC',name:'Bitcoin',change24h:2,updatedAt:new Date(now).toISOString()},{symbol:'ETH',name:'Ethereum',change24h:3,updatedAt:new Date(now).toISOString()},{symbol:'SUI',name:'Sui',change24h:6,updatedAt:new Date(now).toISOString()}]},now};
 for(const theme of ['dark','light']){document.documentElement.dataset.theme=theme;await act(()=>root.render(React.createElement(React.Fragment,{key:theme},React.createElement(Pulse,props),React.createElement(Brief,{...props,items:[],hidden:[],onCoin:s=>clicked=s,onArticle:()=>{}}))));assert.match(document.body.textContent,/Inväntar data/);assert.match(document.body.textContent,/Marknaden just nu/);assert.match(document.body.textContent,/Underlaget räcker inte/);assert.match(document.body.textContent,/Fed:/);assert.equal(document.querySelector('.pulse-details').open,false);assert.equal(document.querySelector('.brief-calendar').open,false);await act(()=>document.querySelector('[aria-label="Visa diagram för Sui"]').click());assert.equal(clicked,'SUI');document.querySelector('.pulse-details').open=true;assert.match(document.querySelector('.pulse-details').textContent,/50 % Fear/);}
 console.log('Pulse UI checks passed: both themes, missing-data states, collapsed detail panels, upcoming dates and chart actions.');
}finally{await act(()=>root.unmount());dom.window.close();rmSync(dir,{recursive:true,force:true});}
