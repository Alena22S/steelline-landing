"""Медленный обход каталога aurum-doors.store: коллекции → модели (и подколлекции эмали → модели).
Сохраняет HTML в catalog-source/aurum/html/<slug>.html. Уже скачанные страницы не перекачивает.
Tilda отвечает 403 на частые запросы — поэтому пауза между страницами и долгий откат при 403."""
import os, re, sys, time, urllib.request, urllib.error
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'html')
os.makedirs(OUT, exist_ok=True)
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
SKIP = re.compile(r'^(catalog|portfolio|diz|shops|system|peregorodki|sistem|3d|company|feretta|sert|soglashenie|cookie|personal|mdf|header|footer)$', re.I)
SEEDS = ['co', 'pd', 'pu', 'ni', 'zr', 'au', 'ag', 'lak', 'nalichie']
DELAY = 4


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.hrefs = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            h = dict(attrs).get('href')
            if h: self.hrefs.append(h)


def slug_of(h):
    h = h.strip()
    m = re.match(r'^https?://(?:www\.)?aurum-doors\.store/([^#?/]+)', h, re.I)
    s = m.group(1) if m else (h.split('#')[0] if re.match(r'^[a-z0-9_-]+(#.*)?$', h, re.I) else None)
    if not s or SKIP.match(s):
        return None
    return s


def get(slug):
    path = os.path.join(OUT, slug + '.html')
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        return open(path, encoding='utf-8').read(), False
    for attempt in range(5):
        req = urllib.request.Request('https://aurum-doors.store/' + slug, headers={'User-Agent': UA, 'Accept-Language': 'ru-RU,ru;q=0.9'})
        try:
            html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
            open(path, 'w', encoding='utf-8').write(html)
            return html, True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(slug, '404', flush=True); return None, True
            wait = 60 * (attempt + 1)
            print(slug, e.code, 'жду', wait, flush=True); time.sleep(wait)
        except Exception as e:
            print(slug, 'ошибка', e, flush=True); time.sleep(20)
    return None, True


queue = [(s, 0) for s in SEEDS]
seen = set(SEEDS)
n = 0
while queue:
    slug, depth = queue.pop(0)
    html, fetched = get(slug)
    n += 1
    print(n, slug, 'ok' if html else 'нет', 'осталось', len(queue), flush=True)
    if html and depth < 2:
        p = Links(); p.feed(html)
        for h in p.hrefs:
            s = slug_of(h)
            if s and s not in seen:
                seen.add(s); queue.append((s, depth + 1))
    if fetched:
        time.sleep(DELAY)
print('готово', n, flush=True)
