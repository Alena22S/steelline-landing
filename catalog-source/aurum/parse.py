"""Сборка данных межкомнатных дверей Aurum из скачанных страниц (html/) → aurum.json.
Берём только данные: модели, цены, цвета, описания, характеристики. Дизайн — наш."""
import json, os, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zb

HERE = os.path.dirname(os.path.abspath(__file__))
GITHUB = 'https://olehmusihin.github.io/aurumdoors/'
TREE = set()
_tree_path = os.path.join(HERE, 'github-tree.json')
if os.path.exists(_tree_path):
    TREE = {x['path'] for x in json.load(open(_tree_path))['tree'] if x['type'] == 'blob'}

# коллекции: slug на aurum → наш раздел
COLLECTIONS = [
    ('co', 'kobalt', 'Кобальт'),
    ('pd', 'palladiy', 'Палладий'),
    ('pu', 'plutoniy', 'Плутоний'),
    ('ni', 'nikel', 'Никель'),
]
HIDDEN = [('zr', 'Цирконий'), ('au', 'Аурум'), ('ag', 'Аргентум')]


def hparams(href):
    """'#doorColor=2&doorPrice=1725&title_tooltip=..&doorText=..' → dict"""
    q = href.split('#', 1)[-1].replace('&amp;', '&')  # в части ссылок Tilda «&» экранирован дважды
    return {k: v for k, v in urllib.parse.parse_qsl(q, keep_blank_values=True)}


def zrecs(slug):
    s = zb.load(slug)
    if s is None:
        return None, []
    return s, [r for r in zb.records(s) if r['type'] == '396']


def num(s):
    s = re.sub(r'[^\d]', '', s or '')
    return int(s) if s else None


def nice(name):
    """'Силк грей' / 'WARM GREY' / 'Дуб Темный' → единый вид: первая буква заглавная"""
    name = re.sub(r'\s+', ' ', name).strip()
    if name.isupper():
        name = name.capitalize()
    fix = {'Warm grey': 'Warm Grey', 'Deep blue': 'Deep Blue', 'Deep green': 'Deep Green', 'Deep black': 'Deep Black',
           'Дуб Темный': 'Дуб тёмный', 'Дуб темный': 'Дуб тёмный', 'Milk': 'Милк', 'Warm Grey': 'Warm Grey', 'Орех пекан': 'Орех пекан'}
    return fix.get(name, name)


def prices(els):
    """Калькулятор Tilda: polotno = '17462', комплект = 'polotno + 9030'"""
    for e in els:
        if not e.get('form'):
            continue
        exprs = [f.get('li_expr') for f in e['form'] if f.get('li_type') == 'fr' and f.get('li_expr')]
        if not exprs:
            continue
        polotno = num(exprs[0]) if re.fullmatch(r'\s*\d+\s*', exprs[0]) else None
        kit = None
        if len(exprs) > 1:
            m = re.fullmatch(r'\s*polotno\s*\+\s*(\d+)\s*', exprs[1])
            kit = polotno + int(m.group(1)) if (m and polotno) else (num(exprs[1]) if re.fullmatch(r'\s*\d+\s*', exprs[1]) else None)
        return polotno, kit
    return None, None


def pairs(els, labels_max_x=200):
    """Характеристики: подпись слева, значение справа на той же высоте"""
    texts = [e for e in els if e.get('txt')]
    out = []
    labels = sorted([e for e in texts if e['x'] < labels_max_x and len(e['txt']) < 40 and e['txt'] != 'Характеристики'], key=lambda e: e['y'])
    for lab in labels:
        cand = [e for e in texts if e['x'] > lab['x'] + 150 and abs(e['y'] - lab['y']) <= 12]
        if cand:
            v = min(cand, key=lambda e: abs(e['y'] - lab['y']))
            out.append({'title': lab['txt'], 'value': v['txt'].replace('\n', ' ')})
    return out


