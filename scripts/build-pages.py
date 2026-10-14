"""Export real, indexable Pages documents. No server, API key or client router required."""
import datetime as dt,html,json,pathlib,re,shutil,unicodedata
from urllib.parse import urlsplit,parse_qs
from zoneinfo import ZoneInfo
from editorial import readable,enrich,deduplicate
from x_archive import readable_post,archivable_post
ROOT=pathlib.Path(__file__).resolve().parents[1];DIST=ROOT/'dist';DOMAIN='https://kryptopuls.se'
ENTRY_LOADER=(ROOT/'scripts/entry-loader.html').read_text(encoding='utf-8')
CATEGORIES=['Bitcoin','Ethereum','Altcoins','Reglering','Institutionellt','Marknaden']
CATEGORY_LABELS={'Altcoins':'Alternativa kryptovalutor','DeFi':'Decentraliserad finans','On-chain':'Händelser i blockkedjan','Mining':'Utvinning','Stablecoins':'Värdestabila kryptovalutor','Säkerhet / Hacks':'Säkerhet / intrång','Börser':'Kryptobörser','ETF':'Börshandlade fonder (ETF)'}
def category_label(value):return CATEGORY_LABELS.get(value,value)
def esc(value):return html.escape(str(value),quote=True)
def cat_slug(value):return unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower()
def date(value):return dt.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(ZoneInfo('Europe/Stockholm')).strftime('%Y-%m-%d kl. %H:%M')
def link(n):return f'<li><a href="{esc(n["path"])}">{esc(n["title"])}</a><small>{esc(n["author"])} · {date(n["publishedAt"])} · {esc(n.get("contentType","rapportering"))}</small></li>'
CSS='''*{box-sizing:border-box}body{margin:0;background:#101214;color:#edf0ed;font:17px/1.75 system-ui,sans-serif}a{color:#b2e591;text-underline-offset:4px}a:hover{color:white}a:focus-visible,button:focus-visible{outline:3px solid #b2e591;outline-offset:5px}header,main,footer{max-width:820px;margin:auto;padding:24px}header{border-bottom:1px solid #303432}.brand{display:flex;align-items:center;gap:10px;color:#edf0ed;text-decoration:none}.brand-mark{width:38px;height:38px;flex:none}.brand-copy{display:flex;flex-direction:column;gap:3px}.brand-copy strong{font-size:14px;line-height:1.1;letter-spacing:1.8px}.brand-copy small{font-size:9px;font-weight:450;line-height:1.2;color:#aab2ad;letter-spacing:0}nav{display:flex;gap:16px;flex-wrap:wrap;font-size:14px;margin:12px 0}h1{font-size:clamp(28px,5vw,44px);line-height:1.18;letter-spacing:-.03em;margin:24px 0}h2{font-size:24px;line-height:1.3;margin-top:36px}p{margin:20px 0}small,.meta{display:block;font-size:13px;color:#b3b9b3}.kicker{color:#b2e591;font-size:12px;text-transform:uppercase;letter-spacing:.1em}.notice{background:#1b211b;border-left:3px solid #b2e591;padding:16px 20px;margin:24px 0;font-size:15px}.notice p{margin:4px 0}.tags{display:flex;gap:10px;flex-wrap:wrap}.tags a{font-size:13px;padding:3px 12px;background:#242924;border-radius:20px}ul{padding:0;list-style:none}li{padding:18px 0;border-bottom:1px solid #303432}li a{font-weight:650}.video{width:100%;aspect-ratio:16/9;border:0;background:#000}footer{border-top:1px solid #303432;margin-top:40px;font-size:13px;color:#b3b9b3}.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:12px;background:#101214}.share{border:1px solid #535e50;background:#242924;color:#edf0ed;padding:10px 16px;border-radius:6px;cursor:pointer}#share-status{font-size:13px}@media(max-width:480px){header,main,footer{padding:20px}body{font-size:16px}}'''


