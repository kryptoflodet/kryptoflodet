# Kryptokollen: drift utan betalda API:er

Befintligt repo: kryptoflodet/kryptoflodet.github.io. Behåll GitHub Pages och den befintliga domäninställningen för kryptokollen.online.

## Drift

GitHub Actions kontrollerar källor enligt befintligt femminutersschema. GitHub kan senarelägga körningar. Körningar köas, skriver inte över varandra och avbryts efter 12 minuter. Använd standardrunner i det publika repot; inga betalda inference-API:er, större runners eller externa abonnemang behövs. Inga betaluppgifter eller API-nycklar har lagts till.

Varje källa har egen timeout, storleksgräns och felstatus. Misslyckad hämtning raderar inte publicerade artiklar. Läs `data/health.json` och källregistret för faktisk senaste hämtning; en lyckad deployment innebär inte att alla källor fungerar. Om språkmodellen eller dess nedladdning misslyckas kan befintliga godkända artiklar fortfarande publiceras. Om inga godkända artiklar finns avbryts körningen och tidigare sajt ligger kvar.

Godkända artiklar lagras i `public/data/archive.json`. Actions sparar nya artiklar i git innan deployment; bortfall av runner-cache får därför inte radera permanenta sidor. Rebase/force-push används inte. Vid samtidig kodändring kan push avvisas: nästa körning börjar från ny main. Säkerställ att repo-inställningar tillåter GITHUB_TOKEN att skriva contents (workflow begär behörigheten). Branch protection kan annars stoppa arkivering och därmed publicering.

## Redaktionella regler

Originalets tid bevaras med tidszon. Samma URL normaliseras, spårningsparametrar tas bort; liknande rubriker slås inte ihop till ett påstått verifierat händelsekluster. Endast uttryckligt kryptoinnehåll tas med. Korta RSS-rubriker, reklamdominerade videobeskrivningar och aggregatorlänkar utan underlag publiceras inte.

**Produktionsläget är reviewed-only.** Insamlingen går automatiskt, men en ny svensk artikel kräver en granskad post i scripts/reviewed.json. Lokal AI-publicering är avstängd efter underkända kvalitetstester. `EDITOR_MODE=draft` kan skapa lokala förslag i `.cache/editor/drafts.json`; dessa publiceras aldrig direkt. Den lokala Qwen-modellen föreslår två korta svenska stycken. Kontroller granskar språk, siffror, källstöd, omfattande kopiering och därefter faktatrohet i en andra modellpassage. Detta är **inte oberoende faktagranskning** och kan missa fel. Nyheter märks rapportering, uttalande, analys, prognos eller rykte. Bekräftad status ges endast åt manuellt granskade besked i reviewed.json, inte på grund av ett varumärke eller flera likadana länkar. Originaltexter och källcookies publiceras inte.

“Viktigast just nu” visar upp till fem publicerade nyheter från senaste 48 timmarna. Urvalet är en transparent ämnesheuristik, inte en säker bedömning av marknadspåverkan. Rykten och prognoser lyfts inte där. Dagsöversikterna bygger enbart på godkänt material och kan vara begränsade; gammalt material ges inte dagens datum.

## X / RSSHub

RSSHub-adaptern är valfri och ej ansluten. Direkt visning av originalinlägg använder nu i stället X:s publika inbäddningsdata via scripts/fetch-x.py. WatcherGuru, cryptorover, TheMoonShow och saylor finns i scripts/x-sources.json. Route: `/twitter/user/<handle>/exclude_rts_replies`. RSSHub kräver numera autentiseringsmaterial på sin server för X-routen. GitHub Pages kan inte köra den servern.

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

## Från X – drift

X:s egna publika inbäddningsflöden används som kostnadsfri källa. De lämnar inte nödvändigtvis ut alla poster eller de senaste posterna. Särskilt Saylor kan ge gamla populära inlägg. Kontonas fasta numeriska ID:n valideras så att ett ändrat användarnamn inte kan byta avsändare obemärkt. Endast relevanta originalinlägg inom 14 dagar visas.

En begränsad komplettering hämtar X-länkar från högst tre aktuella artiklar hos tillåtna RSS-utgivare per körning. Artikellänkar cachas ett dygn. Upp till åtta nya post-ID:n kontrolleras mot X; aldrig mot sekundärkällans omskrivning. Den kontrollerade avsändaren och publiceringstiden måste matcha. Detta är ofullständig upptäckt, vilket även UI upplyser om.

public/data/x.json innehåller aktuella originalposter, källstatus och metadata för upptäckt. GitHub Actions cachar urvalet separat; ett källfel tar inte bort senast hämtade aktuella poster. X-delens originalspråk är avsiktligt tydligt märkt och passerar inte den separata grinden för svenska nyhetsartiklar. Reservtext med källans datum visas om X-widgeten blockeras. Sidan kontaktar X för widgets och bilder; inget X-konto eller X-token används av insamlingen.

X kan ändra eller begränsa inbäddningsformatet. Kontrollera data/x.json och Actions-loggen vid bortfall. Försök inte kringgå inloggning, botkontroller eller åtkomstspärrar. Ordinarie RSS, marknadskurser och artikelarkiv fortsätter oberoende.