def photo_for(folder, color, glass_ids):
    """Фото двери в цвете: файл <цвет><стекло>.jpeg в репозитории; сначала стекло по умолчанию (1), потом любое"""
    if not folder:
        return None
    for g in ['1'] + [g for g in glass_ids if g != '1'] + ['']:
        p = '%s/%s%s.jpeg' % (folder, color, g)
        if p in TREE:
            return GITHUB + p
    return None


def model(slug):
    s, recs = zrecs(slug)
    if not recs:
        return None
    main = recs[0]['els']
    texts = sorted([e for e in main if e.get('txt')], key=lambda e: (e['y'], e['x']))
    top = [e for e in texts if e['y'] < 60 and not e['txt'].startswith('Вернуться')]
    title = min(top, key=lambda e: e['x'])['txt'] if top else (s.title.string if s.title else slug)
    door = next((e for e in main if e.get('href', '').startswith('#door=')), None)
    folder = door['href'].split('=', 1)[1] if door else None
    if not folder and any(t.startswith(slug.capitalize() + '/') for t in TREE):
        folder = slug.capitalize()  # у Zr1 нет ссылки #door, но фото в репозитории лежат в папке Zr1
    glass = []
    for e in main:
        if e.get('href', '').startswith('#glass='):
            p = hparams(e['href'])
            if not any(g['id'] == p.get('glass') for g in glass):
                glass.append({'id': p.get('glass'), 'name': nice(p.get('glassText') or p.get('title_tooltip') or '')})
    colors = []
    for e in sorted(main, key=lambda e: (e['y'], e['x'])):
        if e.get('href', '').startswith('#doorColor='):
            p = hparams(e['href'])
            cid = p.get('doorColor')
            if any(c['id'] == cid for c in colors):
                continue
            colors.append({'id': cid, 'name': nice(p.get('doorText') or p.get('title_tooltip') or ''),
                           'surcharge': (p.get('doorPrice') or '1') not in ('', '0', '1'),
                           'swatch': e.get('img', ''),
                           'photo': photo_for(folder, cid, [g['id'] for g in glass])})
    polotno, kit = prices(main)
    notes = [e['txt'] for e in texts if e['txt'].startswith('*')]
    sizes = next((e['txt'] for r in recs for e in r['els'] if e.get('txt', '').startswith('Размеры')), '')
    specs, molding, mgroups = [], [], set()
    for r in recs[1:]:
        tx = [e for e in r['els'] if e.get('txt')]
        head = next((e['txt'] for e in sorted(tx, key=lambda e: e['y'])), '')
        if head.startswith('Характеристики') and not specs:
            specs = pairs(r['els'])
        elif head in ('Погонаж', 'Коробочный брус', 'Наличники', 'Капители') and head not in mgroups:
            mgroups.add(head)
            imgs = [e for e in r['els'] if e['t'] == 'image' and e.get('img')]
            for t in sorted([e for e in tx if e['txt'] != head], key=lambda e: e['x']):
                name, _, size = t['txt'].partition('\n')
                im = min(imgs, key=lambda i: abs((i['x'] + i['w'] / 2) - (t['x'] + t['w'] / 2)), default=None)
                size = size.strip()
                if size and not re.match(r'^Размер', size):  # «Компланарный коробочный брус\nAverse» — это часть названия
                    name, size = name.strip() + ' ' + size, ''
                molding.append({'name': name.strip(), 'size': re.sub(r'^Размер:?\s*', '', size), 'img': im['img'] if im else '',
                                'group': '' if head == 'Погонаж' else head})
    default_photo = door.get('img') if door else ''
    extra = []
    if not door:  # эмаль: фото двери без ссылки #door, рядом широкое фото в интерьере
        pics = [e for e in main if e['t'] == 'image' and e.get('img') and e['w'] >= 200]
        narrow = sorted([e for e in pics if e['w'] < 450], key=lambda e: e['x'])
        wide = [e for e in pics if e['w'] >= 450]
        default_photo = narrow[0]['img'] if narrow else (wide[0]['img'] if wide else '')
        extra = [e['img'] for e in wide if e['img'] != default_photo]
    color_note = 'Любой цвет по палитрам RAL Classic и NCS' if any('ЛЮБОЙ ЦВЕТ' in e['txt'].upper() for e in texts) else ''
    return {'slug': slug, 'title': title.replace('\n', ' '), 'folder': folder, 'price': polotno, 'priceKit': kit,
            'colors': colors, 'glass': glass, 'notes': notes, 'sizes': sizes, 'specs': specs, 'molding': molding,
            'photo': default_photo, 'extraPhotos': extra, 'colorNote': color_note, 'defaultColor': next((e['txt'] for e in main if e.get('href') == '#doorText'), '')}