LIGHT_CSS="""<style>
:root[data-theme=light]{color-scheme:light;--page-bg:#f1f3f1;--page-surface:#fff;--page-text:#202923;--page-muted:#59655d;--page-border:#dfe5e0;--page-accent:#28764f}
:root[data-theme=light] body{background:var(--page-bg);color:var(--page-text)}
:root[data-theme=light] a{color:var(--page-accent)}
:root[data-theme=light] a:hover{color:#174f34}
:root[data-theme=light] header,:root[data-theme=light] footer{border-color:var(--page-border)}
:root[data-theme=light] .brand{color:var(--page-text)}
:root[data-theme=light] .brand-mark rect{fill:#f7f9f7;stroke:#dfe5e0}
:root[data-theme=light] .brand-mark path{stroke:#28764f}
:root[data-theme=light] .brand-copy small,:root[data-theme=light] small,:root[data-theme=light] .meta,:root[data-theme=light] footer{color:var(--page-muted)}
:root[data-theme=light] .kicker{color:#28764f}
:root[data-theme=light] .notice{background:#eaf3ed;border-left-color:#28764f}
:root[data-theme=light] .tags a{background:#edf1ed}
:root[data-theme=light] .share{border-color:#c8d4cb;background:#f7f9f7;color:#202923}
:root[data-theme=light] .skip:focus{background:#fff;color:#202923}
header{display:flex;align-items:center;justify-content:space-between;gap:18px}.static-header-tools{display:flex;align-items:center;gap:16px}
.static-header-tools nav{margin:0}
.theme-toggle{width:34px;height:34px;display:inline-flex;align-items:center;justify-content:center;border:1px solid #39453d;border-radius:7px;background:transparent;color:inherit;cursor:pointer}
.theme-toggle:hover{background:#ffffff12}
.theme-toggle svg{width:19px;height:19px}
.theme-toggle .icon-moon{display:none}
:root[data-theme=light] .theme-toggle{border-color:#dfe5e0;color:#28764f}
:root[data-theme=light] .theme-toggle:hover{background:#edf1ed}
:root[data-theme=light] .theme-toggle .icon-sun{display:none}
:root[data-theme=light] .theme-toggle .icon-moon{display:block}
@media(max-width:600px){header{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px}.static-header-tools{width:100%;justify-content:space-between;gap:10px}.static-header-tools nav{gap:10px;font-size:12px}}
@media(prefers-reduced-motion:reduce){body{transition:none!important}}
</style>"""
def page(title,description,path,body,schema=None):
 data={'@context':'https://schema.org','@type':'WebPage','name':title,'url':DOMAIN+path}
 if schema:data.update(schema)
 structured=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
 return f'''<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Kryptopuls</title><meta name="description" content="{esc(description[:180])}"><link rel="canonical" href="{DOMAIN}{esc(path)}"><meta property="og:locale" content="sv_SE"><meta property="og:site_name" content="Kryptopuls"><meta property="og:type" content="{'article' if schema and schema.get('@type')=='NewsArticle' else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description[:180])}"><meta property="og:url" content="{DOMAIN}{esc(path)}"><meta property="og:image" content="{DOMAIN}/images/kryptopuls-social.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/png"><meta property="og:image:alt" content="Kryptopuls — kryptonyheter på svenska"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description[:180])}"><meta name="twitter:image" content="{DOMAIN}/images/kryptopuls-social.png"><link rel="icon" type="image/svg+xml" href="/favicon.svg"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#101214"><meta name="color-scheme" content="light dark"><meta name="application-name" content="Kryptopuls"><meta name="author" content="Kryptopuls"><style>{CSS}</style>{LIGHT_CSS}<script>(()=>{{let saved=null;try{{saved=localStorage.getItem("kryptopuls-theme")}}catch{{}}const theme=saved==="light"||saved==="dark"?saved:(matchMedia("(prefers-color-scheme: light)").matches?"light":"dark");document.documentElement.dataset.theme=theme;document.documentElement.style.colorScheme=theme;document.querySelector("meta[name=theme-color]").content=theme==="light"?"#f1f3f1":"#101214";const sync=()=>document.querySelectorAll("[data-theme-toggle]").forEach(b=>{{b.setAttribute("aria-label",theme==="dark"?"Byt till ljust läge":"Byt till mörkt läge");b.title=b.getAttribute("aria-label")}});document.addEventListener("DOMContentLoaded",sync,{{once:true}});document.addEventListener("click",e=>{{const b=e.target.closest("[data-theme-toggle]");if(!b)return;const next=document.documentElement.dataset.theme==="dark"?"light":"dark";document.documentElement.dataset.theme=next;document.documentElement.style.colorScheme=next;try{{localStorage.setItem("kryptopuls-theme",next)}}catch{{}}document.querySelector("meta[name=theme-color]").content=next==="light"?"#f1f3f1":"#101214";b.setAttribute("aria-label",next==="dark"?"Byt till ljust läge":"Byt till mörkt läge");b.title=b.getAttribute("aria-label")}})}})();</script><script type="application/ld+json">{structured}</script></head><body>{ENTRY_LOADER}<a class="skip" href="#content">Till innehållet</a><header><a class="brand" href="/" aria-label="Kryptopuls startsida"><svg class="brand-mark" viewBox="0 0 40 40" aria-hidden="true"><rect x="1" y="1" width="38" height="38" rx="11" fill="#171a1c" stroke="#39453d"/><path d="M6 21h7l4-9 6 17 4-9h7" fill="none" stroke="#9bd8b0" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg><span class="brand-copy"><strong>KRYPTOPULS</strong><small>Kryptomarknaden. På svenska. I realtid.</small></span></a><div class="static-header-tools"><nav aria-label="Huvudnavigation"><a href="/">Senaste</a><a href="/kategori/bitcoin/">Bitcoin</a><a href="/kategori/ethereum/">Ethereum</a><a href="/kategori/altcoins/">Alternativa kryptovalutor</a><a href="/?category=YouTube">YouTube</a></nav><button class="theme-toggle" type="button" data-theme-toggle aria-label="Byt till ljust läge" title="Byt till ljust läge"><svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></svg><svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.8 13.3A8.5 8.5 0 0 1 10.7 3.2 8.5 8.5 0 1 0 20.8 13.3z"/></svg></button></div></header><main id="content">{body}</main><footer>Kryptopuls · Självständiga svenska sammanfattningar med tydliga källor. Uppgifter från en källa är inte automatiskt oberoende bekräftade. Inget här är personlig investeringsrådgivning.<br><a href="/">Till nyhetsflödet</a></footer></body></html>'''

