"""Наши магазины со steelline.store/magazines → prototype-catalog/data/stores.json + фото салонов в WebP (img/stores/).
Страница Tilda: на каждый город — свой Zero Block с карточками салонов (текст, фото, карта).
Запуск: venv-python catalog-source/stores.py путь/к/magazines.html"""
import hashlib, io, json, os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'aurum'))
import zb
from bs4 import BeautifulSoup

SITE = os.path.join(os.path.dirname(HERE), 'prototype-catalog')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'

# блок → город (вкладки «Города:» на старой странице)
CITY = {
    'rec170364243': 'Екатеринбург', 'rec170364244': 'Сургут', 'rec170364245': 'Пермь', 'rec194972530': 'Тюмень',
    'rec321148033': 'Челябинск', 'rec208124950': 'Уфа', 'rec321131324': 'Курган', 'rec208124937': 'Нижневартовск',
    'rec321032545': 'Нижний Тагил', 'rec419520863': 'Миасс', 'rec739467539': 'Лангепас', 'rec170368476': 'Каменск-Уральский',
    'rec199306359': 'Серов', 'rec321035716': 'Новый Уренгой', 'rec547328884': 'Югорск',
}
# часы, которых нет в тексте десктопной версии (взяты из мобильной)
HOURS_FIX = {'Гарнизон 5': ['Пн-Пт 09.00-18.00', 'Сб 10.00-16.00']}
# салон есть только в мобильной версии страницы
EXTRA = [{'city': 'Нижневартовск', 'text': 'ТЦ Полигон\nул. Индустриальная 29, стр. 11\n8 950 514 12 29\n8(3466)401-001\n8(3466)407-005\nsdpoligon@mail.ru\nПн-Вс 09:00–18:00', 'photos': []}]

PHONE = re.compile(r'^(?:\+\s?7|8)[\s\d()\-]{9,}$')
HOURS = re.compile(r'^(?:Пн|Вт|Ср|Чт|Пт|Сб|Вс)', re.I)
PLACE = re.compile(r'(ТЦ|ТК|ТД|ИЦ|ЖК|салон|Салон|центр|ателье|пав\.|уровень|этаж|Галерея)')


def tel(p):
    d = re.sub(r'\D', '', p)
    if len(d) == 11 and d[0] == '8':
        d = '7' + d[1:]
    return '+' + d


def nice_phone(p):
    d = tel(p)[1:]
    if len(d) != 11:
        return p.strip()
    # мобильные и городские с кодом из 3 цифр: +7 (922) 207-75-52; с кодом из 4–5 цифр оставляем как на старом сайте
    if d[1] == '9' or d[1:4] in ('343', '342', '351', '347'):
        return '+7 (%s) %s-%s-%s' % (d[1:4], d[4:7], d[7:9], d[9:11])
    return p.strip().replace('  ', ' ')


def norm_hours(h):
    h = re.sub(r'\s*-\s*', '–', h.strip())
    h = re.sub(r'(?i)^пн–пт:?', 'Пн–Пт', h).replace('сб– вс', 'Сб–Вс').replace('сб–вс', 'Сб–Вс')
    h = re.sub(r'с (\d)', r'\1', h).replace(' до ', '–').replace(':', ' ', 1) if ' до ' in h else h
    h = h.replace('09:00', '9.00').replace('18:00', '18.00').replace('19:00', '19.00').replace('11:00', '11.00').replace('10:00', '10.00').replace('20:00', '20.00')
    h = re.sub(r'\s+', ' ', h).replace('Пн–Пт ', 'Пн–Пт: ').replace('Пн–Вс ', 'Пн–Вс: ').replace('Пн–Сб ', 'Пн–Сб: ').replace('Сб–Вс ', 'Сб–Вс: ')
    h = re.sub(r'^(Сб|Вс) ', r'\1: ', h)
    h = h.replace('::', ':').replace(': :', ':')
    return h[:1].upper() + h[1:]


