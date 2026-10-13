"""Export real, indexable Pages documents. No server, API key or client router required."""
import datetime as dt,html,json,pathlib,re,shutil,unicodedata
from urllib.parse import urlsplit,parse_qs
from zoneinfo import ZoneInfo
from editorial import readable,enrich,deduplicate
from x_archive import readable_post
ROOT=pathlib.Path(__file__).resolve().parents[1];DIST=ROOT/'dist';DOMAIN='https://kryptokollen.online'
CATEGORIES=['Bitcoin','Ethereum','Altcoins','Reglering','Institutionellt','Marknaden']
def esc(value):return html.escape(str(value),quote=True)
def cat_slug(value):return unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower()
def date(value):return dt.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(ZoneInfo('Europe/Stockholm')).strftime('%Y-%m-%d kl. %H:%M')
def link(n):return f'<li><a href="{esc(n["path"])}">{esc(n["title"])}</a><small>{esc(n["author"])} · {date(n["publishedAt"])} · {esc(n.get("contentType","rapportering"))}</small></li>'
CSS='''*{box-sizing:border-box}body{margin:0;background:#101214;color:#edf0ed;font:17px/1.75 system-ui,sans-serif}a{color:#b2e591;text-underline-offset:4px}a:hover{color:white}a:focus-visible,button:focus-visible{outline:3px solid #b2e591;outline-offset:5px}header,main,footer{max-width:820px;margin:auto;padding:24px}header{border-bottom:1px solid #303432}.brand{font-size:24px;font-weight:800;color:#edf0ed;text-decoration:none}nav{display:flex;gap:16px;flex-wrap:wrap;font-size:14px;margin:12px 0}h1{font-size:clamp(28px,5vw,44px);line-height:1.18;letter-spacing:-.03em;margin:24px 0}h2{font-size:24px;line-height:1.3;margin-top:36px}p{margin:20px 0}small,.meta{display:block;font-size:13px;color:#b3b9b3}.kicker{color:#b2e591;font-size:12px;text-transform:uppercase;letter-spacing:.1em}.notice{background:#1b211b;border-left:3px solid #b2e591;padding:16px 20px;margin:24px 0;font-size:15px}.notice p{margin:4px 0}.tags{display:flex;gap:10px;flex-wrap:wrap}.tags a{font-size:13px;padding:3px 12px;background:#242924;border-radius:20px}ul{padding:0;list-style:none}li{padding:18px 0;border-bottom:1px solid #303432}li a{font-weight:650}.video{width:100%;aspect-ratio:16/9;border:0;background:#000}footer{border-top:1px solid #303432;margin-top:40px;font-size:13px;color:#b3b9b3}.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:12px;background:#101214}.share{border:1px solid #535e50;background:#242924;color:#edf0ed;padding:10px 16px;border-radius:6px;cursor:pointer}#share-status{font-size:13px}@media(max-width:480px){header,main,footer{padding:20px}body{font-size:16px}}'''

def page(title,description,path,body,schema=None):
 data={'@context':'https://schema.org','@type':'WebPage','name':title,'url':DOMAIN+path}
 if schema:data.update(schema)
 structured=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
 return f'''<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Kryptokollen</title><meta name="description" content="{esc(description[:180])}"><link rel="canonical" href="{DOMAIN}{esc(path)}"><meta property="og:locale" content="sv_SE"><meta property="og:site_name" content="Kryptokollen"><meta property="og:type" content="{'article' if schema and schema.get('@type')=='NewsArticle' else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description[:180])}"><meta property="og:url" content="{DOMAIN}{esc(path)}"><meta property="og:image" content="{DOMAIN}/images/kryptokollen-social.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/png"><meta property="og:image:alt" content="Kryptokollen — kryptonyheter på svenska"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description[:180])}"><meta name="twitter:image" content="{DOMAIN}/images/kryptokollen-social.png"><link rel="icon" href="/favicon.svg"><meta name="theme-color" content="#101214"><style>{CSS}</style><script type="application/ld+json">{structured}</script></head><body><a class="skip" href="#content">Till innehållet</a><header><a class="brand" href="/">Kryptokollen<span style="color:#b2e591">.</span></a><nav aria-label="Huvudnavigation"><a href="/">Senaste</a><a href="/kategori/bitcoin/">Bitcoin</a><a href="/kategori/ethereum/">Ethereum</a><a href="/kategori/altcoins/">Altcoins</a></nav></header><main id="content">{body}</main><footer>Kryptokollen · Självständiga svenska sammanfattningar med tydliga källor. Uppgifter från en källa är inte automatiskt oberoende bekräftade. Inget här är personlig investeringsrådgivning.<br><a href="/">Till nyhetsflödet</a></footer></body></html>'''