def embed(n):
 if n['sourceId'] not in {'moon-video','rover-video','altcoin-daily-video','felix-video','mmcrypto-video','diary-video','pbd-video','cryptokid-video','cryptocurrently-video'}:return ''
 u=urlsplit(n['originalUrl']);video=None
 if u.scheme!='https' or u.username or u.password or u.port:return ''
 if u.hostname=='youtu.be':video=u.path[1:]
 elif u.hostname in {'www.youtube.com','youtube.com','m.youtube.com'}:
  video=parse_qs(u.query).get('v',[None])[0] if u.path=='/watch' else u.path.rstrip('/').split('/')[-1] if re.match(r'^/(shorts|live|embed)/',u.path) else None
 if not video or not re.fullmatch(r'[A-Za-z0-9_-]{11}',video):return ''
 return f'<h2>Se videon</h2><p class="meta">Sammanfattningen bygger på kanalens beskrivning. Videon visas på originalspråket. Svenska undertexter kan väljas i spelaren om de finns tillgängliga.</p><iframe class="video" title="{esc(n["title"])}" loading="lazy" src="https://www.youtube-nocookie.com/embed/{video}?hl=sv&cc_lang_pref=sv&cc_load_policy=1" allow="encrypted-media; picture-in-picture; fullscreen" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'

def linked_x_text(text):
 parts=re.split(r'(https?://[^\s<>]+)',text);output=[]
 for part in parts:
  try:
   u=urlsplit(part)
   allowed=u.scheme=='https' and u.hostname in {'x.com','twitter.com','t.co'} and not u.username and not u.password and not u.port
  except ValueError:allowed=False
  output.append(f'<a href="{esc(part)}" target="_blank" rel="noopener noreferrer">{esc(part)}</a>' if allowed else esc(part))
 return ''.join(output)

