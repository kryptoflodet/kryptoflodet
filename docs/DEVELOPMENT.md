# Kryptopuls – utvecklingslogg

## Uppdrag 12 oktober 2026
Befintligt repo kryptoflodet/kryptoflodet.github.io. Inga extra API-kostnader. GitHub Pages används med kryptopuls.se som avsedd domän.

## Implementerat och lokalt testat
- Isolerad RSS/Atom-insamling, tidszoner, framtidskontroll, storleksgräns och felstatus.
- URL-normalisering och dubletter; källans ursprung och uppgiftstyp bevaras.
- Publiceringsgrind: tillräcklig svensk egen text och granskning krävs. Modellförslag publiceras aldrig automatiskt.
- Beständigt nyhetsarkiv och verkliga /nyheter/.../ HTML-sidor.
- Åtta kategorier, fler kategorier per artikel, egna kategoriarkiv.
- Viktigast just nu (högst fem från senaste 48h, inga utfyllnadsnyheter).
- Varför är detta viktigt, originalkälla, tydlig osäkerhet och videoinbäddning med tillåtna källor.
- Daterade dagsöversikter av granskade poster, SEO, canonical, OG, JSON-LD, sitemap och robots.
- Femminutersschema, tester före publicering, arkivering före deployment och kö som Actions-artifact.
- Marknadsöversikten hämtar CoinGeckos 50 största kryptovalutor. Besökaren väljer valutor och drar raderna till önskad ordning; valda valutor syns även i tickern. Marknadspulsen visar Fear & Greed, Altcoin Season, BTC-dominans, BTC jämfört med ETH och marknadstrend direkt under Marknaden live.

## Avsiktliga begränsningar
Tidigare kontrollpunkt: direkt X-import var inte ansluten (ersatt av lösningen nedan). Publik RSSHub gav 404 och Nitter 410; valfri egen RSSHub-adapter finns för fyra konton. Den kräver ingen betald X API, men en fungerande server och RSSHub-autentisering saknas. Resten fungerar utan den.

Tre fria lokala Qwen-modeller utvärderades: 1.7B, 4B Instruct och 8B. Alla gav språkproblem eller osäkra fakta i prov. 8B hittade dessutom på en inflationsuppgift i ett test om ett försäkringsbolag; källstödsgrinden avvisade den. En 4B-text passerade modellens egen kontroll trots tydliga språkfel och togs bort före publicering. Därför är produktionsläget reviewed-only. Experimentmodulen är till för lokala utkast. GitHub Models har avvecklats och används inte. Betalda tjänster har inte aktiverats.

Automatisk naturlig svensk nyhetsskrivning och oberoende flerkällskontroll är således inte lösta. Dagsöversikten är ett försiktigt sammanställt urval, inte en komplett generativ dagsanalys. Aktuella YouTube-flöden svarade HTTP-fel vid test; fungerande flöden påverkas inte, och videor utan tillräckligt textunderlag publiceras inte.

## Aktiv kontrollpunkt
Publicerat: commit a7cea3d5f5387f73266f4567c3002034e67c61a3. GitHub Actions-körning 38231790878 slutfördes med success, inklusive insamling, marknadsdata, bygge, alla frontendtester, 19 Python-tester och Pages-deployment.

Historisk livekontroll 12 oktober 2026 före domänbytet: produktionssajten svarade HTTP 200 och den ursprungliga GitHub Pages-adressen omdirigerades korrekt. Nyhets-JSON visade schemaVersion 2, tre granskade artiklar och reviewed-only. Senaste kontrollerade hämtning 10:29 UTC nådde 22 av 24 aktiva källor; 219 kandidater hölls tillbaka. Sui-artikeln, /kategori/sui/, /idag/ och /sitemap.xml svarade 200. Alla interna länkar i 16 genererade HTML-sidor validerades före publicering.

Visuell desktop-/mobilkontroll är INTE slutförd: molnwebbläsaren fastnade med timeout och lokala browserbinärer kunde inte installeras. Inga påståenden om visuellt godkänd mobilvy görs. Nästa konkreta steg är visuell kontroll vid 390 och 1440 px och därefter fortsatt utvärdering av gratis språkhantering. Drift och beständiga artikelsidor är publicerade; full automatisk redaktion är inte färdig.

## Återuppta
Fortsätt från aktuell releasegren. Kontrollera git status, senaste remote main och denna logg. Förbättra språkautomationen endast med en gratis metod som klarar en separat svensk kvalitetsutvärdering. Slå inte på automatisk publicering av nuvarande modellförslag. Läs docs/OPERATIONS.md för begränsningar och drift. Automatisk återstart av ChatGPT efter användningsgräns kan inte garanteras; inga försök att kringgå gränser ska göras.

