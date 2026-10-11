# Kryptoflödet

Svensk nyhetstjänst med dom senaste kryptonyheterna. Allt på svenska. Inget krångel. Bara krypto

https://kryptoflodet.github.io

## Starta lokalt

Node.js 24 rekommenderas, samma version som publiceringsflödet använder.

```sh
npm ci
npm run dev
```

Öppna adressen som Vite visar, med sökvägen `/kryptoflodet/`.

```sh
npm run build
npm test
npm run preview
```

## GitHub Pages

Projektfilerna ligger direkt i repositoryts rot. `vite.config.ts` använder `base: '/kryptoflodet/'`. Bygget hamnar i `dist/`; inga serverfunktioner krävs för den publicerade sidan. Bilder, ikoner, skript, sökning och startsidelänkar använder samma base path.

Befintliga `.github/workflows/deploy.yml` är bevarad oförändrad. Den kör `npm ci`, `npm run build` och publicerar `dist` vid push till `main`. Repositoryts Settings → Pages → Source behöver vara GitHub Actions.

Förväntad adress: https://kryptoflodet.github.io/kryptoflodet/

## Data och begränsningar

- Nyhetsflödet innehåller tydligt märkta **demonyheter**. Originalkällornas startsidor är inte belägg för demohändelserna.
- Kurser för BTC, ETH, SOL, SUI, HBAR, ONDO, XRP, ADA, DOGE, XLM, AVAX, LINK, BNB, HYPE och LTC hämtas direkt i webbläsaren från CoinGeckos publika API, i både USD och SEK.
- Ett nytt kursanrop görs varje minut när sidan är synlig. CoinGeckos tillgänglighet, CORS och anropsgränser kan påverka uppdateringarna. Ingen API-nyckel inkluderas i klienten.
- Senast lyckade hämtning sparas lokalt. Vid avbrott visas den som **fördröjd**. En verklig, daterad prisögonblicksbild följer med som sista reserv. Den presenteras aldrig som live innan ett nytt anrop lyckas.
- Bilderna är AI-genererade redaktionella illustrationer, inte fotografier av nyhetshändelser.
- Bokmärken sparas i den aktuella webbläsaren.

## Struktur

- `src/App.tsx`: gränssnitt, filter, ticker och dialoger.
- `src/styles.css`: responsiv design och kortlayout.
- `src/lib/`: datamodeller, demo, källbedömning och marknadsadapter.
- `public/`: favicon och optimerade bilder.
- `tests/`: kontroll av filter, marknadsdata och Pages-sökvägar.
- `backend/`: bevarad serverkod, importgränssnitt och databasmigreringar från Sites-versionen. Den körs inte och ingår inte i Pages-bygget. Se `backend/README.md`.

## Aktuell GitHub Pages-publicering

Repositoryt heter `kryptoflodet.github.io` och Vites base är `/`.
`.github/workflows/news-pages.yml` bygger och publicerar vid push till main,
manuell körning och enligt ett femminutersschema. GitHub kan fördröja
schemakörningar och inaktiverar scheman i inaktiva publika repositoryn.
GitHub Pages måste använda **GitHub Actions** som publiceringskälla.

`python scripts/fetch-news.py` hämtar RSS/Atom och sparar metadata i
`public/data/news.json`. Källfel behåller senaste lyckade poster via Actions cache;
om allt misslyckas utan tidigare data stoppas publicering. Inga API-nycklar krävs
för de öppna RSS-källorna. Källornas status visas i appen. X, Instagram, Strategy
och BlackRock är inte anslutna utan separat godkänd dataåtkomst. Ondo och Chainlink
visas som hämtningsfel om deras provade feed inte svarar med giltig RSS.

Utländska rubriker översätts lokalt med Argos en–sv, CTranslate2 och SentencePiece. Lingua granskar målspråket. Rubriker som inte klarar språk- eller sifferkontroll publiceras inte; ingen engelsk reservtext visas. Maskinöversättning kan fortfarande innehålla fel.
RSS-publicering räknas inte som oberoende bekräftelse, och automatiska poster har
varken sentimentanalys eller påhittad konfidens. Bilderna är AI-illustrationer.
Öppna webbläsare hämtar ny publicerad JSON varje minut utan att tappa filter.

Kontroll: `npm ci`, `npm run build`, `npm test`,
`python -m unittest discover -s tests -p '*_test.py'`.


## Svenskt flöde och utökade källor

Källor konfigureras i `scripts/sources.json`. Tillagda källor inkluderar
Cryptonews, Dagens industri, Avanzabloggen, Realtid, Dagens PS, SVT Ekonomi,
Riksbanken, WSJ, The Block och CryptoSlate. Svenska breda ekonomiflöden samlas under kategorin Ekonomi. Detta är inte fullständiga
artikelarkiv och kringgår inte betalväggar.

CryptoRover och The Moon Show följs även via deras verifierade YouTube-kanalers
Atom-flöden. Google Nyheter ger separat mediebevakning av Michael Saylor,
CryptoRover, The Moon Show, Watcher.Guru och länkar till @bitcoin. Det är artiklar
OM dessa profiler, inte ett komplett flöde av deras X-inlägg. Nitter svarade 410
eller 502 vid test; RSSHub gav timeout. Ingen X API-nyckel används. Direktflöden
från X är fortfarande inte anslutna.

Installera översättningsberoenden med
`pip install -r scripts/translation-requirements.txt` före nyhetsinhämtning.
Språkmodellen hämtas från Argos officiella modellserver. Modell och översättningar
cachas i GitHub Actions; ingen betald AI-tjänst används. Vid modellfel stoppas
publiceringen och den senaste webbversionen ligger kvar. Femminutersschemat är
oförändrat. Illustrationernas överlagrade etikett har tagits bort; metodsidan
beskriver fortfarande hur bilderna har skapats.