def collection(slug):
    s, recs = zrecs(slug)
    els = recs[0]['els'] if recs else []
    desc = next((e['txt'] for e in sorted(els, key=lambda e: e['y']) if e.get('txt') and len(e['txt']) > 80), '')
    links = []
    for e in sorted([e for r in recs for e in r['els'] if e.get('href')], key=lambda e: (e['y'], e['x'])):
        h = e['href']
        m = re.match(r'^(?:https?://aurum-doors\.store/)?([a-z]+\d+n?)(?:#.*)?$', h, re.I)
        if m and m.group(1) not in links:
            links.append(m.group(1))
    return {'title': s.title.string if s and s.title else slug, 'desc': desc, 'models': links}


def rub(n):
    return '{:,}'.format(n).replace(',', ' ') + ' ₽'


def hidden(slug, name):
    """Скрытые двери Аурум / Аргентум: страница-конструктор → одна карточка коллекции.
    Цены «от»: за полотно и за комплект; варианты отделки — строками характеристик."""
    s, recs = zrecs(slug)
    els = [e for r in recs for e in r['els']]
    texts = sorted([e for e in els if e.get('txt')], key=lambda e: (e['y'], e['x']))
    desc = next((e['txt'].replace('\n', ' ') for e in texts if len(e['txt']) > 80 and not e['txt'].startswith('*')), '')
    colors = []
    for e in sorted(els, key=lambda e: (e['y'], e['x'])):
        if e.get('href', '').startswith('#doorColor='):
            p = hparams(e['href'])
            nm = nice(p.get('doorText') or p.get('title_tooltip') or '')
            if nm and not any(c['name'] == nm for c in colors):
                colors.append({'id': p.get('doorColor'), 'name': nm, 'surcharge': (p.get('doorPrice') or '1') not in ('', '0', '1'), 'swatch': e.get('img', ''), 'photo': None})
    cnames = {c['name'].lower() for c in colors} | {'deep black', 'силк грей', 'дуб темный'}
    kits, cloths, rows = [], [], []
    for i, e in enumerate(texts):
        t = e['txt']
        m = re.search(r'комплекта?\s+от\s+([\d\s]+)р', t)
        if m:
            kit = num(m.group(1)); kits.append(kit)
            head = next((x['txt'] for x in reversed(texts[:i]) if x['x'] < 100 and len(x['txt']) < 60 and not re.search(r'\d', x['txt']) and x['txt'] not in ('Цвет', 'Кромки') and x['txt'].lower() not in cnames), '')
            if head:
                head = re.sub(r'^Варианты HPL панелей.*', 'HPL-панели Gentas', head)
                rows.append({'title': head, 'value': 'комплект от ' + rub(kit)})
        for m in re.finditer(r'Цена за полотно[^\n]*\n([\d\s]+)р[\s\S]*?Цена за комплект[^\n]*\n([\d\s]+)р', t):
            cloths.append(num(m.group(1))); kits.append(num(m.group(2)))
    imgs = sorted([e for e in els if e['t'] in ('image', 'shape') and e.get('img') and e['w'] >= 300], key=lambda e: -e['w'] * (e['h'] or 1))
    notes = [e['txt'].replace('\n', ' ') for e in texts if e['txt'].startswith('*')]
    return {'slug': slug, 'title': name, 'folder': None, 'price': min(cloths) if cloths else None, 'priceKit': min(kits) if kits else None,
            'colors': colors, 'glass': [], 'notes': notes[:1], 'sizes': '', 'specs': rows, 'molding': [],
            'photo': imgs[0]['img'] if imgs else '', 'desc': desc, 'defaultColor': ''}


