# Kryptokollen – utvecklingslogg

## Uppdrag 12 oktober 2026
Befintligt repo kryptoflodet/kryptoflodet.github.io. Inga extra API-kostnader. GitHub Pages och kryptokollen.online behålls.

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
- Befintliga 15 marknadskurser, blogg, lokala bokmärken och grafer behålls.

## Avsiktliga begränsningar
Direkt X-import är inte ansluten. Publik RSSHub gav 404 och Nitter 410; valfri egen RSSHub-adapter finns för fyra konton. Den kräver ingen betald X API, men en fungerande server och RSSHub-autentisering saknas. Resten fungerar utan den.

Tre fria lokala Qwen-modeller utvärderades: 1.7B, 4B Instruct och 8B. Alla gav språkproblem eller osäkra fakta i prov. 8B hittade dessutom på en inflationsuppgift i ett test om ett försäkringsbolag; källstödsgrinden avvisade den. En 4B-text passerade modellens egen kontroll trots tydliga språkfel och togs bort före publicering. Därför är produktionsläget reviewed-only. Experimentmodulen är till för lokala utkast. GitHub Models har avvecklats och används inte. Betalda tjänster har inte aktiverats.

Automatisk naturlig svensk nyhetsskrivning och oberoende flerkällskontroll är således inte lösta. Dagsöversikten är ett försiktigt sammanställt urval, inte en komplett generativ dagsanalys. Aktuella YouTube-flöden svarade HTTP-fel vid test; fungerande flöden påverkas inte, och videor utan tillräckligt textunderlag publiceras inte.

## Aktiv kontrollpunkt
Publicerat: commit a7cea3d5f5387f73266f4567c3002034e67c61a3. GitHub Actions-körning 38231790878 slutfördes med success, inklusive insamling, marknadsdata, bygge, alla frontendtester, 19 Python-tester och Pages-deployment.

Livekontroll 12 oktober 2026: kryptokollen.online svarar HTTP 200. kryptoflodet.github.io omdirigeras till den egna domänen och svarar 200. Nyhets-JSON visar schemaVersion 2, tre granskade artiklar och reviewed-only. Senaste kontrollerade hämtning 10:29 UTC nådde 22 av 24 aktiva källor; 219 kandidater hålls tillbaka. Sui-artikeln, /kategori/sui/, /idag/ och /sitemap.xml svarar 200. Alla interna länkar i 16 genererade HTML-sidor validerades före publicering.

Visuell desktop-/mobilkontroll är INTE slutförd: molnwebbläsaren fastnade med timeout och lokala browserbinärer kunde inte installeras. Inga påståenden om visuellt godkänd mobilvy görs. Nästa konkreta steg är visuell kontroll vid 390 och 1440 px och därefter fortsatt utvärdering av gratis språkhantering. Drift och beständiga artikelsidor är publicerade; full automatisk redaktion är inte färdig.

## Återuppta
Arbetsgren kryptokollen-release (tidigare kryptokollen-news-service). Kontrollera git status, senaste remote main och denna logg. Förbättra språkautomationen endast med en gratis metod som klarar en separat svensk kvalitetsutvärdering. Slå inte på automatisk publicering av nuvarande modellförslag. Läs docs/OPERATIONS.md för begränsningar och drift. Automatisk återstart av ChatGPT efter användningsgräns kan inte garanteras; inga försök att kringgå gränser ska göras.
