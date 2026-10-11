# Kryptoflödet Blog

Blog lives at `/?category=Blog`, beside Reglering. Posts are rendered directly on the site and archived in `public/data/blog.json`. Deep link: `/?category=Blog&post=YYYY-MM-DD`.

An authorized ChatGPT automation starts Wednesday and Sunday at 20:00 Europe/Stockholm (DST-aware). The automation researches, writes, commits, and verifies publication. Writing and GitHub Pages deployment add latency; this is not a guaranteed exact-time delivery. Automation does not require a paid model API in this repository. Do not replace it with a template that merely repeats feed headlines.

Wednesday covers Monday through Wednesday publication (Mittveckan); Sunday covers Monday through Sunday publication (Veckan). Verify publication and event dates; prefer primary sources. Explain jargon and distinguish reported facts, interpretation, and uncertainty. Only directly crypto-related events. Write original, polished Swedish prose, normally 600–1000 words with 4–6 key events, but prioritize evidence over length. Avoid long quotations, copied articles, invented facts, hype and personal investment advice.

## Data format

JSON object with `posts` array. Preserve existing entries. One entry per scheduled date; `id` is that date, preventing duplicate runs. Publish timestamps are actual ISO timestamps with a timezone. Future-dated posts are hidden until their publication time. All visible text is Swedish. Text is rendered as plain text; do not insert HTML or Markdown.

Evergreen educational guides use `kind: "guide"` and a descriptive slug such as `krypto-for-nyborjare`. Preserve these alongside dated recaps; a guide is not the scheduled recap for that date.

Each post:
- `id`: YYYY-MM-DD
- `title`: clear editorial headline
- `dek`: informative two-sentence introduction
- `publishedAt`: actual ISO timestamp, including offset
- `period`: e.g. `5–11 oktober 2026` or `12–14 oktober 2026 · Mittveckan`
- `readingMinutes`: positive integer based on approximately 200 words/minute
- `takeaways`: array of 3 concise Swedish key points
- `sections`: array of `{ "heading": "...", "paragraphs": ["..."], "sourceIds": ["s1"] }`
- `sources`: array of `{ "id": "s1", "name": "Utgivarens namn", "url": "https://..." }`

Every factual news section must reference its supporting original source URL. Final contextual section may refer to preceding sources. Never claim whole-market completeness based only on feeds.

## Publishing

Read current main and current blog.json. Add the post, validate schema and unique IDs, build and run existing tests. Use GitHub create_tree with current base tree, create_commit with current parent, then update_ref with expected_sha. If main changed, re-read and merge changes; no forced overwrite. Existing news-pages workflow deploys automatically. Blog data is not part of the news cache; never overwrite it while fetching RSS. Verify Actions success and the public JSON/post link. Report failure honestly if any step fails.

Sections may include optional `table: {headers: string[], rows: string[][]}` for factual comparisons. Every row must match the header length; source links belong in sourceIds.
