import {defineConfig} from 'vite';
import {execFileSync} from 'node:child_process';
import react from '@vitejs/plugin-react';
import {fileURLToPath,URL} from 'node:url';
const revision=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();
const versionPlugin={name:'site-revision',transformIndexHtml(){return [{tag:'meta',attrs:{name:'site-revision',content:revision},injectTo:'head' as const}];},generateBundle(this:any){this.emitFile({type:'asset',fileName:'version.json',source:JSON.stringify({revision})});}};
export default defineConfig({base:'./',plugins:[react(),versionPlugin],resolve:{alias:{'@':fileURLToPath(new URL('./src',import.meta.url))}},build:{outDir:'dist'}});
