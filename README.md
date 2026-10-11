# Kryptoflödet

Svensk kryptonyhetstjänst med mörk responsiv design, bilder, sökning, kategorier, coin-filter, källgranskning, lokala bokmärken och en sömlöst rullande marknadsticker.

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
