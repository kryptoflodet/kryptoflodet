import {mkdtempSync,readFileSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createRequire} from 'node:module';
import ts from 'typescript';
import assert from 'node:assert/strict';
const out=join(mkdtempSync(join(tmpdir(),'market-preferences-tests-')),'preferences.cjs');
writeFileSync(out,ts.transpileModule(readFileSync(new URL('../src/lib/market-preferences.ts',import.meta.url),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText);
const {sortMarketQuotes,normalizeHiddenSymbols,toggleHiddenSymbol,normalizeMarketOrder,moveMarketSymbol}=createRequire(import.meta.url)(out);
const quotes=[
 {id:'a',symbol:'AAA',name:'Alpha',marketCapRank:2,price:2,priceSek:20,change24h:-2,changeSek24h:-2,marketCap:20,marketCapSek:200,volume24h:4,volume24hSek:40,updatedAt:null},
 {id:'b',symbol:'BBB',name:'Beta',marketCapRank:1,price:3,priceSek:30,change24h:5,changeSek24h:5,marketCap:30,marketCapSek:300,volume24h:1,volume24hSek:10,updatedAt:null},
 {id:'c',symbol:'CCC',name:'Gamma',marketCapRank:3,price:null,priceSek:null,change24h:null,changeSek24h:null,marketCap:null,marketCapSek:null,volume24h:null,volume24hSek:null,updatedAt:null},
];
assert.deepEqual(sortMarketQuotes(quotes,'rank').map(q=>q.symbol),['BBB','AAA','CCC']);
assert.deepEqual(sortMarketQuotes(quotes,'name').map(q=>q.symbol),['AAA','BBB','CCC']);
assert.deepEqual(sortMarketQuotes(quotes,'change-high').map(q=>q.symbol),['BBB','AAA','CCC']);
assert.deepEqual(sortMarketQuotes(quotes,'price-low','SEK').map(q=>q.symbol),['AAA','BBB','CCC']);
assert.deepEqual(sortMarketQuotes(quotes,'cap-low').map(q=>q.symbol),['AAA','BBB','CCC']);
assert.deepEqual(sortMarketQuotes(quotes,'volume-high').map(q=>q.symbol),['AAA','BBB','CCC']);
assert.deepEqual(sortMarketQuotes(quotes,'volume-low').map(q=>q.symbol),['BBB','AAA','CCC']);
assert.deepEqual(normalizeHiddenSymbols(['btc','BTC','bad symbol',null,'eth']),['BTC','ETH']);
assert.deepEqual(toggleHiddenSymbol(['BTC'],'ETH',true),['BTC','ETH']);
assert.deepEqual(toggleHiddenSymbol(['BTC','ETH'],'BTC',false),['ETH']);
assert.deepEqual(normalizeMarketOrder(['sol','BTC','UNKNOWN','BTC'],['BTC','ETH','SOL','SUI']),['SOL','BTC','ETH','SUI']);
assert.deepEqual(moveMarketSymbol(['BTC','ETH','SOL'],'BTC','SOL'),['ETH','BTC','SOL']);
assert.deepEqual(moveMarketSymbol(['BTC','ETH','SOL'],'BTC','SOL',true),['ETH','SOL','BTC']);
assert.deepEqual(moveMarketSymbol(['BTC','ETH','SOL'],'UNKNOWN','SOL'),['BTC','ETH','SOL']);
console.log('Market preference checks passed: sorting helpers, visibility choices and saved drag order.');
