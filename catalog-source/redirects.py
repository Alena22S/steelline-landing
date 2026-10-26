"""Таблица 301-переадресаций со старого сайта steelline.store (Tilda) на новый.
Источник старых адресов — карта старого сайта (catalog-source/sitemap.xml) + разделы из меню старого сайта, которых нет в карте.
Новые адреса — статичные страницы (prototype-catalog/build.py): /catalog/…, /magazines, /gid, /port, /diz.

Результат:
  catalog-source/redirects.csv        — таблица для проверки: старый адрес → новый, способ сопоставления
  server/nginx-steelline.conf         — фрагмент настроек nginx: адреса без «/» на конце и все переадресации
Запуск: python3 catalog-source/redirects.py"""
import csv, json, os, re
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
cat = json.load(open(os.path.join(ROOT, 'prototype-catalog', 'data', 'catalog.json'), encoding='utf-8'))
products = cat['products']
ours = {p['url'] for p in products}
old = [urlparse(u).path.rstrip('/') or '/' for u in re.findall(r'<loc>([^<]*)', open(os.path.join(HERE, 'sitemap.xml'), encoding='utf-8').read())]
# разделы из меню старого сайта (в карте их нет, но на них ведут ссылки)
old += ['/st3', '/100u', '/nalichie', '/zakaz', '/husky', '/dvupol', '/100', '/smartkv', '/70']

# страницы, которые есть на новом сайте по тем же адресам (переадресация не нужна)
SAME = {'/', '/catalog', '/magazines', '/gid', '/port', '/diz', '/blog', '/st1', '/st2', '/st4', '/st7', '/st8', '/st9', '/st10'} | {'/catalog/' + c['slug'] for c in cat['categories']} | {'/catalog/dom', '/catalog/kvartira'} | ours

# разделы и служебные страницы старого сайта
FIXED = {
    '/caralog/kvartira/marker/avrora2': '/catalog/kvartira/marker/avrora2',   # опечатка в адресе старого сайта
    '/catalog/kvartira/zakaznie': '/catalog/kvartira', '/catalog/kvartira/nalichie': '/catalog/kvartira',
    '/100u': '/catalog/dom/svarnie', '/nalichie': '/catalog/dom', '/zakaz': '/catalog/dom/markeri', '/husky': '/catalog/dom/husky',
    '/huskygl': '/catalog/dom/husky', '/dvupol': '/catalog/dom/nestandart', '/100': '/catalog/kvartira', '/smartkv': '/catalog/kvartira/smart',
    '/70': '/catalog/kvartira/marker',
    '/personal': '/privacy.html', '/cookie': '/privacy.html', '/soglashenie': '/consent.html',
    '/teh92': '/gid', '/teh100': '/gid', '/sunteh': '/gid', '/tehno15b': '/gid',
    # пока не перенесены — ведём на ближайший раздел (см. «Что осталось» в отчёте)
    # /sert — пока нет действующих сертификатов, ведём на главную; когда страница соберётся, убрать строку
    **({} if os.path.isdir(os.path.join(ROOT, 'sert')) else {'/sert': '/'}),
    '/acz': '/catalog', '/news1': '/blog', '/otzyv': '/port', '/land': '/', '/st3': '/st10',
    '/vk': 'https://vk.com/steellinerussia', '/inst': 'https://instagram.com/steelline_ru',
    '/dvery_mall': '/', '/goodzon': '/', '/kp2': '/catalog', '/page23376484.html': '/', '/page30979446.html': '/',
    '/page106020236.html': '/', '/page125724526.html': '/',
}


def base(slug):
    """«benvil2», «arktik2-1», «beverly92» → «benvil», «arktik», «beverly»: без цифр и вариантов в конце"""
    return re.sub(r'(-?\d+)+$', '', slug.lower())


# модели: по названию в адресе (без цифр на конце), сначала в том же разделе
by_base = {}
for p in products:
    by_base.setdefault(base(p['url'].rsplit('/', 1)[1]), []).append(p)
TRANSLIT_FIX = {'beverly': 'beverli', 'kvins': 'kvins', 'kallisto': 'kallisto', 'irving': 'irving'}


TR = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
      'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
      'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'}
for p in products:  # ещё и по названию латиницей: «Беверли» → beverli
    t = base(re.sub(r'[^a-z0-9]', '', ''.join(TR.get(c, c) for c in p['title'].lower())))
    if p not in by_base.setdefault(t, []):
        by_base[t].append(p)


def fuzzy(b):
    """похожее название: beverly ≈ beverli, kallisto ≈ kalisto — только при высокой похожести"""
    import difflib
    best = difflib.get_close_matches(b, list(by_base), n=1, cutoff=0.84)
    return by_base[best[0]] if best else []


def match_model(path):
    slug = path.rsplit('/', 1)[1]
    b = TRANSLIT_FIX.get(base(slug), base(slug))
    cands = by_base.get(b, []) or fuzzy(b)
    if not cands:
        return None
    section = path.rsplit('/', 1)[0]
    same = [p for p in cands if p['url'].rsplit('/', 1)[0] == section]
    return (same or cands)[0]['url']


rows = []
for path in sorted(set(old)):
    if path in SAME:
        continue
    if path in FIXED:
        rows.append((path, FIXED[path], 'раздел / служебная'))
        continue
    m = match_model(path)
    if m:
        rows.append((path, m, 'модель (по названию)'))
    elif path.startswith('/catalog/'):
        section = path.rsplit('/', 1)[0]
        rows.append((path, section if section in SAME else '/catalog', 'снятая модель → раздел'))
    else:
        rows.append((path, '/catalog', 'старый лендинг → каталог'))
# старые адреса прототипа на тестовом сайте → новые разделы (ссылки могли попасть в рекламу и закладки)
for a, b in [('/prototype-catalog/stores.html', '/magazines'), ('/prototype-catalog/gid.html', '/gid'),
             ('/prototype-catalog/portfolio.html', '/port'), ('/prototype-catalog/designers.html', '/diz')]:
    rows.append((a, b, 'прототип → раздел'))

with open(os.path.join(HERE, 'redirects.csv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    w.writerow(['старый адрес', 'новый адрес', 'как сопоставлено'])
    w.writerows(rows)

conf = ['# Фрагмент для server { … } сайта steelline.store (nginx). Сгенерирован catalog-source/redirects.py — не править вручную.',
        '#',
        '# 1) Адреса страниц без «/» на конце, как на старом сайте: /catalog/dom/svarnie/agios → файл …/agios/index.html',
        'location / {',
        '    try_files $uri $uri/index.html $uri/ =404;',
        '}',
        '',
        '# 2) 301-переадресации со старых адресов (%d шт.)' % len(rows)]
for a, b, how in rows:
    conf.append('location = %s { return 301 %s; }  # %s' % (a, b, how))
os.makedirs(os.path.join(ROOT, 'server'), exist_ok=True)
open(os.path.join(ROOT, 'server', 'nginx-steelline.conf'), 'w', encoding='utf-8').write('\n'.join(conf) + '\n')

from collections import Counter
print('старых адресов:', len(set(old)), '| те же адреса на новом сайте:', len(set(old) & SAME), '| переадресаций:', len(rows))
print(Counter(r[2] for r in rows))
for r in rows:
    if r[2] != 'модель (по названию)':
        continue
    print('  ', r[0], '→', r[1])
