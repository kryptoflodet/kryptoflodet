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
19 Python-tester samt befintliga frontendtester körs inför publicering. Nästa steg: publicera den testade ändringen, kontrollera Actions, egen domän, egna artikel-URL:er och layout. Uppdatera denna punkt med faktisk deploymentstatus.

## Återuppta
Arbetsgren kryptokollen-news-service. Kontrollera git status, senaste remote main och denna logg. Förbättra språkautomationen endast med en gratis metod som klarar en separat svensk kvalitetsutvärdering. Slå inte på automatisk publicering av nuvarande modellförslag. Läs docs/OPERATIONS.md för begränsningar och drift. Automatisk återstart av ChatGPT efter användningsgräns kan inte garanteras; inga försök att kringgå gränser ska göras.