## X-inlägg – uppföljning 12 oktober

Ny fungerande väg: X:s offentliga inbäddningsdata, utan konto, cookies eller betalt API. Testet hämtade 44 kryptorelevanta originalinlägg. Avsändarens numeriska konto-ID, användarnamn och originalets publiceringstid valideras. Ovidkommande innehåll, svar, retweets, uppenbar reklam, framtida datum och inlägg äldre än 14 dagar sorteras bort. Gamla pinnade/populära inlägg används inte som nya.

Crypto Rovers aktuella konto är @cryptorover, bekräftat av hans egen webbplats crypto-rover.com. @rovercrc är borttaget ur anslutningen. WatcherGuru, TheMoonShow och cryptorover gav aktuella profiler. Saylors profil gav gamla populära inlägg; för honom används dessutom riktiga X-länkar från nyhetsartiklar, vars text, avsändare och tid därefter hämtas från X:s enskilda inbäddningsdata. Ett aktuellt Saylor-inlägg kunde verifieras. Detta ger begränsad bevakning, inte ett komplett kronologiskt flöde.

Startsidan visar nu en Från X-del direkt i nyhetsflödet, med filter för de fyra kontona, originaltext som reserv och X:s egna inbäddningar. Dessa är tydligt märkta originalinlägg på originalspråket och räknas inte som granskade svenska nyhetsartiklar. Ursprungliga bilder visas även om widgets inte fungerar. Ingen svensk automatiserad text publiceras genom denna väg.

Insamlingen körs efter RSS i befintlig Pages-workflow. X-fel hålls separata, senaste urval cachas och utgivna nyhetsartiklar påverkas inte. 26 Python-tester och befintliga frontendtester passerar. Kontrollera aktuell release efter push.

Översättning: inte löst. Google dokumenterar en Gemini API-gratisnivå även i EU, men den kräver en API-nyckel för ett projekt utan aktiverad fakturering. Ingen nyckel finns ansluten här, inga faktureringsinställningar har ändrats och ingen otestad integration har slagits på. Det är ett möjligt nästa försök; kvalitet och kvot måste testas innan automatisk publicering.

X-release publicerad i commit 4bb234c39b8d41faaadfbc28a6d2764f2db9654b. Actions 38242365778 slutfördes med success, inklusive 26 Python-tester, frontendtester och Pages. X:s oEmbed svarade 200 och gav giltig native embed-markup för ett hämtat Watcher.Guru-inlägg. Ingen betald API eller autentisering användes.

Sju aktuella originalinlägg har fått separat skrivna svenska sammanfattningar, kontrollerade mot den hämtade originaltexten. De är inte oberoende faktagranskningar. scripts/x-summaries.json binder varje sammanfattning till exakt källtext med SHA-256 och ursprungs-URL; ändrad text tar bort sammanfattningen tills ny kontroll gjorts. Detta löser läsbarheten för dessa sju inlägg men är inte löpande automatisk översättning.


## Kontrollpunkt: svenska X-kort i samma flöde (12 oktober 2026)

Ersätter ovanstående Från X-sektion och sjutextslösning. 68 aktuella originalposter har svenska versioner: 65 källbundna granskade texter och 3 från fullt matchade automatiska språkregler. Svenska visas först, originalet kan fällas ut utan att lämna sidan; konto, svensk publiceringstid och direktlänk till X finns kvar. Inga separata X- eller SUI/Solana-flikar har lagts till. X och artiklar använder samma kronologiska lista, sökning, filter, sidvisning och bokmärken. Gamla reservposter äldre än 14 dagar döljs.

Automatisk språkhantering använder begränsade fullständigt matchade regler; övriga nya texter kräver granskning. Två gratis översättningsmodeller testades men gav betydelsefel. Detta är **inte** en generell självgående AI-översättare. Se OPERATIONS.md för exakt gräns och nästa steg. Inga betalda API:er, nya hemligheter eller modellnedladdningar i produktionsflödet.

Verifiering före publicering: byggtest, befintliga frontendtester, nya tester för blandat flöde och språkgrind. Lokal riktig webbläsare kunde inte installeras (Playwright-nedladdningen gav en trasig zip); ingen fullständig visuell desktop-/mobilgranskning påstås. Interaktionskontroller i DOM körs separat. Publicera till main med villkorad ref-uppdatering och följ Pages-körningen; kontrollera därefter live x.json och den publicerade appen.


