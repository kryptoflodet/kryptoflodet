import type { NewsItem, Source, MarketQuote } from './types';
export const snapshot = '2026-10-11T12:00:00Z';
export const sources: Source[] = [
 ['sec','SEC','MYNDIGHET','RSS','https://www.sec.gov',98,'sec'],
 ['strategy','Strategy','OFFICIELL','API','https://www.strategy.com',95,'strategy'],
 ['saylor','Michael Saylor','OFFICIELL','X','https://x.com/saylor',88,'strategy'],
 ['bitcoinmag','Bitcoin Magazine','MEDIA','RSS','https://bitcoinmagazine.com',78,'bitcoinmag'],
 ['watcher','Watcher.Guru','MEDIA','X','https://watcher.guru',70,'watcher'],
 ['ethereum','Ethereum Foundation','OFFICIELL','RSS','https://blog.ethereum.org',95,'ethereum'],
 ['sui','Sui','OFFICIELL','X','https://sui.io',93,'sui'],
 ['solana','Solana','OFFICIELL','API','https://solana.com',92,'solana'],
 ['fed','Federal Reserve','MYNDIGHET','RSS','https://www.federalreserve.gov',98,'fed'],
 ['coindesk','CoinDesk','MEDIA','RSS','https://www.coindesk.com',85,'coindesk'],
 ['rover','CryptoRover','INFLUENCER','X','https://x.com/rovercrc',45,'rover'],
 ['moon','The Moon Show','INFLUENCER','X','https://www.youtube.com/@TheMoon',40,'moon'],
 ['bitcoin','Bitcoin','MEDIA','X','https://x.com/bitcoin',60,'bitcoin'],
 ['kid','CryptoKid','INFLUENCER','X','',40,'kid'],
 ['blackrock','BlackRock','OFFICIELL','API','https://www.blackrock.com',95,'blackrock'],
 ['ondo','Ondo Finance','OFFICIELL','X','https://ondo.finance',90,'ondo'],
 ['instagram','Instagram · officiella konton','OFFICIELL','Instagram','https://www.instagram.com',0,'instagram'],
].map(([id,name,type,channel,url,trust,independenceGroup])=>({id,name,type,channel,url,trust,independenceGroup,enabled:false,connection:'planned'} as Source));
type Seed = [string,string,string,string,string[],string,string,string,number,NewsItem['status'],NewsItem['sentiment'],string[]];
const seeds: Seed[] = [
 ['etf','Spot-ETF: nytt besked sätter Bitcoin i fokus','Reglering','sec',['BTC'],'Ett exempel på hur ett myndighetsbesked om en Bitcoin-ETF presenteras: beslutet sammanfattas, originalet länkas och återpubliceringar grupperas.','Ett ändrat regelverk kan påverka hur institutioner får exponering mot Bitcoin. Ett godkännande innebär däremot inte automatiskt nya inflöden.','New decision puts Bitcoin spot ETFs in focus',5,'confirmed','Bullish',['ETF','Bitcoin']],
 ['treasury','Ett nytt Bitcoin-köp på bolagets balansräkning','Institutioner','strategy',['BTC'],'I detta scenario rapporterar ett bolag ett nytt Bitcoin-köp. Företagets eget besked är huvudkälla, medan Saylor och medier visas som relaterade källor.','Större företagsköp kan påverka efterfrågan. Finansiering och köpets storlek behövs för att bedöma den faktiska betydelsen.','A new corporate Bitcoin treasury purchase',4,'confirmed','Bullish',['Bitcoin','Michael Saylor']],
 ['sui-upgrade','Sui presenterar en uppgradering för snabbare transaktioner','Altcoins','sui',['SUI'],'Ett illustrativt projektbesked om en nätverksuppgradering. Flödet skiljer projektets tekniska påståenden från självständigt verifierade resultat.','Kortare väntetider kan förbättra användningen av nätverket. Effekten på SUI-tokenen är en separat fråga.','Sui introduces a network upgrade',3,'confirmed','Neutral',['SUI','Nätverk']],
 ['eth','Ethereum: nästa steg för skalning av nätverket','Ethereum','ethereum',['ETH'],'Ett exempel på ett officiellt utvecklarbesked om skalning. Förslaget är fortfarande under arbete och ska inte tolkas som en redan genomförd uppgradering.','Lägre kostnader kan underlätta fler användningsområden. Tidsplan och faktisk användning avgör utfallet.','Ethereum developers discuss scaling',3,'confirmed','Neutral',['Ethereum','DeFi']],
 ['fed','Marknaden inväntar nästa besked från Fed','Makro','fed',['BTC','ETH'],'Ett makroexempel som visar hur centralbanksinformation sätts i sammanhang. Inga verkliga räntesiffror eller aktuella prognoser anges i demoflödet.','Räntor och likviditet påverkar ofta viljan att äga riskfyllda tillgångar, däribland kryptovalutor.','Markets await the next Federal Reserve decision',4,'confirmed','Neutral',['Fed','Bitcoin']],
 ['sol','Solana får ett nytt verktyg för institutionella användare','Institutioner','solana',['SOL'],'I detta demoexempel presenterar projektet en produkt för institutioner. En lansering skiljs tydligt från bevis på att produkten används.','Fler verktyg kan sänka tröskeln för institutioner. Det är användningen över tid som visar den praktiska betydelsen.','Solana introduces institutional tooling',3,'confirmed','Bullish',['Solana','Institutioner']],
 ['hack','Uppgifter om säkerhetsincident i ett DeFi-protokoll','Säkerhet / Hacks','coindesk',['ETH'],'Ett övningsscenario med preliminära uppgifter om en incident. Omfattning och orsak är ännu inte verifierade och presenteras därför inte som fakta.','Bekräftade incidenter kan påverka tillit och likviditet. Preliminära förlustuppgifter kan ändras snabbt.','Reports of a DeFi security incident',4,'unconfirmed','Bearish',['DeFi','Säkerhet']],
 ['ondo','Tokeniserade tillgångar: ett nytt produktexempel från Ondo','DeFi','ondo',['ONDO'],'Ett illustrativt besked om tokeniserade tillgångar. Produktens utveckling hålls åtskild från antaganden om värdet på ONDO-tokenen.','En växande produkt kan ha betydelse för sektorn, men skapar inte nödvändigtvis motsvarande värde för tokenägare.','Ondo introduces a tokenized asset product',3,'confirmed','Neutral',['Tokenisering','ONDO']],
 ['rumor','Obekräftade uppgifter om en möjlig börsnotering','Börser','rover',['SUI'],'Ett exempel på ett påstående från sociala medier som saknar ett officiellt besked. Flera konton återger samma ursprungliga uppgift.','En faktisk notering kan påverka tillgänglighet och likviditet. Ryktet i sig visar inte att någon notering är beslutad.','Unverified exchange listing speculation',2,'rumor','Neutral',['SUI','Börser']],
 ['flow','ETF-flöden: en dags rörelse behöver ett längre perspektiv','ETF','blackrock',['BTC','ETH'],'Ett exempel på hur rapporterade fondflöden kan sammanfattas utan att en enskild dags rörelse förväxlas med en långsiktig trend.','Jämförelser över flera dagar och mellan fonder ger en mer rättvisande bild av kapitalflöden.','ETF flows require a longer perspective',3,'confirmed','Neutral',['ETF','Bitcoin','Ethereum']],
 ['hbar','Analytiker diskuterar användningen av Hedera','Altcoins','watcher',['HBAR'],'Ett exempel på marknadskommentar, inte ett verifierat nytt partnerskap. Författarens tolkning hålls separat från bekräftade händelser.','Aktivitet och verklig efterfrågan behöver granskas innan slutsatser om tokenvärdet dras.','Analysts discuss Hedera adoption',2,'unconfirmed','Bullish',['HBAR']],
 ['xrp','Stablecoins och betalningar åter i rampljuset','Stablecoins','bitcoinmag',['XRP'],'Ett illustrativt mediereferat om betalningar och stablecoins. Påståenden om integrationer behöver beläggas av berörda parter.','Betalningsinfrastruktur kan få bredare användning utan att alla relaterade tillgångar påverkas lika mycket.','Stablecoins and payments in focus',3,'unconfirmed','Neutral',['Stablecoins','XRP']],
 ['mining','Bitcoin-mining: energikostnaden påverkar marginalerna','Mining','coindesk',['BTC'],'Ett analysillustrerande exempel om sambandet mellan energikostnader, nätverkets svårighetsgrad och lönsamheten för miners.','Pressade marginaler kan påverka hur mycket Bitcoin miners behöver sälja för att täcka kostnader.','Energy costs affect mining margins',2,'unconfirmed','Neutral',['Bitcoin','Mining']],
 ['onchain','Stor on-chain-rörelse kräver mer kontext','On-chain','watcher',['BTC'],'Ett exempel på en större överföring. Att mynt flyttas mellan adresser betyder inte i sig att någon köper eller säljer.','Interna överföringar och förändrad förvaring kan se ut som stora marknadsrörelser. Adressernas funktion måste först undersökas.','Large on-chain transfer needs context',3,'unconfirmed','Neutral',['Bitcoin','On-chain']],
];
export const demoNews: NewsItem[] = seeds.map((s,i)=>{
 const [id,title,category,sourceId,coins,summary,why,originalTitle,importance,status,sentiment,topics]=s;
 const source=sources.find(x=>x.id===sourceId)!;
 return {id,eventKey:`demo:${id}`,title,category,sourceId,coins,summary,why,originalTitle,importance,status,sentiment,topics,originalText:`Illustrative scenario: ${originalTitle}. Not a real source quotation.`,originalLanguage:'en',translation:summary,author:source.name,publishedAt:new Date(Date.parse(snapshot)-(i===0?4:i*19)*60000).toISOString(),importedAt:snapshot,originalUrl:source.url,sourceType:source.type,evidence:[{sourceId,url:source.url,originId:id,direct:true,verified:status==='confirmed'},...(id==='treasury'?[{sourceId:'saylor',url:'https://x.com/saylor',originId:id,direct:false,verified:false},{sourceId:'bitcoinmag',url:'https://bitcoinmagazine.com',originId:id,direct:false,verified:false}]:[]),...(id==='etf'?[{sourceId:'coindesk',url:'https://www.coindesk.com',originId:id,direct:false,verified:false}]:[])],confidence:status==='confirmed'?92:status==='rumor'?24:56,breaking:i===0,demo:true,analysisMethod:'demo'};
});
export const market: MarketQuote[] = [
 {symbol:'BTC',name:'Bitcoin',price:98432.50,change24h:2.34,marketCap:'1,96 biljoner',series:[19,22,17,24,23,31,27,34,32,42,39,46]},
 {symbol:'ETH',name:'Ethereum',price:3246.18,change24h:1.82,marketCap:'391 miljarder',series:[15,19,17,21,27,24,32,30,35,31,39,41]},
 {symbol:'SOL',name:'Solana',price:186.42,change24h:-0.76,marketCap:'96 miljarder',series:[42,36,40,32,34,27,30,20,25,21,24,18]},
 {symbol:'SUI',name:'Sui',price:3.84,change24h:5.67,marketCap:'13 miljarder',series:[12,15,13,23,20,24,29,27,35,39,36,48]},
 {symbol:'XRP',name:'XRP',price:2.41,change24h:0.92,marketCap:'140 miljarder',series:[20,23,21,27,23,30,32,29,34,37,35,40]},
];
export const categories=['Senaste','Bitcoin','Ethereum','Altcoins','Reglering','Institutionellt','Marknaden'];
