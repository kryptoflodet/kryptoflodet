# Kryptopuls: drift utan betalda API:er

Befintligt repo: kryptoflodet/kryptoflodet.github.io. GitHub Pages används med kryptopuls.se som avsedd anpassad domän.

## Drift

GitHub Actions kontrollerar källor enligt befintligt femminutersschema. GitHub kan senarelägga körningar. Körningar köas, skriver inte över varandra och avbryts efter 12 minuter. Använd standardrunner i det publika repot; inga betalda inference-API:er, större runners eller externa abonnemang behövs. Inga betaluppgifter eller API-nycklar har lagts till.

Varje källa har egen timeout, storleksgräns och felstatus. Misslyckad hämtning raderar inte publicerade artiklar. Läs `public/data/health.json` och källregistret för faktisk senaste hämtning; en lyckad deployment innebär inte att alla källor fungerar. RSS-kandidater äldre än sju dagar sorteras bort, och de nyaste granskas först. Upp till åtta kandidater behandlas per körning; för låg källtext eller misslyckad språk-/faktakontroll lämnas de opublicerade. En tillfällig käll- eller modellmiss ska inte ta bort befintliga artiklar.

Godkända artiklar lagras i `public/data/archive.json`. Actions sparar nya artiklar i git innan deployment; bortfall av runner-cache får därför inte radera permanenta sidor. Rebase/force-push används inte. Vid samtidig kodändring kan push avvisas: nästa körning börjar från ny main. Säkerställ att repo-inställningar tillåter GITHUB_TOKEN att skriva contents (workflow begär behörigheten). Branch protection kan annars stoppa arkivering och därmed publicering.

## Redaktionella regler

Originalets tid bevaras med tidszon. Samma URL normaliseras, spårningsparametrar tas bort; liknande rubriker slås inte ihop till ett påstått verifierat händelsekluster. Endast uttryckligt kryptoinnehåll tas med. Korta RSS-rubriker, reklamdominerade videobeskrivningar och aggregatorlänkar utan underlag publiceras inte.

RSS-insamlingen fortsätter automatiskt, men nya svenska nyhetstexter publiceras först efter manuell språkgranskning mot originalkällan och registrering i `scripts/reviewed.json`. Övriga kandidater sparas i granskningskön. Produktionsflödet använder `EDITOR_MODE=reviewed-only`; maskinöversatta `edited-sv`-texter godkänns aldrig av publiceringsregeln. Detta minskar nyhetsmängden, men hindrar obestyrkta maskinöversättningar från att presenteras som färdig svenska. Varje publicerad nyhet är fortfarande obekräftad om inte artikelns status uttryckligen säger något annat. Granskning av språket är inte oberoende faktagranskning. Originaltexter och källcookies publiceras inte.

“Viktigast just nu” visar upp till fem publicerade nyheter från senaste 48 timmarna. Urvalet är en transparent ämnesheuristik, inte en säker bedömning av marknadspåverkan. Rykten och prognoser lyfts inte där. Dagsöversikterna bygger enbart på godkänt material och kan vara begränsade; gammalt material ges inte dagens datum.

## X / RSSHub

RSSHub-adaptern är valfri och ej ansluten. Direkt visning av originalinlägg använder nu i stället X:s publika inbäddningsdata via scripts/fetch-x.py. WatcherGuru, cryptorover, TheMoonShow, saylor och BitcoinArchive (@BitcoinArchive, konto-ID 970994516357472257) finns i scripts/x-sources.json. Route: `/twitter/user/<handle>/exclude_rts_replies`. RSSHub kräver numera autentiseringsmaterial på sin server för X-routen. GitHub Pages kan inte köra den servern.

Tester 2026-10-12: offentlig rsshub.app-route gav 404; nitter.net RSS gav 410. Därför används inte någon av dem som obligatorisk dependency. Watcher.Gurus egen nyhetssidas RSS fungerar som separat källa. Mediebevakning är inte samma sak som kontots egna X-inlägg.

