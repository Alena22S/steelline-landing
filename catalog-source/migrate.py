"""Переезд на основной домен одной командой.

  python3 catalog-source/migrate.py https://steelline.store            — подготовить сайт к индексации на домене
  python3 catalog-source/migrate.py https://steelline.store --check    — только проверить, ничего не меняя

Что делает:
  1. пересобирает статичные страницы (prototype-catalog/build.py) с адресом домена и БЕЗ запрета индексации;
  2. переводит адреса основной версии (canonical) главной, политики и согласия на домен;
  3. пишет sitemap.xml со всеми страницами для поисковиков и robots.txt со ссылкой на неё;
  4. пересобирает таблицу переадресаций и настройки nginx (catalog-source/redirects.py).
Прототипы с параметрами в адресе (prototype-catalog/catalog.html?cat=…, model.html?id=…, межкомнатные двери)
остаются закрытыми от индексации: у входных дверей и разделов теперь есть статичные страницы.
После запуска — проверить изменения (git diff) и опубликовать (push в main)."""
import datetime, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

if len(sys.argv) < 2 or not re.match(r'^https://[a-z0-9.-]+$', sys.argv[1].rstrip('/')):
    sys.exit('Укажите домен: python3 catalog-source/migrate.py https://steelline.store [--check]')
SITE = sys.argv[1].rstrip('/')
CHECK = '--check' in sys.argv


def read(p):
    return open(os.path.join(ROOT, p), encoding='utf-8').read()


def write(p, s):
    if CHECK:
        print('  [проверка] изменился бы', p)
    else:
        open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(s)


# 1. статичные страницы
if not CHECK:
    env = dict(os.environ, SITE_URL=SITE, INDEX='1')
    subprocess.run([sys.executable, os.path.join(ROOT, 'prototype-catalog', 'build.py')], env=env, check=True)

# 2. canonical у страниц в корне
for page in ('index.html', 'privacy.html', 'consent.html'):
    s = read(page)
    # canonical и превью для соцсетей (og:url, og:image) — на домен
    s2 = re.sub(r'((?:<link rel="canonical" href=|<meta property="og:(?:url|image)" content=)")https://[^/"]+', r'\1' + SITE, s)
    if s2 != s:
        write(page, s2)

# 3. карта сайта и robots.txt
pages = ['/']
for dirpath, _, files in os.walk(ROOT):
    rel = os.path.relpath(dirpath, ROOT).replace(os.sep, '/')
    if rel.split('/')[0] not in ('catalog', 'magazines', 'gid', 'port', 'diz', 'blog', 'sert') and not re.match(r'^st\d+$', rel) or 'index.html' not in files:
        continue
    html = open(os.path.join(dirpath, 'index.html'), encoding='utf-8').read()
    if 'name="robots" content="noindex' in html and not CHECK:
        sys.exit('Страница /%s всё ещё закрыта от индексации — сборка не прошла?' % rel)
    pages.append('/' + rel)
pages += ['/privacy.html', '/consent.html']


def prio(p):
    if p == '/': return '1.0'
    if p in ('/catalog', '/catalog/dom', '/catalog/kvartira', '/catalog/mezhkom', '/magazines', '/gid', '/port', '/diz'): return '0.9'
    if p in ('/blog', '/sert') or re.match(r'^/st\d+$', p): return '0.6'
    if p.count('/') == 3 and p.startswith('/catalog/'): return '0.8'  # разделы /catalog/dom/svarnie
    if p.startswith('/catalog/'): return '0.7'                         # модели
    return '0.3'


today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p in sorted(set(pages), key=lambda p: (-float(prio(p)), p)):
    sm.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>' % (SITE, p if p.endswith(('/', '.html')) else p + '/', today, prio(p)))
sm.append('</urlset>')
write('sitemap.xml', '\n'.join(sm) + '\n')

robots = """User-agent: *
Disallow: /send.php
# прототипы с параметрами в адресе закрыты мета-тегом noindex на самих страницах (не запрещаем — пусть роботы его видят)

User-agent: Yandex
Disallow: /send.php
Clean-param: utm_source&utm_medium&utm_campaign&utm_content&utm_term&yclid&gclid&_ym_debug&vitrina

Sitemap: %s/sitemap.xml
""" % SITE
write('robots.txt', robots)

# 4. переадресации
if not CHECK:
    subprocess.run([sys.executable, os.path.join(HERE, 'redirects.py')], check=True)

print('Домен:', SITE, '| страниц в карте сайта:', len(set(pages)), '| режим:', 'проверка' if CHECK else 'готово — проверьте git diff и опубликуйте')