def embed(n):
 if n['sourceId'] not in {'moon-video','rover-video','altcoin-daily-video','felix-video','mmcrypto-video'}:return ''
 u=urlsplit(n['originalUrl']);video=None
 if u.scheme!='https' or u.username or u.password or u.port:return ''
 if u.hostname=='youtu.be':video=u.path[1:]
 elif u.hostname in {'www.youtube.com','youtube.com','m.youtube.com'}:
  video=parse_qs(u.query).get('v',[None])[0] if u.path=='/watch' else u.path.rstrip('/').split('/')[-1] if re.match(r'^/(shorts|live|embed)/',u.path) else None
 if not video or not re.fullmatch(r'[A-Za-z0-9_-]{11}',video):return ''
 return f'<h2>Se videon</h2><p class="meta">Sammanfattningen bygger på kanalens beskrivning. Videon spelas från YouTube på originalspråket.</p><iframe class="video" title="{esc(n["title"])}" loading="lazy" src="https://www.youtube-nocookie.com/embed/{video}" allow="encrypted-media; picture-in-picture; fullscreen" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'

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
 original=post['originalLanguage']=='sv';text=post['text'] if original else post['swedish']['text']
 label='Svenskt original' if original else 'Sammanfattat på svenska' if post['swedish']['method']=='summary' else 'Översatt till svenska'
 art='bitcoin' if 'BTC' in post['coins'] else 'ethereum' if 'ETH' in post['coins'] else 'network'
 media=''
 for image in post.get('media',[])[:4]:
  try:
   u=urlsplit(image.get('url',''))
   if u.scheme!='https' or u.hostname!='pbs.twimg.com' or u.username or u.password or u.port:continue
  except (ValueError,AttributeError):continue
  media+=f'<img src="{esc(image["url"])}" alt="{esc(image.get("alt") or "Bild från originalinlägget på X")}" loading="lazy" onerror="this.onerror=null;this.src=\'/images/{art}-640.webp\';this.alt=\'Illustrationsbild\'" style="display:block;max-width:100%;height:auto;margin:20px 0;border-radius:8px">'
 original_html='' if original else f'<details><summary>Visa original</summary><blockquote lang="en" style="white-space:pre-wrap;overflow-wrap:anywhere">{linked_x_text(post["text"])}</blockquote></details>'
 body=f'''<article><span class="kicker">X · @{esc(post['handle'])}</span><h1>{esc(title)}</h1><p class="meta"><time datetime="{esc(post['publishedAt'])}">{date(post['publishedAt'])}</time>, svensk tid</p><p class="meta">{esc(label)}</p><section aria-label="X-inlägget" style="white-space:pre-wrap;overflow-wrap:anywhere"><p>{linked_x_text(text) if original else esc(text)}</p></section>{media}{original_html}<p class="notice">Kontots uppgifter är inte oberoende bekräftade. Detta är Kryptokollens sparade återgivning av inlägget. Originalet på X kan senare ändras eller tas bort.</p><p><a href="{esc(post['url'])}" target="_blank" rel="noopener noreferrer">Visa originalposten på X →</a></p><button class="share" id="share">Kopiera länk</button><p id="share-status" role="status"></p><script>document.getElementById('share').onclick=async()=>{{const s=document.getElementById('share-status');const url=document.querySelector('link[rel=canonical]').href;try{{await navigator.clipboard.writeText(url);s.textContent='Länken är kopierad.'}}catch{{s.textContent=url}}}};</script></article>'''
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
  tags=''.join(f'<a href="/kategori/{cat_slug(c)}/">{esc(c)}</a>' for c in n['categories'])
  verification=n.get('verificationNote') or 'Källans uppgifter har inte bekräftats oberoende. Sammanfattningen ska läsas som en återgivning av vad källan rapporterar.'
  why=f'<section class="notice"><h2>Varför är detta viktigt?</h2><p>{esc(n["why"])}</p></section>' if n.get('why') else ''
  body=f'''<article><span class="kicker">{esc(n['contentType'])} · {esc(n['author'])}</span><h1>{esc(n['title'])}</h1><p class="meta">Källan publicerade <time datetime="{esc(n['publishedAt'])}">{date(n['publishedAt'])}</time>, svensk tid</p><div class="tags">{tags}</div><p class="notice">{esc(verification)}</p><section aria-label="Nyhetstext">{paragraphs}</section>{why}{embed(n)}<p class="meta">{esc(n.get('editorialDisclosure','Självständigt skriven svensk sammanfattning. Originalartikeln återpubliceras inte.'))}</p><h2>Källa och underlag</h2><p><a href="{esc(n['originalUrl'])}" rel="noopener noreferrer">{esc(n['author'])} – originalpubliceringen ↗</a></p><p class="meta">Rubriken i original: {esc(n['originalTitle'])}</p><button class="share" id="share">Kopiera artikellänk</button><p id="share-status" role="status"></p><script>document.getElementById('share').onclick=async()=>{{const s=document.getElementById('share-status');try{{await navigator.clipboard.writeText(document.querySelector('link[rel=canonical]').href);s.textContent='Länken är kopierad.'}}catch{{s.textContent=document.querySelector('link[rel=canonical]').href}}}};</script></article>'''
  schema={'@type':'NewsArticle','headline':n['title'],'datePublished':n['publishedAt'],'dateModified':n.get('editedAt',n['importedAt']),'author':{'@type':'Organization','name':'Kryptokollen','url':DOMAIN},'publisher':{'@type':'Organization','name':'Kryptokollen','url':DOMAIN},'mainEntityOfPage':DOMAIN+n['path'],'inLanguage':'sv-SE','citation':n['originalUrl'],'articleSection':n['categories'],'description':n['summary']}
  write(n['path'],page(n['title'],n['summary'],n['path'],body,schema))
 x_archive=ROOT/'public/data/x-archive.json'
 x_posts=json.loads(x_archive.read_text()).get('posts',[]) if x_archive.exists() else []
 for post in x_posts:
  if readable_post(post):
   path,content=x_page(post);write(path,content)
 for c in CATEGORIES:
  matching=[n for n in items if c in n['categories']];path='/kategori/'+cat_slug(c)+'/'
  body=f'<span class="kicker">Nyhetsarkiv</span><h1>{esc(c)}</h1><p>Svenska sammanfattningar med källor och sammanhang. En nyhet kan tillhöra flera kategorier.</p><ul>'+''.join(map(link,matching))+'</ul>'
  if not matching:body+='<p>Inga publicerade nyheter i kategorin ännu.</p>'
  write(path,page(c+' – nyheter',f'Nyheter om {c} på svenska med tydliga originalkällor.',path,body))
 sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+DOMAIN+esc(u)+'</loc></url>' for u in urls)+'</urlset>'
 (DIST/'sitemap.xml').write_text(sitemap);(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+DOMAIN+'/sitemap.xml\n')
 home=DIST/'index.html';text=home.read_text();text=text.replace('<noscript>Aktivera JavaScript för att använda Kryptokollen.</noscript>','<noscript><h1>Kryptokollen – kryptonyheter på svenska</h1><ul>'+''.join(map(link,items[:30]))+'</ul></noscript>');home.write_text(text)
 print(f'Exported {len(items)} articles, {len(x_posts)} permanent X pages and {len(CATEGORIES)} categories')
if __name__=='__main__':main()
