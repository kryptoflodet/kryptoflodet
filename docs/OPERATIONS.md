# Kryptokollen: drift utan betalda API:er

Befintligt repo: kryptoflodet/kryptoflodet.github.io. Behåll GitHub Pages och den befintliga domäninställningen för kryptokollen.online.

## Drift

GitHub Actions kontrollerar källor enligt befintligt femminutersschema. GitHub kan senarelägga körningar. Körningar köas, skriver inte över varandra och avbryts efter 12 minuter. Använd standardrunner i det publika repot; inga betalda inference-API:er, större runners eller externa abonnemang behövs. Inga betaluppgifter eller API-nycklar har lagts till.

Varje källa har egen timeout, storleksgräns och felstatus. Misslyckad hämtning raderar inte publicerade artiklar. Läs `public/data/health.json` och källregistret för faktisk senaste hämtning; en lyckad deployment innebär inte att alla källor fungerar. RSS-kandidater äldre än sju dagar sorteras bort, och de nyaste granskas först. Upp till åtta kandidater behandlas per körning; för låg källtext eller misslyckad språk-/faktakontroll lämnas de opublicerade. En tillfällig käll- eller modellmiss ska inte ta bort befintliga artiklar.

Godkända artiklar lagras i `public/data/archive.json`. Actions sparar nya artiklar i git innan deployment; bortfall av runner-cache får därför inte radera permanenta sidor. Rebase/force-push används inte. Vid samtidig kodändring kan push avvisas: nästa körning börjar från ny main. Säkerställ att repo-inställningar tillåter GITHUB_TOKEN att skriva contents (workflow begär behörigheten). Branch protection kan annars stoppa arkivering och därmed publicering.

## Redaktionella regler

Originalets tid bevaras med tidszon. Samma URL normaliseras, spårningsparametrar tas bort; liknande rubriker slås inte ihop till ett påstått verifierat händelsekluster. Endast uttryckligt kryptoinnehåll tas med. Korta RSS-rubriker, reklamdominerade videobeskrivningar och aggregatorlänkar utan underlag publiceras inte.

Nya artiklar från tillåtna medier och officiella utgivare kan sammanfattas automatiskt med den lokala Qwen-modellen (`EDITOR_MODE=local-validated`). Den föreslår två svenska stycken. Deterministiska kontroller granskar språk, siffror och omfattande kopiering; en andra modellpassage granskar texten mot källunderlaget. Detta är **inte oberoende faktagranskning** och kan missa fel. Om kontrollerna underkänner en kandidat publiceras den inte. Källor med kort eller otillräckligt textunderlag ligger kvar i granskningskön. Nyheter märks rapportering, uttalande, analys, prognos eller rykte. Bekräftad status ges endast åt manuellt granskade besked i `scripts/reviewed.json`. Originaltexter och källcookies publiceras inte.

“Viktigast just nu” visar upp till fem publicerade nyheter från senaste 48 timmarna. Urvalet är en transparent ämnesheuristik, inte en säker bedömning av marknadspåverkan. Rykten och prognoser lyfts inte där. Dagsöversikterna bygger enbart på godkänt material och kan vara begränsade; gammalt material ges inte dagens datum.

## X / RSSHub

RSSHub-adaptern är valfri och ej ansluten. Direkt visning av originalinlägg använder nu i stället X:s publika inbäddningsdata via scripts/fetch-x.py. WatcherGuru, cryptorover, TheMoonShow, saylor och BitcoinArchive (@BitcoinArchive, konto-ID 970994516357472257) finns i scripts/x-sources.json. Route: `/twitter/user/<handle>/exclude_rts_replies`. RSSHub kräver numera autentiseringsmaterial på sin server för X-routen. GitHub Pages kan inte köra den servern.

Tester 2026-10-12: offentlig rsshub.app-route gav 404; nitter.net RSS gav 410. Därför används inte någon av dem som obligatorisk dependency. Watcher.Gurus egen nyhetssidas RSS fungerar som separat källa. Mediebevakning är inte samma sak som kontots egna X-inlägg.

Om användaren redan har en egen kostnadsfri server kan RSSHub köras där enligt officiell dokumentation. Servern behöver HTTPS och eget skydd. Spara URL i GitHub Secret `RSSHUB_BASE_URL`; aldrig i repo. X-cookies/tokens stannar hos RSSHub och ska aldrig finnas i nyhetsfiler eller loggar. Ingen ny betald server ska beställas för detta projekt. Utan sådan drift lämnas funktionen avstängd och resten fortsätter.

Dokumentation: https://docs.rsshub.app/deploy/ och https://github.com/DIYgod/RSSHub/tree/master/lib/routes/twitter