def parse(text, city):
    lines = [l.strip().rstrip(',') for l in text.split('\n') if l.strip()]
    phones = [l for l in lines if PHONE.match(l)]
    emails = [l for l in lines if '@' in l]
    hours = [l for l in lines if HOURS.match(l)]
    rest = [l for l in lines if l not in phones and l not in emails and l not in hours]
    rest = [l for l in rest if l not in ('г. Арамиль',)]
    addr = [l for l in rest if re.search(r'(?i)(ул\.?|ул |пр\.|пр-т|мкрн|проспект)', l)]
    place = [l for l in rest if l not in addr]
    for k, v in HOURS_FIX.items():
        if any(k in a for a in addr):
            hours = v
    name = ''
    for p in place:
        m = re.search(r'(?:салон(?: дверей)?|Салон|ателье[^,]*?)\s*[«"]?([^«»"]+?)[»"]?$', p)
        if re.search(r'(?i)салон|ателье', p) and m:
            name = re.sub(r'(?i)^салон\s+', '', p).strip(' «»"')
    name = name or (place[0] if place and not re.search(r'(?i)уровень|этаж|пав\.', place[0]) else 'Стальная линия')
    # ТЦ, этаж, павильон — подсказка «где искать»
    where = [p for p in place if p != name and p.strip(' «»"') != name]
    addr_s = ', '.join(a.rstrip('.') for a in addr)
    return {
        'city': 'Арамиль' if 'Арамиль' in text else city,
        'name': name.replace('Интерьерный центр ', 'ИЦ ').strip() if False else name,
        'address': addr_s,
        'where': ', '.join(where),
        'phones': [{'text': nice_phone(p), 'tel': tel(p)} for p in phones],
        'emails': emails,
        'hours': [norm_hours(h) for h in hours],
    }

# Выверено вручную по тексту старой страницы (автоматический разбор путал коды городов в телефонах).
# Порядок — как на старой странице; фото и рейтинг подставляются из разбора.
def ph(*xs):
    return [{'text': x, 'tel': '+' + re.sub(r'\D', '', x)} for x in xs]
