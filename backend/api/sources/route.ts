import {sources} from '@/lib/demo';
export async function GET(){return Response.json({sources,mode:'planned',note:'Preliminära redaktionella bedömningar. Inga källor är anslutna; kontonas identitet behöver kontrolleras före aktivering.'});}
