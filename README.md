# Kryptokollen

Svenska kryptonyheter och marknadsdata på https://kryptoflodet.github.io/.

## Nyhetsflöde

Hämtar och publicerar nyheter vid push, manuell körning och enligt femminutersschema. 
GitHub kan fördröja körningar och inaktivera scheman efter lång inaktivitet i publika repositoryn.

`scripts/sources.json` innehåller källorna. `scripts/crypto_scope.py` släpper bara
igenom rubriker med ett direkt kryptoämne. Bred ekonomi, energi och indirekt
makropåverkan räcker inte. DI, Avanza, Realtid, Dagens PS, SVT Ekonomi, WSJ, Fed och
Riksbanken är borttagna. Samma filter tillämpas på återhämtade äldre poster.
Filtret är konservativt och kan utelämna relevanta men otydliga rubriker.

CoinMarketCap Community läses som offentlig, indexerad nyhetsbevakning via Google
Nyheter; bidragen är inte automatiskt verifierade av CoinMarketCap. CoinGlass
finns i registret men är inte anslutet: deras direkta nyhets-API kräver separat
API-åtkomst. Datadiagram och likvidationssidor publiceras inte som nyheter.
X-profiler följs med begränsad mediebevakning; CryptoRover och The Moon Show även
via deras egna YouTube-flöden. Det är inte en fullständig import av X-inlägg.

Utländska rubriker översätts lokalt med Argos, CTranslate2 och SentencePiece.
Lingua granskar språket. Rubriker som inte klarar språk- eller sifferkontroll
publiceras inte. Maskinöversättning kan innehålla fel. Modell och översättningar
cachas. Ingen betald AI-tjänst eller API-nyckel används för översättningen.

`scripts/reviewed.json` innehåller avgränsade, granskade originalbesked med svensk
sammanfattning. Bara dessa kan få status `confirmed`; källtyp i sig räcker inte.
Bekräftelsen gäller det angivna beskedet, inte alla projektets prestationspåståenden
eller påverkan på tokenpriset. Granskningsanteckningen visas i artikeln.

## Marknad och diagram

Alla 15 kurser kontrolleras var 30:e sekund hos CoinGecko. En separat, tidsstämplad
reserv hämtas av GitHub med `scripts/fetch-market.py`. Gamla/saknade kurser visas
som fördröjda; tidsstämplarna kommer från kurskällan, inte från publiceringstid.

Klick på tickern eller marknadsöversikten öppnar ett tillgängligt dialogfönster.
Perioder: 24 timmar, i dag (Stockholm), vecka, månad, kvartal, i år, ett år, tre år,
fem år och all tillgänglig historik. Kort historik kommer från CoinGecko i USD/SEK.
Lång historik och reservhämtning kommer från Binance i **USDT**, tydligt märkt.
USD, USDT och SEK blandas inte i samma serie. Historik från Binance börjar vid
notering av handelsparet, inte kryptovalutans skapande. Ingen historik fabriceras.

## Lokal utveckling och verifiering

```sh
npm ci
pip install -r scripts/translation-requirements.txt
python scripts/fetch-news.py
python scripts/fetch-market.py
npm run build
npm test
python -m unittest discover -s tests -p '*_test.py'
npm run dev
```

`backend/` bevarar tidigare serverkod men körs inte på GitHub Pages.