MANUAL = [
    dict(city='Екатеринбург', name='Интерьерный центр ASTROOM', where='6 этаж, галерея А', address='ул. Цвиллинга, 1',
         phones=ph('+7 (922) 207-75-52', '+7 (343) 385-28-03'), emails=['astroom@steelline.store'], hours=['Пн–Вс: 10:00–20:00']),
    dict(city='Арамиль', name='Салон «Дверная лавка»', where='', address='ул. Гарнизон, 5',
         phones=ph('+7 (919) 397-73-17'), emails=['zakazdver@bk.ru'], hours=['Пн–Пт: 9:00–18:00', 'Сб: 10:00–16:00']),
    dict(city='Сургут', name='Стальная линия', where='', address='ул. Профсоюзов, 51',
         phones=ph('+7 (922) 244-22-02'), emails=['dveri-surguta.galleri@mail.ru'], hours=['Пн–Сб: 10:00–20:00', 'Вс: 10:00–19:00']),
    dict(city='Сургут', name='Стальная линия', where='', address='ул. Восход, 1',
         phones=ph('+7 (3462) 31-03-31'), emails=['dm310331@mail.ru'], hours=['Пн–Вс: 10:00–20:00']),
    dict(city='Пермь', name='Стальная линия', where='ТЦ «Радуга»', address='ул. 1-я Красноармейская, 6',
         phones=ph('+7 (342) 207-32-40'), emails=['holz.raduga@mail.ru'], hours=['Пн–Сб: 10:00–21:00', 'Вс: 10:00–20:00']),
    dict(city='Тюмень', name='Стальная линия', where='ТК «Орион», 1 уровень, 2 линия', address='ул. Федюнинского, 43',
         phones=ph('+7 (3452) 38-80-74', '+7 (919) 950-80-74'), emails=['stroysnami72@yandex.ru'], hours=['Пн–Вс: 10:00–21:00']),
    dict(city='Тюмень', name='Салон «Geona»', where='ТК «Орион», 1 уровень, 1 линия', address='ул. Федюнинского, 43',
         phones=ph('+7 (3452) 69-90-45'), emails=[], hours=['Пн–Вс: 10:00–21:00']),
    dict(city='Тюмень', name='Стальная линия', where='ТЦ «1000 мелочей», павильон 4', address='ул. Молодёжная, 80/2',
         phones=ph('+7 (3452) 38-82-84'), emails=['stroysnami72@yandex.ru'], hours=['Пн–Вс: 9:00–19:00']),
    dict(city='Челябинск', name='Ателье паркета и дверей Le Pole', where='ЖК «Манхэттен»', address='ул. Труда, 174',
         phones=ph('+7 (351) 223-83-70'), emails=[], hours=['Пн–Пт: 10:00–19:00', 'Сб: 11:00–18:00', 'Вс: выходной']),
    dict(city='Челябинск', name='Салон Rada doors', where='ТЦ Palazzo stile & decor', address='ул. Российская, 142',
         phones=ph('+7 (958) 881-49-76', '+7 (904) 809-94-00'), emails=[], hours=['Пн–Пт: 10:00–20:00', 'Сб–Вс: 10:00–19:00']),
    dict(city='Уфа', name='Салон Odin doors', where='ТЦ «ВДНХ»', address='ул. Менделеева, 158',
         phones=ph('+7 (987) 137-05-49'), emails=[], hours=['Пн–Вс: 10:00–20:00']),
    dict(city='Курган', name='Стальная линия', where='', address='ул. Гоголя, 128',
         phones=ph('+7 (3522) 63-01-43', '+7 (908) 007-22-29'), emails=['dekor-parket@mail.ru'], hours=['Пн–Пт: 10:00–19:00', 'Сб: 10:00–18:00', 'Вс: 10:00–17:00']),
    dict(city='Нижневартовск', name='Стальная линия', where='ИЦ «Новый Гулливер»', address='ул. Индустриальная, 46, стр. 1',
         phones=ph('+7 (922) 781-83-20'), emails=[], hours=['Пн–Вс: 10:00–19:00']),
    dict(city='Нижний Тагил', name='Стальная линия', where='', address='пр. Мира, 34',
         phones=ph('+7 (953) 606-90-93'), emails=['nt-dveri-ggm@yandex.ru'], hours=['Пн–Вс: 10:00–19:00']),
    dict(city='Миасс', name='Стальная линия', where='', address='пр. Автозаводцев, 20',
         phones=ph('+7 (3513) 555-666', '+7 (919) 314-53-33'), emails=[], hours=['Пн–Пт: 10:00–19:00', 'Сб–Вс: 10:00–15:00']),
    dict(city='Лангепас', name='Стальная линия', where='ТЦ «Борислава»', address='ул. Мира, 4',
         phones=ph('+7 (34669) 5-08-67'), emails=[], hours=['Пн–Пт: 10:00–18:00', 'Сб–Вс: выходной']),
    # второй номер на старом сайте с ошибкой: «+7(908)20-05-05» — 10 цифр вместо 11; не показываем, пока не уточним
    dict(city='Каменск-Уральский', name='Стальная линия', where='ТЦ «Лео»', address='ул. 4-й Пятилетки, 45',
         phones=ph('+7 (3439) 36-99-90'), emails=['dvernisag-ku@mail.ru'], hours=['Пн–Вс: 10:00–20:00']),
    dict(city='Серов', name='Салон дверей «Триумф»', where='', address='ул. Ленина, 151',
         phones=ph('+7 (992) 022-84-14', '+7 (952) 147-04-50'), emails=['triumfserov@mail.ru'], hours=['Пн–Вс: 10:00–18:00']),
    dict(city='Новый Уренгой', name='Стальная линия', where='', address='мкр. Энтузиастов, 1',
         phones=ph('+7 (932) 096-87-67', '+7 (932) 056-51-54'), emails=['221061@list.ru'], hours=['Пн–Пт: 10:00–19:00', 'Сб–Вс: 10:00–18:00']),
    dict(city='Югорск', name='Стальная линия', where='ТД «Светлячок», центральное крыльцо', address='ул. Попова, 2В',
         phones=ph('+7 (922) 444-44-34', '+7 (922) 188-88-43'), emails=['dveri-yugorsk@mail.ru'], hours=['Пн–Вс: 11:00–19:00']),
    dict(city='Нижневартовск', name='Стальная линия', where='ТЦ «Полигон»', address='ул. Индустриальная, 29, стр. 11',
         phones=ph('+7 (950) 514-12-29', '+7 (3466) 40-10-01', '+7 (3466) 40-70-05'), emails=['sdpoligon@mail.ru'], hours=['Пн–Вс: 9:00–18:00'],
         ll='76.52939,60.93525'),  # карты на старом сайте нет — координаты дома по OpenStreetMap
]