def x_page(post):
 title='X · '+post['author'];path='/x/'+post['id']+'/'
 original=post['originalLanguage']=='sv';pending=not readable_post(post)
 text=post['text'] if original else post['swedish']['text'] if not pending else 'Svensk översättning saknas för det här inlägget.'
 label='Svensk översättning saknas' if pending else 'Svenskt original' if original else 'Sammanfattat på svenska' if post['swedish']['method']=='summary' else 'Maskinöversatt till svenska' if post['swedish'].get('engine','').startswith(('nllb-','mymemory-')) else 'Översatt till svenska'
 art='bitcoin' if 'BTC' in post['coins'] else 'ethereum' if 'ETH' in post['coins'] else 'network'
 fallback_art='bitcoin-news' if art=='bitcoin' else art
 media=''
 for image in post.get('media',[])[:4]:
  try:
   u=urlsplit(image.get('url',''))
   if u.scheme!='https' or u.hostname!='pbs.twimg.com' or u.username or u.password or u.port:continue
  except (ValueError,AttributeError):continue
  media+=f'<img src="{esc(image["url"])}" alt="{esc(image.get("alt") or "Bild från originalinlägget på X")}" loading="lazy" onerror="this.onerror=null;this.src=\'/images/{fallback_art}-640.webp\';this.alt=\'Illustrationsbild\'" style="display:block;max-width:100%;height:auto;margin:20px 0;border-radius:8px">'
 language=''
 original_html='' if original else '<p class="meta">Originaltexten visas på avsändarens X-sida och återges inte här.</p>'
 body=f'''<article><span class="kicker">X · @{esc(post['handle'])}</span><h1>{esc(title)}</h1><p class="meta"><time datetime="{esc(post['publishedAt'])}">{date(post['publishedAt'])}</time>, svensk tid</p><p class="meta">{esc(label)}</p><section aria-label="X-inlägget" style="white-space:pre-wrap;overflow-wrap:anywhere"><p>{linked_x_text(text) if original else esc(text)}</p></section>{media}{original_html}<p class="notice">Kontots uppgifter är inte oberoende bekräftade. Detta är Kryptopulss sparade återgivning av inlägget. Originalet på X kan senare ändras eller tas bort.</p><p><a href="{esc(post['url'])}" target="_blank" rel="noopener noreferrer">Visa originalposten på X →</a></p><button class="share" id="share">Kopiera länk</button><p id="share-status" role="status"></p><script>document.getElementById('share').onclick=async()=>{{const s=document.getElementById('share-status');const url=document.querySelector('link[rel=canonical]').href;try{{await navigator.clipboard.writeText(url);s.textContent='Länken är kopierad.'}}catch{{s.textContent=url}}}};</script></article>'''
 return path,page(title,text,path,body,{'@type':'SocialMediaPosting','headline':title,'datePublished':post['publishedAt'],'inLanguage':'sv-SE','citation':post['url'],'author':{'@type':'Person','name':post['author']}})

