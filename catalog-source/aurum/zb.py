"""Разбор страниц Tilda: блоки Zero Block (T396) → список элементов с координатами, текстом, ссылками и картинками."""
import json, os, re
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))


def load(slug):
    path = os.path.join(HERE, 'html', slug + '.html')
    if not os.path.exists(path):
        return None
    return BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')


def text_of(el):
    for br in el.find_all('br'):
        br.replace_with('\n')
    t = el.get_text()
    t = re.sub(r'[ \t ]+', ' ', t)
    t = re.sub(r' *\n *', '\n', t)
    return t.strip()


def num(v):
    """'168', '168px', '-12.5' → число; пусто или непонятно → 0"""
    m = re.match(r'\s*(-?\d+(?:\.\d+)?)', v or '')
    return float(m.group(1)) if m else 0.0


def elems(rec):
    out = []
    for e in rec.select('.tn-elem'):
        f = lambda k: e.get('data-field-%s-value' % k)
        o = {'t': e.get('data-elem-type'), 'y': num(f('top')), 'x': num(f('left')), 'w': num(f('width')), 'h': num(f('height'))}
        atom = e.select_one('.tn-atom')
        a = e.find('a') or (atom if atom is not None and atom.name == 'a' else None)
        if a is not None and a.get('href'):
            o['href'] = a['href']
        img = e.find('img')
        src = (img and (img.get('data-original') or img.get('src'))) or (atom is not None and atom.get('data-original')) or ''
        if src:
            o['img'] = src
        inp = e.select_one('.tn-atom__inputs-data')
        if inp is not None and inp.get('data-value'):
            try:
                o['form'] = json.loads(inp['data-value'])
            except ValueError:
                pass
        if o['t'] in ('text', 'button') and atom is not None:
            o['txt'] = text_of(atom)
        out.append(o)
    return out


def records(soup, desktop=True):
    """Блоки страницы без шапки и подвала. desktop=True — пропускаем мобильные дубли (data-screen-max < 980)."""
    out = []
    root = soup.select_one('#allrecords')
    for r in root.select('.r'):
        if r.find_parent(id='t-header') or r.find_parent(id='t-footer') or r.find_parent('header') or r.find_parent('footer'):
            continue
        smax = r.get('data-screen-max') or ''
        if desktop and smax and int(re.sub(r"\D", "", smax) or 9999) <= 980:
            continue
        # «вставленные» Zero Block приходят как тип 121 с data-alias-record-type=396
        rec = {'id': r.get('id'), 'type': r.get('data-alias-record-type') or r.get('data-record-type')}
        if rec['type'] == '396':
            rec['els'] = elems(r)
        else:
            rec['text'] = text_of(r)
            rec['imgs'] = list(dict.fromkeys(i.get('data-original') or i.get('src') for i in r.select('[data-original], img') if (i.get('data-original') or i.get('src'))))
            rec['links'] = list(dict.fromkeys(a.get('href') for a in r.find_all('a') if a.get('href')))
        out.append(rec)
    return out
