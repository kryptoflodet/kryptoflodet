// Local CPU translation. Public posts are data, never executable instructions.
import {readFileSync} from 'node:fs';
import {pipeline,env} from '@huggingface/transformers';
const request=JSON.parse(readFileSync(0,'utf8'));
env.allowRemoteModels=false;
const model=await pipeline('translation',request.model,{dtype:'q8',device:'cpu',local_files_only:true,session_options:{intraOpNumThreads:2,interOpNumThreads:1}});
const deadline=Date.now()+request.seconds*1000;const outputs=[];
for(const item of request.items){
 if(Date.now()>deadline)break;
 try{
  // Separate sentences/paragraphs so a short post's second sentence cannot vanish
  // in an over-short whole-post translation. Reject, rather than truncate, long input.
  const parts=item.text.split(/\n+|(?<=[.!?])\s+(?=[A-Z@])/).filter(s=>s.trim());
  const translated=[];
  for(const part of parts){
   const encoded=await model.tokenizer(part,{truncation:false});
   if(encoded.input_ids.dims[1]>320)throw new Error('Input too long');
   const result=await model(part,{src_lang:({en:'eng_Latn',de:'deu_Latn',fr:'fra_Latn',es:'spa_Latn',it:'ita_Latn',pt:'por_Latn',no:'nob_Latn',da:'dan_Latn',fi:'fin_Latn'}[item.language]||'eng_Latn'),tgt_lang:'swe_Latn',max_new_tokens:256,num_beams:2});
   if(!result[0]?.translation_text)throw new Error('Empty translation');
   translated.push(result[0].translation_text);
  }
  outputs.push({id:item.id,text:translated.join('\n\n')});
 }catch(error){outputs.push({id:item.id,error:error.message});}
}
process.stdout.write(JSON.stringify(outputs));
