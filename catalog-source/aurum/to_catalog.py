"""aurum.json (из parse.py) → prototype-catalog/data/aurum.json + фото в WebP в prototype-catalog/img/aurum/.
Фото: двери в каждом цвете (GitHub), кружки цветов и погонаж (Tilda CDN). Уже сжатые файлы не перекачиваем."""
import hashlib, io, json, os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SITE = os.path.join(ROOT, 'prototype-catalog')
IMG = os.path.join(SITE, 'img', 'aurum')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'

src = json.load(open(os.path.join(HERE, 'aurum.json'), encoding='utf-8'))
jobs = {}  # локальный путь → (url, вид)


def local(url, kind, name=None):
    if not url:
        return ''
    if not name:
        name = hashlib.md5(url.encode()).hexdigest()[:12]
    rel = 'img/aurum/%s%s.webp' % ({'door': '', 'sw': 'sw/', 'mold': 'mold/', 'photo': 'ph/'}[kind], name)
    jobs[rel] = (url, kind)
    return rel


def fetch_convert(item):
    rel, (url, kind) = item
    path = os.path.join(SITE, rel)
    if os.path.exists(path):
        return rel, 'есть'
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40).read()
        im = Image.open(io.BytesIO(data))
        im = im.convert('RGBA') if im.mode in ('P', 'LA', 'RGBA') else im.convert('RGB')
        box = {'door': (700, 1300), 'sw': (96, 96), 'mold': (360, 360), 'photo': (900, 1200)}[kind]
        im.thumbnail(box, Image.LANCZOS)
        if kind == 'sw':  # кружок цвета — квадрат из центра
            w, h = im.size; m = min(w, h)
            im = im.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im.save(path, 'WEBP', quality=82 if kind != 'sw' else 88, method=6)
        return rel, 'ok'
    except Exception as e:
        return rel, 'ошибка %s %s' % (url, e)


def latin(t):
    # «Со1» на сайте Aurum иногда набрано кириллицей — приводим к латинице, как на страницах моделей
    return re.sub(r'^(С|с)(?=[oо]\d)', 'C', t).replace('Со', 'Co', 1) if re.match(r'^[СC][оo]\d', t) else t


in_stock = {s.lower().rstrip('n') for s in src.get('inStock', [])}


def natural(d):
    m = re.match(r'([a-z]+)(\d+)', d['slug'].lower())
    return (m.group(1), int(m.group(2))) if m else (d['slug'], 0)


# внутри коллекции — по номеру модели (Base 1, Base 2…), коллекции — в порядке разделов
corder = {c['slug']: i for i, c in enumerate(src['collections'])}
src['products'].sort(key=lambda d: (corder.get(d['collection'], 99), d.get('sub', ''), natural(d)))
products, counts = [], {}
for d in src['products']:
    coll = next(c for c in src['collections'] if c['slug'] == d['collection'])
    slug = d['slug'].lower()
    colors = []
    for c in d['colors']:
        if not c['name']:
            continue
        colors.append({'id': c['id'], 'name': c['name'], 'surcharge': c['surcharge'],
                       'swatch': local(c['swatch'], 'sw'),
                       'photo': local(c['photo'], 'door', '%s-%s' % (slug, c['id'])) if c.get('photo') else ''})
    photos = [c['photo'] for c in colors if c['photo']] or ([local(d['photo'], 'photo')] if d.get('photo') else [])
    photos += [local(u, 'photo') for u in d.get('extraPhotos', [])]
    # у эмали стиль берём из раздела «Двери в эмали» (в карточках моделей везде «Современный»)
    style = d.get('styleFallback') or next((s['value'] for s in d['specs'] if s['title'] == 'Стиль'), '') or coll.get('style', '')
    style = {'Современный': 'Современный', 'Минимализм': 'Минимализм'}.get(style, style)
    cats = ['mezhkom/' + d['collection']]
    stock = slug in in_stock
    if stock:
        cats.append('mezhkom/nalichie')
    for c in cats:
        counts[c] = counts.get(c, 0) + 1
    products.append({
        'id': 'au-' + slug, 'kind': 'interior', 'title': latin(d['title']).strip(), 'slug': slug,
        'oldUrl': 'https://aurum-doors.store/' + d['slug'],
        'collection': d['collection'], 'collectionName': (coll['name'] + ' ' + d['sub']) if d.get('sub') else coll['name'], 'cats': cats,
        'price': d.get('price') or 0, 'priceKit': d.get('priceKit') or 0,
        'photos': photos[:1] if colors else photos[:3], 'colors': colors, 'colorNote': d.get('colorNote', ''), 'colorNames': [c['name'] for c in colors],
        'glass': [g['name'] for g in d.get('glass', [])],
        'notes': d.get('notes', []), 'sizes': d.get('sizes', ''), 'desc': d.get('desc') or coll.get('desc', ''),
        'specs': d.get('specs', []),
        'molding': [{'name': m['name'], 'size': m['size'], 'group': m.get('group', ''), 'img': local(m['img'], 'mold')} for m in d.get('molding', [])],
        'style': [style] if style else [], 'window': ['Со стеклом' if d.get('glass') or d.get('glazed') else 'Глухая'],
        'inStock': stock,
        'sale': d['collection'] == 'kobalt',  # распродажа склада в Екатеринбурге: −40% на полотна коллекции Кобальт
        'scene': slug in ('au', 'ag'),  # у Аурума и Аргентума — фото в интерьере; у остальных — сама дверь
        # поля входных дверей — пустые, чтобы общий код каталога не спотыкался
        'coating': [], 'series': [], 'special': [], 'editions': [], 'place': ['Межкомнатные'], 'specialPrice': False, 'thermo': False,
    })

order = [c['slug'] for c in src['collections']]
categories = [{'slug': 'mezhkom/' + c['slug'], 'name': c['name'], 'lead': c.get('lead') or c.get('desc', ''), 'count': counts.get('mezhkom/' + c['slug'], 0)}
              for c in src['collections'] if counts.get('mezhkom/' + c['slug'])]
if counts.get('mezhkom/nalichie'):
    categories.append({'slug': 'mezhkom/nalichie', 'name': 'В наличии', 'lead': 'Межкомнатные двери Aurum, которые есть на складе в Екатеринбурге: забрать можно без ожидания производства.', 'count': counts['mezhkom/nalichie']})

if '--no-images' not in sys.argv:
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(fetch_convert, sorted(jobs.items())))
    bad = [r for r in res if r[1].startswith('ошибка')]
    print('фото: всего', len(res), 'новых', sum(1 for r in res if r[1] == 'ok'), 'ошибок', len(bad))
    for b in bad[:10]:
        print(' ', b[1])
    missing = {r[0] for r in bad}
    for p in products:  # битые фото не показываем
        for c in p['colors']:
            if c['photo'] in missing: c['photo'] = ''
            if c['swatch'] in missing: c['swatch'] = ''
        p['photos'] = [x for x in p['photos'] if x not in missing] or [c['photo'] for c in p['colors'] if c['photo']][:1]
        p['molding'] = [m for m in p['molding'] if m['img'] not in missing or not m['img']]

json.dump({'categories': categories, 'products': products}, open(os.path.join(SITE, 'data', 'aurum.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('товаров', len(products), 'разделы', [(c['name'], c['count']) for c in categories])
