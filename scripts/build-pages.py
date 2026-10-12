"""Export real, indexable Pages documents. No server, API key or client router required."""
import datetime as dt,html,json,pathlib,re,shutil,unicodedata
from urllib.parse import urlsplit,parse_qs
from zoneinfo import ZoneInfo
from editorial import readable,enrich,deduplicate
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
 return f'''<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Kryptokollen</title><meta name="description" content="{esc(description[:180])}"><link rel="canonical" href="{DOMAIN}{esc(path)}"><meta property="og:locale" content="sv_SE"><meta property="og:site_name" content="Kryptokollen"><meta property="og:type" content="{'article' if schema and schema.get('@type')=='NewsArticle' else 'website'}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description[:180])}"><meta property="og:url" content="{DOMAIN}{esc(path)}"><meta property="og:image" content="{DOMAIN}/images/bitcoin-1280.webp"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.svg"><meta name="theme-color" content="#101214"><style>{CSS}</style><script type="application/ld+json">{structured}</script></head><body><a class="skip" href="#content">Till innehållet</a><header><a class="brand" href="/">Kryptokollen<span style="color:#b2e591">.</span></a><nav aria-label="Huvudnavigation"><a href="/">Senaste</a><a href="/idag/">Kryptokollen idag</a><a href="/kategori/bitcoin/">Bitcoin</a><a href="/kategori/ethereum/">Ethereum</a><a href="/kategori/altcoins/">Altcoins</a></nav></header><main id="content">{body}</main><footer>Kryptokollen · Självständiga svenska sammanfattningar med tydliga källor. Uppgifter från en källa är inte automatiskt oberoende bekräftade. Inget här är personlig investeringsrådgivning.<br><a href="/">Till nyhetsflödet</a> · <a href="/idag/">Dagsöversikter</a></footer></body></html>'''

def embed(n):
 if n['sourceId'] not in {'moon-video','rover-video','altcoin-daily-video','felix-video'}:return ''
 u=urlsplit(n['originalUrl']);video=None
 if u.scheme!='https' or u.username or u.password or u.port:return ''
 if u.hostname=='youtu.be':video=u.path[1:]
 elif u.hostname in {'www.youtube.com','youtube.com','m.youtube.com'}:
  video=parse_qs(u.query).get('v',[None])[0] if u.path=='/watch' else u.path.rstrip('/').split('/')[-1] if re.match(r'^/(shorts|live|embed)/',u.path) else None
 if not video or not re.fullmatch(r'[A-Za-z0-9_-]{11}',video):return ''
 return f'<h2>Se videon</h2><p class="meta">Sammanfattningen bygger på kanalens beskrivning. Videon spelas från YouTube på originalspråket.</p><iframe class="video" title="{esc(n["title"])}" loading="lazy" src="https://www.youtube-nocookie.com/embed/{video}" allow="encrypted-media; picture-in-picture; fullscreen" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'

def main():
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
 for c in CATEGORIES:
  matching=[n for n in items if c in n['categories']];path='/kategori/'+cat_slug(c)+'/'
  body=f'<span class="kicker">Nyhetsarkiv</span><h1>{esc(c)}</h1><p>Svenska sammanfattningar med källor och sammanhang. En nyhet kan tillhöra flera kategorier.</p><ul>'+''.join(map(link,matching))+'</ul>'
  if not matching:body+='<p>Inga publicerade nyheter i kategorin ännu.</p>'
  write(path,page(c+' – nyheter',f'Nyheter om {c} på svenska med tydliga originalkällor.',path,body))
 # Reproducible daily overviews built only from published material; never pretend old data is today's news.
 days={}
 for n in items:
  day=dt.datetime.fromisoformat(n['publishedAt'].replace('Z','+00:00')).astimezone(ZoneInfo('Europe/Stockholm')).date().isoformat();days.setdefault(day,[]).append(n)
 daily=[]
 for day,rows in sorted(days.items(),reverse=True):
  title='Kryptokollen idag – '+day;path='/idag/'+day+'/'
  selected=sorted(rows,key=lambda n:(n['importance'],n['publishedAt']),reverse=True)[:8]
  publishers=len({n['sourceId'] for n in rows});topics=[c for c in CATEGORIES if any(c in n['categories'] for n in rows)]
  intro=f'Den {day} innehåller Kryptokollens urval {len(rows)} publicerade nyheter från {publishers} källor. Bevakningen berör '+', '.join(topics)+'.'
  body=f'<span class="kicker">Dagsöversikt · svensk tid</span><h1>{esc(title)}</h1><p>{esc(intro)}</p><p>Översikten bygger på det material som klarat publiceringskontrollen och täcker inte allt som hänt på marknaden. Dagens pågående urval kan uppdateras.</p>'
  for kind,heading in [('rapportering','Rapporterade händelser'),('uttalande','Uttalanden'),('analys','Analyser'),('prognos','Prognoser'),('rykte','Obekräftade uppgifter')]:
   group=[n for n in selected if n['contentType']==kind]
   if group:body+=f'<h2>{heading}</h2><ul>'+''.join(map(link,group))+'</ul>'
  body+='<h2>Att hålla koll på</h2><p>Skilj mellan besked om planer och sådant som redan genomförts. Följ originalkällornas uppdateringar för förändrade villkor och bekräftelser. Prisprognoser i enskilda inlägg är inte fastställda utfall.</p>'
  write(path,page(title,intro,path,body));daily.append({'date':day,'path':path,'title':title,'count':len(rows)})
 today=dt.datetime.now(ZoneInfo('Europe/Stockholm')).date().isoformat()
 body='<h1>Kryptokollen idag</h1><p>Dagsöversikter från publicerade nyheter, grupperade efter svensk kalenderdag.</p>'
 if today not in days:body+='<p class="notice">Det finns ännu inget tillräckligt underlag för en dagsöversikt idag. Nedan visas tidigare publicerade dagar.</p>'
 body+='<ul>'+''.join(f'<li><a href="{d["path"]}">{esc(d["title"])}</a><small>{d["count"]} nyheter</small></li>' for d in daily)+'</ul>'
 write('/idag/',page('Kryptokollen idag','Dagens kryptonyheter samlade i en svensk översikt.','/idag/',body))
 (DIST/'data/daily.json').write_text(json.dumps({'days':daily},ensure_ascii=False))
 sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+DOMAIN+esc(u)+'</loc></url>' for u in urls)+'</urlset>'
 (DIST/'sitemap.xml').write_text(sitemap);(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+DOMAIN+'/sitemap.xml\n')
 home=DIST/'index.html';text=home.read_text();text=text.replace('<noscript>Aktivera JavaScript för att använda Kryptokollen.</noscript>','<noscript><h1>Kryptokollen – kryptonyheter på svenska</h1><ul>'+''.join(map(link,items[:30]))+'</ul><a href="/idag/">Kryptokollen idag</a></noscript>');home.write_text(text)
 print(f'Exported {len(items)} articles, {len(CATEGORIES)} categories, {len(daily)} daily overviews')
if __name__=='__main__':main()