Om användaren redan har en egen kostnadsfri server kan RSSHub köras där enligt officiell dokumentation. Servern behöver HTTPS och eget skydd. Spara URL i GitHub Secret `RSSHUB_BASE_URL`; aldrig i repo. X-cookies/tokens stannar hos RSSHub och ska aldrig finnas i nyhetsfiler eller loggar. Ingen ny betald server ska beställas för detta projekt. Utan sådan drift lämnas funktionen avstängd och resten fortsätter.

Dokumentation: https://docs.rsshub.app/deploy/ och https://github.com/DIYgod/RSSHub/tree/master/lib/routes/twitter

## Video och marknad

Videor får bara publiceras med tillräckligt textunderlag och svensk sammanfattning. YouTube beskrivningar är inte fullständiga transkript; detta anges på artikelsidan. Tillåtna kanaler och värdnamn kontrolleras innan inbäddning. Felaktiga eller otillgängliga kanaler slår inte ut RSS.

CoinGecko hämtar topp 50 efter marknadsvärde i USD och SEK. Besökarens urval och dragordning sparas lokalt, och valda valutor visas i tickern. Webbläsaren återanvänder ett färskt lokalt svar i en minut; vid API-fel används den publicerade snapshoten. `scripts/fetch-market.py` skriver snapshoten åt GitHub Actions och behåller senast fungerande data om USD-hämtningen misslyckas. SEK-kurser kan återanvändas från föregående snapshot vid ett separat SEK-fel. Föråldrade priser märks i gränssnittet.

Marknadspulsen använder Fear & Greed från Alternative.me, dominans och dygnstrend från CoinGecko Global, BTC/ETH dygnsförändringar från CoinGecko och Altcoin Season från CoinMarketCap med BlockchainCenter som reserv. Senast fungerande indikatorvärden behålls om källorna tillfälligt inte svarar.

## Vidareutveckling

Artikelns stabila `id`, `slug`, `path`, `categories` och källbevis hålls separata från UI. Personliga bokmärken ligger lokalt i webbläsaren. En framtida kontotjänst kan lagra artikel-ID:n utan att flytta publiceringsarkivet. Ingen autentisering eller databas har lagts till nu.

Kör lokalt: `python scripts/fetch-news.py`, `npm ci`, `npm run build`, `npm test`, `python -m unittest discover -s tests -p '*_test.py'`. Modellfilen cachas och kontrolleras med SHA-256; den ska inte committas.

## Modellutvärdering och konkret begränsning

Testat 2026-10-12: Qwen3-1.7B Q8 svarade engelska eller hoppade över användbart underlag. Qwen3-4B-Instruct-2507 Q4 gav bl.a. onaturliga uttryck och en otillräckligt säker text som passerade dess egen kontroll. Qwen3-8B Q4 återgav ett syntetiskt faktatest bättre, men med upprepningar, språkfel och lång CPU-tid. Modellernas egen ja/nej-granskning räcker inte som publiceringsgaranti. Därför är den säkra reservlösningen granskade texter, inte automatisk publicering av dessa förslag.

GitHub Models kontrollerades som möjligt gratisalternativ men har enligt https://docs.github.com/en/github-models lagts ned 30 juli 2026. Ingen integration med denna avvecklade tjänst har byggts. Inga betalda alternativ aktiverades.

Nästa förbättring av språkautomationen behöver en kostnadsfri lösning som klarar en separat svensk utvärderingsmängd och faktagranskning. Behåll reviewed-only tills sådan evidens finns. Ändra inte produktionsläget för att få ett större flöde. Produktionskörningen installerar eller startar inte språkmodellen; lokala modellexperiment får inte godkänna text för publicering.