## Video och marknad

Videor får bara publiceras med tillräckligt textunderlag och svensk sammanfattning. YouTube beskrivningar är inte fullständiga transkript; detta anges på artikelsidan. Tillåtna kanaler och värdnamn kontrolleras innan inbäddning. Felaktiga eller otillgängliga kanaler slår inte ut RSS.

Befintlig CoinGecko-marknadsöversikt och dess reservdata behålls. Ingen Fear & Greed eller ny marknadsleverantör har lagts till utan stabilitetsbehov. Föråldrade priser märks enligt befintlig kod.

## Vidareutveckling

Artikelns stabila `id`, `slug`, `path`, `categories` och källbevis hålls separata från UI. Personliga bokmärken ligger lokalt i webbläsaren. En framtida kontotjänst kan lagra artikel-ID:n utan att flytta publiceringsarkivet. Ingen autentisering eller databas har lagts till nu.

Kör lokalt: `python scripts/fetch-news.py`, `npm ci`, `npm run build`, `npm test`, `python -m unittest discover -s tests -p '*_test.py'`. Modellfilen cachas och kontrolleras med SHA-256; den ska inte committas.

## Modellutvärdering och konkret begränsning

Testat 2026-10-12: Qwen3-1.7B Q8 svarade engelska eller hoppade över användbart underlag. Qwen3-4B-Instruct-2507 Q4 gav bl.a. onaturliga uttryck och en otillräckligt säker text som passerade dess egen kontroll. Qwen3-8B Q4 återgav ett syntetiskt faktatest bättre, men med upprepningar, språkfel och lång CPU-tid. Modellernas egen ja/nej-granskning räcker inte som publiceringsgaranti. Därför är den säkra reservlösningen granskade texter, inte automatisk publicering av dessa förslag.

GitHub Models kontrollerades som möjligt gratisalternativ men har enligt https://docs.github.com/en/github-models lagts ned 30 juli 2026. Ingen integration med denna avvecklade tjänst har byggts. Inga betalda alternativ aktiverades.

Nästa förbättring av språkautomationen behöver en kostnadsfri lösning som klarar en separat svensk utvärderingsmängd och faktagranskning. Behåll reviewed-only tills det finns sådan evidens. Ändra inte bara en flagga för att få ett större flöde. Kör `pip install -r scripts/editor-requirements.txt` och `EDITOR_MODE=draft python scripts/fetch-news.py` för experiment; produktionskörningen installerar inte modellen och påverkas inte av modellserverns tillgänglighet.

Kön med källänkar, originalrubriker och publiceringstid sparas som Actions-artifact i tre dagar. Fulla källtexter finns inte i kön. Den hjälper nästa redaktionella genomgång utan att otillräckliga artiklar visas för läsaren. Avancerad automatisk sammanhängande dagsanalys och oberoende flerkällsverifiering är ännu inte implementerade; dagsöversikten är ett deterministiskt urval av granskade artiklar.

## X-inlägg i det gemensamma flödet – drift

X:s egna publika inbäddningsflöden används som kostnadsfri källa. Tester 2026-10-13: `timeline-profile/user-id/<id>` hämtade färska inlägg från Watcher.Guru, Crypto Rover, The Moon Show och Bitcoin Archive. Den alternativa `screen-name/<handle>` hämtade aktuella poster från flera av samma konton när ID-vägen inte svarade. Enskilda statusar fungerade även via X:s publika `tweet-result`-endpoint. Profilflöden kan ändå sakna nya poster eller fastna på äldre, populära inlägg; sådana visas inte som nya.

Hämtningen provar först ett fast konto-ID och sedan kontonamnet när det behövs. Timeout är 20 sekunder och högst tre konton hämtas parallellt. Loggen visar endpoint, feltyp och HTTP-status. Vid fel bevaras tidigare inlägg från Actions-cache. Upp till 30 poster hålls per konto och 180 totalt, så stora konton inte tränger undan mindre. HTTP 429 följer `Retry-After`; när headern saknas väntar den berörda endpointen 30 minuter. Reservvägarna har egna statusar. Schemat kör var femte minut.

En begränsad komplettering hämtar X-länkar från högst sex aktuella artiklar hos tillåtna RSS-utgivare per körning. Både publicerade och väntande artiklar tas med, inklusive Strategy/MSTR-rubriker. Artikellänkar cachas ett dygn. Varje konto får en egen budget om högst två enskilda post-ID:n som kontrolleras mot X; aldrig mot sekundärkällans omskrivning. Artikelhämtning och postkontroller körs högst tre parallellt. Den kontrollerade avsändaren och publiceringstiden måste matcha. Detta är ofullständig upptäckt, vilket även källregistret och metodbeskrivningen upplyser om.

