import {mkdtempSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createRequire} from 'node:module';
import ts from 'typescript';
import assert from 'node:assert/strict';
const dir=mkdtempSync(join(tmpdir(),'video-tests-'));
try{
 writeFileSync(join(dir,'video.js'),ts.transpileModule(readFileSync('src/lib/video.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText);
 const {youtubeVideo}=createRequire(import.meta.url)(join(dir,'video.js'));
 for(const sourceId of ['moon-video','altcoin-daily-video','rover-video','felix-video','mmcrypto-video','diary-video','pbd-video','cryptokid-video','cryptocurrently-video'])for(const originalUrl of ['https://www.youtube.com/watch?v=-zGjZyIgoOs','https://youtu.be/-zGjZyIgoOs','https://www.youtube.com/shorts/-zGjZyIgoOs','https://www.youtube.com/live/-zGjZyIgoOs'])assert.equal(youtubeVideo({sourceId,originalUrl}),'-zGjZyIgoOs');
 for(const originalUrl of ['https://youtube.com.evil.test/watch?v=-zGjZyIgoOs','javascript:alert(1)','https://youtube.com/watch?v=bad','https://youtube.com/playlist?list=-zGjZyIgoOs','https://youtube.com@evil.test/watch?v=-zGjZyIgoOs'])assert.equal(youtubeVideo({sourceId:'moon-video',originalUrl}),null);
 assert.equal(youtubeVideo({sourceId:'moon-watch',originalUrl:'https://www.youtube.com/watch?v=-zGjZyIgoOs'}),null);
 console.log('Video checks passed: old/new URLs, shorts/live, source allowlist and hostile URL rejection.');
}finally{rmSync(dir,{recursive:true,force:true});}