def main():
 # Remove pages generated by older versions after the daily overview feature is retired.
 shutil.rmtree(DIST/'idag',ignore_errors=True)
 (DIST/'data/daily.json').unlink(missing_ok=True)
 feed=json.loads((ROOT/'public/data/news.json').read_text());archive=ROOT/'public/data/archive.json'
 rows=json.loads(archive.read_text())['items'] if archive.exists() else feed['items']
 items=[enrich(n) for n in deduplicate(rows) if readable(n)]
 if not items:raise ValueError('No readable articles: refusing to export empty site')
 category_root=DIST/'kategori';active_categories={cat_slug(c) for c in CATEGORIES}
 if category_root.exists():
  for old_page in category_root.iterdir():
   if old_page.is_dir() and old_page.name not in active_categories:shutil.rmtree(old_page)
 urls=['/'];paths=set()
 def write(path,content):
  if not re.fullmatch(r'/[a-z0-9/-]+/',path):raise ValueError('Unsafe permanent URL')
  if path in paths:raise ValueError('Duplicate permanent URL')
  paths.add(path);target=DIST/path.strip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content);urls.append(path)
 for n in items:
  paragraphs=''.join('<p>'+esc(p)+'</p>' for p in n['readerText'].split('\n\n') if p.strip() and p!=n.get('why'))
  tags=''.join(f'<a href="/kategori/{cat_slug(c)}/">{esc(category_label(c))}</a>' for c in n['categories'])
  verification=n.get('verificationNote') or 'Källans uppgifter har inte bekräftats oberoende. Sammanfattningen ska läsas som en återgivning av vad källan rapporterar.'
  why=f'<section class="notice"><h2>Varför är detta viktigt?</h2><p>{esc(n["why"])}</p></section>' if n.get('why') else ''
  body=f'''<article><span class="kicker">{esc(n['contentType'])} · {esc(n['author'])}</span><h1>{esc(n['title'])}</h1><p class="meta">Källan publicerade <time datetime="{esc(n['publishedAt'])}">{date(n['publishedAt'])}</time>, svensk tid</p><div class="tags">{tags}</div><p class="notice">{esc(verification)}</p><section aria-label="Nyhetstext">{paragraphs}</section>{why}{embed(n)}<p class="meta">{esc(n.get('editorialDisclosure','Självständigt skriven svensk sammanfattning. Originalartikeln återpubliceras inte.'))}</p><h2>Källa och underlag</h2><p><a href="{esc(n['originalUrl'])}" rel="noopener noreferrer">{esc(n['author'])} – originalpubliceringen ↗</a></p><button class="share" id="share">Kopiera artikellänk</button><p id="share-status" role="status"></p><script>document.getElementById('share').onclick=async()=>{{const s=document.getElementById('share-status');try{{await navigator.clipboard.writeText(document.querySelector('link[rel=canonical]').href);s.textContent='Länken är kopierad.'}}catch{{s.textContent=document.querySelector('link[rel=canonical]').href}}}};</script></article>'''
  schema={'@type':'NewsArticle','headline':n['title'],'datePublished':n['publishedAt'],'dateModified':n.get('editedAt',n['importedAt']),'author':{'@type':'Organization','name':'Kryptopuls','url':DOMAIN},'publisher':{'@type':'Organization','name':'Kryptopuls','url':DOMAIN,'logo':{'@type':'ImageObject','url':DOMAIN+'/icon-512.png'}},'mainEntityOfPage':DOMAIN+n['path'],'inLanguage':'sv-SE','citation':n['originalUrl'],'articleSection':[category_label(c) for c in n['categories']],'description':n['summary']}
  write(n['path'],page(n['title'],n['summary'],n['path'],body,schema))
 x_archive=ROOT/'public/data/x-archive.json'
 x_posts=json.loads(x_archive.read_text()).get('posts',[]) if x_archive.exists() else []
 for post in x_posts:
  if archivable_post(post):
   path,content=x_page(post);write(path,content)
 for c in CATEGORIES:
  matching=[n for n in items if c in n['categories']];path='/kategori/'+cat_slug(c)+'/'
  body=f'<span class="kicker">Nyhetsarkiv</span><h1>{esc(category_label(c))}</h1><p>Svenska sammanfattningar med källor och sammanhang. En nyhet kan tillhöra flera kategorier.</p><ul>'+''.join(map(link,matching))+'</ul>'
  if not matching:body+='<p>Inga publicerade nyheter i kategorin ännu.</p>'
  write(path,page(category_label(c)+' – nyheter',f'Nyheter om {category_label(c).lower()} på svenska med tydliga originalkällor.',path,body))
 sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+DOMAIN+esc(u)+'</loc></url>' for u in urls)+'</urlset>'
 (DIST/'sitemap.xml').write_text(sitemap);(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+DOMAIN+'/sitemap.xml\n')
 home=DIST/'index.html';text=home.read_text();text=text.replace('<noscript>Aktivera JavaScript för att använda Kryptopuls.</noscript>','<noscript><h1>Kryptopuls – kryptonyheter på svenska</h1><ul>'+''.join(map(link,items[:30]))+'</ul></noscript>');home.write_text(text)
 print(f'Exported {len(items)} articles, {len(x_posts)} permanent X pages and {len(CATEGORIES)} categories')
if __name__=='__main__':main()