def emal_groups():
    """Страница «Двери в эмали»: подколлекции по стилям (Современный / Неоклассический / Классический)"""
    s, recs = zrecs('lak')
    els = recs[0]['els'] if recs else []
    heads = sorted([e for e in els if e.get('txt') and e['txt'].endswith('стиль')], key=lambda e: e['y'])
    desc = next((e['txt'].replace('\n', ' ') for e in sorted(els, key=lambda e: e['y']) if e.get('txt') and len(e['txt']) > 80), '')
    out = []
    for e in sorted([e for e in els if e.get('href') and re.fullmatch(r'[a-z]+', e['href'])], key=lambda e: (e['y'], e['x'])):
        head = next((h['txt'] for h in reversed(heads) if h['y'] < e['y']), '')
        style = {'Современный стиль': 'Современный', 'Неоклассический стиль': 'Неоклассика', 'Классический стиль': 'Классика'}.get(head, '')
        if e['href'] not in [o['slug'] for o in out]:
            out.append({'slug': e['href'], 'style': style})
    return desc, out


def stock_list():
    c = collection('nalichie')
    return [m for m in c['models'] if m.lower().endswith('n')]


if __name__ == '__main__':
    out = {'collections': [], 'products': [], 'missing': [], 'inStock': stock_list()}
    for src, our, name in COLLECTIONS:
        c = collection(src)
        out['collections'].append({'slug': our, 'src': src, 'name': name, 'desc': c['desc'], 'models': c['models']})
        for m in c['models']:
            d = model(m)
            if not d:
                out['missing'].append(m); continue
            d['collection'] = our
            out['products'].append(d)

    # эмаль: подколлекции → модели
    edesc, groups = emal_groups()
    out['collections'].append({'slug': 'emal', 'src': 'lak', 'name': 'Эмаль', 'desc': edesc,
                               'lead': 'Двери в эмали: современные, неоклассические и классические модели с покраской в любой цвет по RAL.'})
    for g in groups:
        c = collection(g['slug'])
        sub = re.split(r'\s+-\s+', c['title'])[0].strip() or g['slug'].capitalize()
        for m in c['models']:
            if not re.fullmatch(g['slug'] + r'\d+', m):
                continue
            d = model(m)
            if not d:
                out['missing'].append(m); continue
            d['collection'] = 'emal'
            d['sub'] = sub
            d['styleFallback'] = g['style']
            d['desc'] = d.get('desc') or c['desc']
            out['products'].append(d)

    # скрытые двери
    out['collections'].append({'slug': 'skrytye', 'src': 'zr', 'name': 'Скрытые двери',
                               'lead': 'Двери на скрытом алюминиевом коробе Invisible: полотно в одной плоскости со стеной, под покраску, обои или в цвет.'})
    for src, name in [('au', 'Аурум'), ('ag', 'Аргентум')]:
        d = hidden(src, name)
        d['collection'] = 'skrytye'
        out['products'].append(d)
    zr = model('zr1')
    if zr:
        zr['collection'] = 'skrytye'
        zr['desc'] = collection('zr')['desc']
        out['products'].append(zr)

    json.dump(out, open(os.path.join(HERE, 'aurum.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('товаров', len(out['products']), 'в наличии', out['inStock'], 'нет страниц', out['missing'])
