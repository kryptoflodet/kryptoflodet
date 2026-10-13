"""Publication rules shared by ingestion, archive and HTML export. No paid services."""
import datetime as dt, hashlib, re, unicodedata
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from swedish_quality import is_swedish_quality
UTC=dt.timezone.utc

def canonical_url(url):
 p=urlsplit(url)
 if p.scheme not in ('https','http') or not p.hostname or p.username or p.password:raise ValueError('Invalid source URL')
 query=[(k,v) for k,v in parse_qsl(p.query) if not k.lower().startswith('utm_') and k.lower() not in {'fbclid','gclid','ref','source'}]
 host=p.netloc.lower()
 if host.startswith('www.'):host=host[4:]
 if host in {'twitter.com','x.com'}:host='x.com'
 return urlunsplit((p.scheme,host,p.path.rstrip('/') or '/',urlencode(sorted(query)),''))

def slug(item):
 name=unicodedata.normalize('NFKD',item['title']).encode('ascii','ignore').decode().lower()
 return re.sub(r'[^a-z0-9]+','-',name).strip('-')[:78].rstrip('-')+'-'+item['id'][:10]

def readable(item):
 text=item.get('readerText','')
 return item.get('contentVersion')==2 and len(text.split())>=30 and item.get('translationStatus')=='reviewed-sv' and is_swedish_quality(item.get('title',''),item.get('summary',''),text) and not re.search(r'Läs originalartikeln för fullständiga|Se videon direkt i nyheten',text)

def enrich(item):
 text=item.get('originalTitle','')+' '+item.get('originalText','')
 lower=text.lower()
 kind='rapportering'
 if item.get('sourceType')=='INFLUENCER' or item.get('channel')=='X':kind='uttalande'
 if re.search(r'\b(predict\w*|forecast\w*|price target|prisprognos|could reach|may reach)\b',lower):kind='prognos'
 elif re.search(r'\b(rumou?r\w*|unconfirmed|rykte|obekräftat)\b',lower):kind='rykte'
 elif re.search(r'\b(analysis|analyst\w*|analys\w*)\b',lower):kind='analys'
 tags=list(item.get('coins',[]))
 categories=[]
 for symbol,name in [('BTC','Bitcoin'),('ETH','Ethereum')]:
  if symbol in tags:categories.append(name)
 if any(s not in ('BTC','ETH') for s in tags):categories.append('Altcoins')
 rules=[('Reglering',r'\b(sec|regulat\w*|court|law|legislation|domstol)\b'),('Institutionellt',r'\b(etf|etfs|institution\w*|blackrock|strategy|treasury)\b'),('Marknaden',r'\b(price|market|rises?|falls?|inflows?|outflows?|pris|marknad\w*)\b')]
 for category,pattern in rules:
  if re.search(pattern,lower):categories.append(category)
 if not categories:categories=['Marknaden']
 score=2; reasons=[]
 if re.search(r'\b(hack\w*|exploit\w*|breach|stolen|security patch|sårbarhet)\b',lower):score=5;reasons.append('Säkerhetsincident eller säkerhetsuppdatering')
 elif re.search(r'\b(approv\w*|reject\w*|ruling|launch\w*|collaborat\w*|integrat\w*|upgrade\w*|mainnet|buy\w*|bought|purchase\w*)\b',lower):score=4;reasons.append('Beslut, köp eller förändring i ett nätverk')
 elif re.search(r'\b(etfs?|inflows?|outflows?|record|all.time.high)\b',lower):score=3;reasons.append('Kapitalflöden eller marknadshändelse')
 if kind in {'prognos','rykte'}:score=min(score,2)
 if item.get('sourceType')=='INFLUENCER':score=min(score,2)
 item.update(contentType=kind,categories=list(dict.fromkeys(categories)),importance=score,importanceReason='; '.join(reasons) or 'Ordinarie kryptobevakning',breaking=False)
 if score>=4 and not item.get('why'):
  if 'Reglering' in categories:item['why']='Regler och myndighetsbeslut kan ändra villkoren för kryptotjänster. Ett förslag, ett beslut och en regel som har trätt i kraft är olika saker; läs källans besked för vad som faktiskt gäller.'
  elif re.search(r'\b(hack\w*|exploit\w*|breach|stolen|security patch)\b',lower):item['why']='Säkerhetsincidenter kan påverka tillgången till en tjänst och användarnas medel. Omfattning och orsaker behöver bekräftas; tidiga uppgifter kan förändras.'
  elif 'Institutionellt' in categories:item['why']='Institutionella köp och börshandlade produkter visar hur vissa aktörer får exponering mot krypto. Ett enskilt besked säger inte hur priset kommer att utvecklas.'
  else:item['why']='Förändringar i ett kryptonätverk eller en tjänst kan påverka hur den används. Skilj mellan en plan, en testversion och en funktion som faktiskt har blivit tillgänglig.'
 item.setdefault('slug',slug(item));item['path']='/nyheter/'+item['slug']+'/'
 return item

def deduplicate(items):
 result={}
 for n in items:
  try:key=canonical_url(n['originalUrl'])
  except (ValueError,KeyError):continue
  prev=result.get(key)
  if not prev or (readable(n),n.get('importedAt',''))>(readable(prev),prev.get('importedAt','')):result[key]=n
 return sorted(result.values(),key=lambda n:n['publishedAt'],reverse=True)

def select_important(items,now=None):
 now=now or dt.datetime.now(UTC)
 fresh=[n for n in items if readable(n) and n.get('importance',0)>=3 and n.get('contentType') not in {'rykte','prognos'} and 0<=(now-dt.datetime.fromisoformat(n['publishedAt'].replace('Z','+00:00'))).total_seconds()<=48*3600]
 return sorted(fresh,key=lambda n:(n['importance'],n['publishedAt']),reverse=True)[:5]
