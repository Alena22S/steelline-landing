"""Медленно скачивает страницы входных дверей со steelline.store (у которых нет характеристик серии) → catalog-source/sl-html/<id>.html"""
import json, os, sys, time, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'sl-html'); os.makedirs(OUT, exist_ok=True)
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'
d = json.load(open(os.path.join(os.path.dirname(HERE), 'prototype-catalog', 'data', 'catalog.json'), encoding='utf-8'))
todo = [p for p in d['products'] if not p.get('specSeries') or not p.get('panels')]
print('страниц', len(todo), flush=True)
for n, p in enumerate(todo, 1):
    path = os.path.join(OUT, p['id'] + '.html')
    if os.path.exists(path) and os.path.getsize(path) > 5000: continue
    for attempt in range(4):
        try:
            html = urllib.request.urlopen(urllib.request.Request(p['oldUrl'], headers={'User-Agent': UA, 'Accept-Language': 'ru-RU,ru;q=0.9'}), timeout=40).read().decode('utf-8', 'replace')
            open(path, 'w', encoding='utf-8').write(html); break
        except urllib.error.HTTPError as e:
            print(p['title'], e.code, flush=True)
            if e.code == 404: break
            time.sleep(60 * (attempt + 1))
        except Exception as e:
            print(p['title'], 'ошибка', e, flush=True); time.sleep(20)
    print(n, p['title'], 'ok' if os.path.exists(path) else 'нет', flush=True)
    time.sleep(5)
print('готово', flush=True)