Kön med källänkar, originalrubriker och publiceringstid sparas som Actions-artifact i tre dagar. Fulla källtexter finns inte i kön. Den hjälper nästa redaktionella genomgång utan att otillräckliga artiklar visas för läsaren. Avancerad automatisk sammanhängande dagsanalys och oberoende flerkällsverifiering är ännu inte implementerade; dagsöversikten är ett deterministiskt urval av granskade artiklar.

## X-inlägg i det gemensamma flödet – drift

X:s egna publika inbäddningsflöden används som kostnadsfri källa. Tester 2026-10-13: `timeline-profile/user-id/<id>` hämtade färska inlägg från Watcher.Guru, Crypto Rover, The Moon Show och Bitcoin Archive. Den alternativa `screen-name/<handle>` hämtade aktuella poster från flera av samma konton när ID-vägen inte svarade. Enskilda statusar fungerade även via X:s publika `tweet-result`-endpoint. Profilflöden kan ändå sakna nya poster eller fastna på äldre, populära inlägg; sådana visas inte som nya.

Hämtningen provar först ett fast konto-ID och sedan kontonamnet när det behövs. Timeout är 20 sekunder och högst tre konton hämtas parallellt. Loggen visar endpoint, feltyp och HTTP-status. Vid fel bevaras tidigare inlägg från Actions-cache. Upp till 30 poster hålls per konto (210 för sju konton), så stora konton inte tränger undan mindre. HTTP 429 följer `Retry-After`; när headern saknas väntar den berörda endpointen 30 minuter. Reservvägarna har egna statusar. Schemat kör var femte minut.

En begränsad komplettering hämtar X-länkar från högst sex aktuella artiklar hos tillåtna RSS-utgivare per körning. Både publicerade och väntande artiklar tas med, inklusive Strategy/MSTR-rubriker. Artikellänkar cachas ett dygn. Varje konto får en egen budget om högst två enskilda post-ID:n som kontrolleras mot X; aldrig mot sekundärkällans omskrivning. Artikelhämtning och postkontroller körs högst tre parallellt. Den kontrollerade avsändaren och publiceringstiden måste matcha. Detta är ofullständig upptäckt, vilket även källregistret och metodbeskrivningen upplyser om.

public/data/x.json innehåller aktuella originalposter, källstatus och metadata för upptäckt. GitHub Actions cachar urvalet separat; ett källfel tar inte bort senast hämtade aktuella poster. X-korten blandas kronologiskt med artiklarna. Svenska visas först, originalet fälls ut lokalt med Visa original. Ingen widget laddas. Varje X-kort visar en lazy-loadad originalbild från pbs.twimg.com när sådan finns, annars en lokal ämnesillustration. Bildfel ger samma lokala reservbild. Illustrationen märks tydligt och originaltexten kan fortfarande fällas ut. Inget X-konto eller X-token används. X-påståenden räknas aldrig automatiskt som bekräftade nyheter och visas inte av filtren Viktigt/Endast bekräftat. Vanliga kategori-, coin-, sök-, sorterings- och bokmärkesfunktioner omfattar korten.

X kan ändra eller begränsa inbäddningsformatet. Kontrollera data/x.json och Actions-loggen vid bortfall. En publik X-status renderades i Chrome utan inloggning. RSSHub gav 404, nitter.net 410, nitter.poast.org 502, xcancel 451 och FxTwitter/vxTwitter 403. Den lokala Playwright Chromium-nedladdningen var trasig, så automatisk skärmdump via GitHub Actions är inte verifierad och har inte lagts till. Kortens X-media och fungerande lokala illustrationsbilder fortsätter användas. Försök inte kringgå inloggning, botkontroller eller åtkomstspärrar. Ordinarie RSS, marknadskurser och artikelarkiv fortsätter oberoende.


## Permanenta X-länkar

MMCrypto är låst till konto-ID `904700529988820992`, verifierat mot X:s egna originaldata. Tester 2026-10-13: Saylors och MMCryptos profilflöden visade gamla populära poster, medan aktuella statusar fungerade via `tweet-result`. Därför är profilflödet och reservhämtningen separata i statusen. En fungerande reservväg märks `Begränsat urval`; den innebär inte fullständig bevakning.

