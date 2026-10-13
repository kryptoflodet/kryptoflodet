import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import ts from 'typescript';

const source=readFileSync('src/lib/crypto-story.ts','utf8');
const compiled=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const loaded={exports:{}};
new Function('exports','module',compiled)(loaded.exports,loaded);
const {isBitcoinStory,isEthereumStory}=loaded.exports;

assert.equal(isBitcoinStory(['BTC'],[]),true,'A Bitcoin-only tag selects the Bitcoin image');
assert.equal(isBitcoinStory([],['Bitcoin']),true,'The Bitcoin category selects the Bitcoin image when coin tags are absent');
assert.equal(isBitcoinStory(['BTC','ETH'],['Bitcoin']),false,'A mixed-currency post does not select the Bitcoin image');
assert.equal(isBitcoinStory(['ETH'],['Bitcoin']),false,'An Ethereum post does not select the Bitcoin image');
assert.equal(isBitcoinStory(['SUI'],['Bitcoin']),false,'An altcoin post does not select the Bitcoin image');
assert.equal(isBitcoinStory([],[]),false,'An unclassified post does not select the Bitcoin image');
assert.equal(isEthereumStory(['ETH'],[]),true,'An Ethereum-only tag selects the Ethereum image');
assert.equal(isEthereumStory(['ETH','BTC'],['Ethereum']),false,'A mixed-currency post does not select the Ethereum image');
assert.equal(isEthereumStory(['SUI'],[]),false,'An altcoin post does not select the Ethereum image');
console.log('Crypto story image classification passed.');
