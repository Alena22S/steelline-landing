"""Характеристики входных дверей → prototype-catalog/data/catalog.json.
Панели (внешняя/внутренняя) и серии берём из scraped.json (страницы steelline.store),
общие характеристики серий 92УТ и 100УТ — с инфографики steelline.store (spec92.png, spec100.png)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CAT = os.path.join(os.path.dirname(HERE), 'prototype-catalog', 'data', 'catalog.json')

INSUL = 'Минеральная плита высокой плотности, минеральная вата Knauf и фольгированный «Порилекс»'
SERIES = {
    '92УТ': {'rows': [
        {'title': 'Толщина полотна', 'value': '100 мм'},
        {'title': 'Толщина коробки', 'value': '113 мм'},
        {'title': 'Панели', 'value': 'Термовлагостойкие MDF 12 мм'},
        {'title': 'Терморазрыв', 'value': 'В полотне и в коробке'},
        {'title': 'Утеплитель', 'value': INSUL},
    ]},
    '100УТ': {'rows': [
        {'title': 'Толщина полотна', 'value': '100 мм'},
        {'title': 'Толщина коробки', 'value': '121 мм'},
        {'title': 'Панели', 'value': 'Термовлагостойкие MDF 16 мм'},
        {'title': 'Терморазрыв', 'value': 'В коробке'},
        {'title': 'Утеплитель', 'value': INSUL},
    ]},
}
TEH = {'teh92': '92УТ', 'teh100': '100УТ'}

# «Хаски»: общая таблица серии (картинка на вкладке «ХАСКИ B» на страницах Хаски steelline.store)
SERIES['Хаски В'] = {'rows': [
    {'title': 'Толщина полотна', 'value': '77 мм'},
    {'title': 'Толщина коробки', 'value': '76 мм'},
    {'title': 'Толщина металла', 'value': '1 мм'},
    {'title': 'Утепление полотна', 'value': 'Пенополистирол, терморазрыв'},
    {'title': 'Утепление коробки', 'value': 'Термобрус'},
    {'title': 'Контуры уплотнения', 'value': '3 контура: 2 уплотнителя D в полотне, 1 щелевой в коробке'},
    {'title': 'Ночная задвижка', 'value': 'Есть'},
    {'title': 'Петли', 'value': '3 шт. с 3D-регулировкой'},
    {'title': 'Стеклопакет', 'value': '3-камерный'},
    {'title': 'Регулятор притвора', 'value': 'Есть'},
    {'title': 'Наличники', 'value': 'Доп. опция'},
    {'title': 'Исполнение Хаски PRO', 'value': '3 терморазрыва и 4-камерный стеклопакет'},
]}

# собственные таблицы характеристик со страниц моделей (спец цена, умный замок, нестандарт) — catalog-source/sl-html
import re, sys
sys.path.insert(0, os.path.join(HERE, 'aurum'))
try:
    import zb
    from bs4 import BeautifulSoup
except ImportError:
    zb = None


def nice_val(v):
    v = re.sub(r'\s+', ' ', v).strip().rstrip('.')
    v = re.sub(r'(\d)\s*мм\.?$', r'\1 мм', v)
    v = re.sub(r'(\d)\.(\d)', r'\1,\2', v)  # 1.5 мм → 1,5 мм
    return v[:1].upper() + v[1:] if v else v


def page_specs(pid):
    path = os.path.join(HERE, 'sl-html', pid + '.html')
    if not zb or not os.path.exists(path):
        return [], None
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    rows, panels = [], None
    for r in zb.records(soup):
        els = r.get('els') or []
        if not rows and any(e.get('txt') == 'Толщина полотна' for e in els):
            labels = sorted([e for e in els if e.get('txt') and e['x'] < 400 and e['t'] == 'text'], key=lambda e: e['y'])
            for lab in labels:
                vals = [e for e in els if e.get('txt') and e['t'] == 'text' and e['x'] > lab['x'] + 300 and abs(e['y'] - lab['y']) <= 10]
                ticks = [e for e in els if e['t'] == 'image' and e['w'] <= 60 and e['x'] > 600 and abs(e['y'] - lab['y']) <= 12]
                if vals:
                    rows.append({'title': lab['txt'], 'value': nice_val(min(vals, key=lambda e: abs(e['y'] - lab['y']))['txt'])})
                elif ticks:
                    rows.append({'title': lab['txt'], 'value': 'Есть'})
    # панели — как в rescrape.py: две строки перед «Внешняя панель»
    t = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', open(path, encoding='utf-8').read())
    import html as _h
    t = _h.unescape(re.sub(r'<br\s*/?>', '\n', t)); t = re.sub(r'<[^>]+>', '\n', t); t = re.sub(r'[ \t\xa0]+', ' ', t)
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    if 'Внешняя панель' in lines:
        i = lines.index('Внешняя панель')
        if i >= 2:
            panels = {'outer': lines[i - 2], 'inner': lines[i - 1]}
    return rows, panels

data = json.load(open(CAT, encoding='utf-8'))
scraped = json.load(open(os.path.join(HERE, 'scraped.json'), encoding='utf-8'))
data['seriesSpecs'] = SERIES
n_panels = n_specs = 0
for p in data['products']:
    s = scraped.get(p['id']) or {}
    # Хаски: весь раздел + модели, у которых на странице та же вкладка «ХАСКИ B» или прямо написано «серии Хаски»
    page = os.path.join(HERE, 'sl-html', p['id'] + '.html')
    page_txt = open(page, encoding='utf-8').read() if os.path.exists(page) else ''
    if any(c == 'dom/husky' for c in p['cats']) or 'ХАСКИ B' in page_txt or 'серии Хаски' in page_txt:
        p['specSeries'] = ['Хаски В']
    own, own_panels = page_specs(p['id'])
    if own:
        p['specs'] = own
    if own_panels and not p.get('panels') and not (s.get('outer') or s.get('inner')):
        p['panels'] = own_panels
    if not s.get('ok'):
        continue
    if s.get('outer') or s.get('inner'):
        p['panels'] = {'outer': s.get('outer') or '', 'inner': s.get('inner') or ''}
        n_panels += 1
    keys = [TEH[t] for t in s.get('teh', []) if t in TEH]
    keys = sorted(set(keys), key=lambda k: int(k[:-2]))
    if keys and not p.get('specSeries'):
        p['specSeries'] = keys
        n_specs += 1
# терморазрыв: у «Двери в дом по спец цене» и части нестандартных он есть, хотя это не основная линейка —
# берём из заголовка/описания страницы модели на steelline.store («… дверь для дома с терморазрывом»)
for p in data['products']:
    page = os.path.join(HERE, 'sl-html', p['id'] + '.html')
    if not p.get('thermo') and os.path.exists(page):
        t = open(page, encoding='utf-8').read()
        title = re.search(r'<title>([^<]*)</title>', t)
        if (title and 'терморазрыв' in title.group(1).lower()) or re.search(r'content="[^"]*[Тт]ерморазрыв полотна', t):
            p['thermo'] = True
json.dump(data, open(CAT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('панели', sum(1 for p in data['products'] if p.get('panels')), 'серии', sum(1 for p in data['products'] if p.get('specSeries')),
      'свои таблицы', sum(1 for p in data['products'] if p.get('specs')), 'без характеристик', [p['title'] for p in data['products'] if not p.get('specSeries') and not p.get('specs')])