`python scripts/x_archive.py` sparar X-original, inklusive poster som ännu saknar svensk text i `public/data/x-archive.json`. Arkivet och genererade sidor på `/x/<post-id>/` bevaras när poster lämnar 14-dagarsflödet. Kopiera länk använder den permanenta Kryptopuls-sidan, som har egen canonical/Open Graph och en länk till originalposten. Tidigare `?xpost=<id>`-länkar öppnar den permanenta sidan när den finns. Saknad post får ett tydligt meddelande och en säker länk till X. Arkivering kräver rätt post-URL och giltigt original. Svenska texter kräver dessutom exakt språkhash; en felaktig språkhash tar bort översättningen, inte den riktiga originalposten. Gamla texter återpubliceras inte som nya.

## Svenska X-texter

`python scripts/x_language.py` körs efter insamlingen och före bygget. `scripts/x-summaries.json` återanvänds för källbundna svenska texter (översättning eller sammanfattning). En granskning gäller endast exakt SHA-256 av originalet och samma käll-URL; ändrade/indragna texter återanvänds inte från cache. Originalfältet `text` ändras aldrig. Svenska original visas oförändrade.

Automatiken är avsiktligt begränsad: endast hela, entydiga formuleringar som matchar svenska språkregler kan översättas automatiskt. Alla andra engelska inlägg ligger kvar i flödet med originalet tillgängligt och märkningen **Svensk översättning inväntar granskning**. Maskinmodellerna NLLB och MyMemory används inte längre för att skriva svensk text till publicering; de gav svengelska och felaktiga facktermer trots beloppskontroller. X-inlägg, konton, filter, delningssidor och automatisk hämtning är kvar.

`x_archive.py` sparar bara svenska original, granskade översättningar och texter från de fasta språkreglerna. Vid varje körning tas gamla oaccepterade maskinöversättningar bort ur arkivet, medan X-originalet och permanenta länkar bevaras. X-påståenden är fortfarande kontots egna uppgifter, inte oberoende bekräftelser. Språkgranskningskön sparas tillsammans med övriga granskningsärenden i Actions-artifact `editorial-review-queue`.

## Svenska nyhetstexter

Endast manuellt språkgranskade nyhetstexter från `scripts/reviewed.json` kan publiceras. `scripts/swedish_quality.py` stoppar dessutom vissa kända felöversättningar som en extra spärr. Nya RSS-kandidater läggs i granskningskön tills rubrik och sammanfattning har kontrollerats mot originalet. Marknadsdata, X-hämtning, källinsamling och övriga nyhetsfunktioner fortsätter automatiskt. Språkgranskning innebär inte oberoende faktabekräftelse; detta framgår av artikelns källnotis.


## Praktisk kontroll 2026-10-13: synliga X-poster

Det gamla språksteget dolde 58 av 100 originalposter. CryptoKid saknades i konfigurationen. `@CryptoKid` är nu låst till X-ID `1443582062963822599`; dess publika profil visade endast gamla populära poster. TwStalker levererade däremot aktuella postlänkar för CryptoKid och MMCrypto. Spegeltext publiceras aldrig som original: varje ID kontrolleras via X:s egen endpoint mot fast avsändar-ID, datum, innehåll och reklam/reply-regler. Dubbla fotnotlänkar får inte felaktigt ärva nästa korts text. Spegelreferenser cachas i 30 minuter; även en ansluten profil kan använda denna reserv när dess senaste synliga post är över 90 minuter gammal. RSS-artikelreferenser och sparade original finns kvar som andra reserver.

Kör `python scripts/fetch-x.py`, `python scripts/x_language.py`, `python scripts/x_archive.py`, sedan bygget och testerna. X-flödet ska behålla originalposten även när svensk text ännu inte kan godkännas.