def main(path):
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    stores, jobs = [], {}

    def umaps(rid):
        out = []
        for e in soup.select_one('#' + rid).select('.tn-elem[data-elem-type="html"]'):
            m = re.search(r'um=constructor%3A([0-9a-f]+)', str(e))
            if m:
                out.append((zb.num(e.get('data-field-top-value')), m.group(1)))
        return out
    for rid, city in CITY.items():
        els = zb.elems(soup.select_one('#' + rid))
        cards = sorted([e for e in els if e['t'] == 'text' and e['y'] > 300 and e.get('txt') and e['txt'] != 'Стальная линия' and '\n' in e['txt']], key=lambda e: e['y'])
        for i, c in enumerate(cards):
            top = c['y'] - 80
            bottom = cards[i + 1]['y'] - 80 if i + 1 < len(cards) else 1e9
            photos = sorted([e for e in els if e.get('img') and e['t'] == 'shape' and top <= e['y'] < bottom], key=lambda e: (round(e['y'] / 40), e['x']))
            # карта салона — конструктор Яндекс Карт со старой страницы (метка уже стоит на нужном доме)
            maps = [m for m in umaps(rid) if top <= m[0] < bottom]
            s = parse(c['txt'], city)
            if maps:
                s['map'] = maps[0][1]
            urls = list(dict.fromkeys(p['img'] for p in photos))
            s['photos'] = []
            for u in urls:
                rel = 'img/stores/%s.webp' % hashlib.md5(u.encode()).hexdigest()[:12]
                jobs[rel] = u
                s['photos'].append(rel)
            stores.append(s)
    for x in EXTRA:
        s = parse(x['text'], x['city']); s['photos'] = []
        stores.append(s)
    # отзывы на Яндекс Картах (виджет рейтинга со старой страницы)
    for s in stores:
        if 'Цвиллинга' in s['address']:
            s['rating'] = '8033680538'
        if 'Гарнизон' in s['address']:
            s['rating'] = '1564598838'

    def fetch(item):
        rel, url = item
        out = os.path.join(SITE, rel)
        if os.path.exists(out):
            return rel, 'есть'
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40).read()
            im = Image.open(io.BytesIO(data))
            try:
                from PIL import ImageOps
                im = ImageOps.exif_transpose(im)
            except Exception:
                pass
            im = im.convert('RGB')
            im.thumbnail((1400, 1400), Image.LANCZOS)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            im.save(out, 'WEBP', quality=80, method=6)
            return rel, 'ok'
        except Exception as e:
            return rel, 'ошибка %s' % e

    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(fetch, sorted(jobs.items())))
    bad = {r[0] for r in res if r[1].startswith('ошибка')}
    for s in stores:
        s['photos'] = [p for p in s['photos'] if p not in bad]
    print('фото', len(res), 'ошибок', len(bad))

    # координаты меток из карт старого сайта → статичная карта Яндекса (картинка без рекламы и лишних панелей)
    def coords(um):
        u = 'https://yandex.ru/map-widget/v1/?um=constructor%3A' + um + '&source=constructor'
        d = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=40).read().decode('utf-8', 'ignore')
        m = re.search(r'"coordinates":\[([\d.]+),([\d.]+)\]', d)
        return '%s,%s' % (m.group(1), m.group(2))

    def static_map(s):
        if not s.get('ll'):
            return
        lon, lat = s['ll'].split(',')
        # салон без фото — карта во всю ширину карточки, кадр шире
        size = '650,300' if not s['photos'] else '650,450'
        rel = 'img/stores/map-%s.webp' % hashlib.md5((s['ll'] + size).encode()).hexdigest()[:10]
        out = os.path.join(SITE, rel)
        if not os.path.exists(out):
            u = ('https://static-maps.yandex.ru/1.x/?ll=%s,%s&z=16&size=%s&l=map&lang=ru_RU&pt=%s,%s,pm2rdl' % (lon, lat, size, lon, lat))
            im = Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=40).read())).convert('RGB')
            im.save(out, 'WEBP', quality=82, method=6)
        s['mapImg'] = rel
    assert len(MANUAL) == len(stores), (len(MANUAL), len(stores))
    for s, m in zip(stores, MANUAL):
        assert s['city'] == m['city'], (s['city'], m['city'])
        s.update(m)
    # фасад ASTROOM — новое фото от заказчика (24.10.2026) вместо старого со старого сайта
    stores[0]['photos'][0] = 'img/stores/astroom.jpg'
    for s in stores:
        if s.get('map') and not s.get('ll'):
            s['ll'] = coords(s['map'])
        static_map(s)
    # Нижневартовск: оба салона рядом в списке
    stores.sort(key=lambda s: [x['city'] for x in MANUAL].index(s['city']))
    json.dump({'stores': stores}, open(os.path.join(SITE, 'data', 'stores.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for s in stores:
        print(s['city'], '|', s['name'], '|', s['address'], '|', s['where'], '|', [p['text'] for p in s['phones']], s['emails'], s['hours'], len(s['photos']))


main(sys.argv[1])