public/data/x.json innehåller aktuella originalposter, källstatus och metadata för upptäckt. GitHub Actions cachar urvalet separat; ett källfel tar inte bort senast hämtade aktuella poster. X-korten blandas kronologiskt med artiklarna. Svenska visas först, originalet fälls ut lokalt med Visa original. Ingen widget laddas. Varje X-kort visar en lazy-loadad originalbild från pbs.twimg.com när sådan finns, annars en lokal ämnesillustration. Bildfel ger samma lokala reservbild. Illustrationen märks tydligt och originaltexten kan fortfarande fällas ut. Inget X-konto eller X-token används. X-påståenden räknas aldrig automatiskt som bekräftade nyheter och visas inte av filtren Viktigt/Endast bekräftat. Vanliga kategori-, coin-, sök-, sorterings- och bokmärkesfunktioner omfattar korten.

X kan ändra eller begränsa inbäddningsformatet. Kontrollera data/x.json och Actions-loggen vid bortfall. En publik X-status renderades i Chrome utan inloggning. RSSHub gav 404, nitter.net 410, nitter.poast.org 502, xcancel 451 och FxTwitter/vxTwitter 403. Den lokala Playwright Chromium-nedladdningen var trasig, så automatisk skärmdump via GitHub Actions är inte verifierad och har inte lagts till. Kortens X-media och fungerande lokala illustrationsbilder fortsätter användas. Försök inte kringgå inloggning, botkontroller eller åtkomstspärrar. Ordinarie RSS, marknadskurser och artikelarkiv fortsätter oberoende.


## Permanenta X-länkar

MMCrypto är låst till konto-ID `904700529988820992`, verifierat mot X:s egna originaldata. Tester 2026-10-13: Saylors och MMCryptos profilflöden visade gamla populära poster, medan aktuella statusar fungerade via `tweet-result`. Därför är profilflödet och reservhämtningen separata i statusen. En fungerande reservväg märks `Begränsat urval`; den innebär inte fullständig bevakning.

`python scripts/x_archive.py` sparar läsbara svenska X-poster i `public/data/x-archive.json`. Arkivet och genererade sidor på `/x/<post-id>/` bevaras när poster lämnar 14-dagarsflödet. Kopiera länk använder den permanenta Kryptokollen-sidan, som har egen canonical/Open Graph och en länk till originalposten. Tidigare `?xpost=<id>`-länkar öppnar den permanenta sidan när den finns. Saknad post får ett tydligt meddelande och en säker länk till X. Arkivering kräver rätt post-URL och exakt språkhash; gamla texter återpubliceras inte som nya.

## Svenska X-texter

`python scripts/x_language.py` körs efter insamlingen och före bygget. `scripts/x-summaries.json` återanvänds för källbundna svenska texter (översättning eller sammanfattning). En granskning gäller endast exakt SHA-256 av originalet och samma käll-URL; ändrade/indragna texter återanvänds inte från cache. Originalfältet `text` ändras aldrig. Svenska original visas oförändrade.

Automatiken är avsiktligt begränsad: fullständigt matchade engelska formuleringar för prisnivåer, kursmål, uttryckliga prognoser, ETF-flöden och uttryckliga köpnotiser om Strategy/BitMine kan återges med naturliga, fasta svenska språkregler och korrekt talformat. Hela inlägget måste passa, inklusive varje mening. Okända påståenden, varningar eller extra förbehåll stoppas; ingen mening kapas bort för att få igenom en post. Korta inlägg översätts; längre godkända texter återges i 1–3 meningar. En generell automatisk sammanfattare för alla typer av inlägg är **inte** aktiverad.

Inlägg utan godkänd svensk text sparas i `public/data/x.json` och `state/x-language-review.json`, men visas inte i det svenska flödet. Kön följer med Actions-artifact `editorial-review-queue`. Fältet `language` i x.json visar räknare för original/reviewed/automatic/pending. Ingen betald tjänst eller extra API-nyckel används. Inga nya modellpaket behöver installeras i produktionskörningen.

Två lokala gratis alternativ prövades på 44 faktiska X-texter: befintlig Argos en_sv 1.5 och OPUS-MT en-sv (Helsinki-NLP, CTranslate2-konvertering Sams200, revision 0e1787c21c03d475b53ee417c92d2849375edba1). Båda underkändes på naturlighet och betydelse; bland annat blev stora belopp fel och centrala facktermer förvanskades. Därför får ingen av dem automatiskt publicera X-text. Nästa steg för bredare automatisering är att utvärdera en bättre kostnadsfri språkmodell mot dessa fall, inklusive oberoende kvalitetsgranskning, före aktivering.