Första svenska UI-releasen publicerades i commit 0d754d0e07e0abc38a47f1a4c2bf7b122060c899, Actions 38270215898: success i samtliga steg inklusive Pages. Livekontroll gav HTTP 200 för startsida, x.json, news.json, JS och befintlig artikel. Gemensamt flöde och svenska etiketter finns i publicerad kod; den gamla X-sektionen/widgeten är borta. Den körningen hämtade 24 ytterligare poster, vilka hölls i språkgranskningskö. De har nu bearbetats (21 källbundna texter samt 3 explicit formulerade köpnotiser som nya testade regler klarar). För testurvalet innan den femte källan lades till var kön tom. Nya okända formuleringar kommer fortfarande att behöva granskas. Fortsättning: bredare tillförlitlig gratis språkmodell och full visuell mobil-/desktopkontroll; befintlig begränsad automatisk språkhantering får inte beskrivas som komplett AI-översättning.


## Bitcoin Archive och bilder i X-korten (12 oktober 2026)

Bitcoin Archive (@BitcoinArchive) har lagts till som femte X-källa. X:s offentliga profildata angav konto-ID 970994516357472257. Handtaget och ID:t matchades mot 15 aktuella kryptorelevanta originalinlägg. De har fått sammanfattningar/översättningar knutna till exakt posttext och käll-URL; nya inlägg går genom samma språkgrind som övriga poster. Därmed har 83 poster i det aktuella testurvalet svenska texter.

Varje X-kort visar nu bildmaterial: godkänd X-originalbild från `pbs.twimg.com` när posten har en, annars en ämnesillustration från befintliga lokala bilder. Om originalbilden inte går att hämta visas den lokala illustrationen. Bildtexten anger tydligt om det är en originalbild eller illustration. Reserverad aspect-ratio och lazy loading minskar layoutskift och onödig nätverkstrafik; originalbilder begränsas till godkänd X-host. Mobil och desktop använder samma komponent med olika bildbredd.

## Kryptopuls: överblick på 30 sekunder (14 oktober 2026)

Utgår från befintlig main, utan byte av repo, ramverk, tema eller nyhets-/X-insamling. Audit: React/Vite på statiska Pages; CoinGecko topp 50, webbläsarcache och Actions-reserv; Alternative.me och CMC/BlockchainCenter i befintlig context-insamling; blandat RSS/X-flöde; svenska RSS-artiklar kräver redaktionell granskning, X använder lokal automatöversättning och gratis reserv. Bevarad backend körs inte på Pages. Befintlig Actions publicerar efter bygge och tester. Marknadstabellen är fortsatt dold på mobil i stående läge. Light/Dark använder befintliga CSS-variabler. Ingen kalender eller ordlista fanns i aktuell main; denna ändring lägger till en kompakt kommande-del, ingen ny ordlistesida.

Befintlig MarketPulse utökas med totalmarknad, dominans, volym och fast viktad poäng. Befintliga index fälls ut med källor, observationstider och metodik. Poängen kräver alla tre färska värden: Fear & Greed 50 %, BTC 24h 25 %, totalmarknad 24h 25 %. Saknade/äldre värden omviktas inte och ger ingen poäng. Marknadsvärde/volym läses från samma CoinGecko Global-svar och bevaras i samma cache. Ingen extra API eller hemlighet behövs.

MarketBrief på ofiltrerad startsida använder Stockholms klockslag, BTC/ETH och första synliga altcoin enligt sparad marknadsordning. Nyhetsurvalet är högst tre granskade, ej demo/ryktesposter från senaste 48h. Varför-sektionen är ett deterministiskt ämnesurval av aktuella granskade nyheter, inte kausal analys; inga antagna ETF-/likvidationssiffror eller AI-genererade orsaker. Det kan saknas tillräckligt nyhetsunderlag.

Kommande datum är ett litet källkontrollerat urval från Fed/BLS med direktlänkar, svensk tid, datumkontroll och automatisk utfasning när händelsen passerat. Fed-möten visas utan obekräftade klockslag. Registret är redaktionellt, inte en självgående kalenderimport; coin-specifika datum har inte hittats på. Lägg endast in sådana efter verifiering hos projektets primärkälla.

Verifiering: TypeScript/produktionsbygge, befintliga frontendtester, nya beräknings-/freshness-/datumtester samt Python-insamlingstester. Full visuell browserkontroll är inte genomförd i denna miljö; mobilregler och temavariabler kontrolleras i kod och komponenternas beteende i DOM.
