"""Собирает прототипы страниц каталога из частей лендинга (шапка, подвал, форма заявки, уведомление о cookie).
Запуск: python3 prototype-catalog/build.py  → prototype-catalog/catalog.html и model.html
В Astro эти части станут общими компонентами; здесь — только для согласования дизайна.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'prototype-catalog')
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()


def part(start, end):
    i = src.index(start)
    j = src.index(end, i) + len(end)
    return src[i:j]


head = src[src.index('<!doctype html>'):src.index('</head>')]
header = part('<header class="header"', '</header>')
footer = part('<footer class="footer" id="footer">', '</footer>')
cookie = part('<div class="cookie"', '</div>\n  </div>')
sticky = part('<a class="btn btn--gradient sticky-cta"', '</a>')
lead = part('<dialog class="lead" id="lead"', '</dialog>')
callback = part('<button class="callback-fab"', '</dialog>')
bonus = part('<div class="bonus-fab js-bonus-fab"', '\n  </div>')  # карточка «Вам доступна скидка 20%»
script = re.search(r'<script src="script\.js\?v=\d+"></script>', src).group(0)


def fix(html):
    """Пути лендинга → пути из папки прототипа."""
    html = re.sub(r'(src|href|srcset)="(assets/|favicon|styles\.css|script\.js|privacy\.html|consent\.html|send\.php)',
                  r'\1="../\2', html)
    html = html.replace('action="send.php"', 'action="../send.php"')
    html = html.replace('href="#top"', 'href="../"')
    html = html.replace('href="prototype-catalog/', 'href="')  # ссылки лендинга на каталог — изнутри папки каталога
    html = re.sub(r'href="#(?!")', 'href="../#', html)
    html = html.replace('href="../#footer"', 'href="#footer"')  # «Контакты» в шапке — к подвалу этой же страницы
    return html


_SLASH_RE = re.compile(r'href="(/(?:catalog|magazines|gid|port|diz|blog|sert|st\d+)(?:/[^"#?]*?)?)(?<!/)(#[^"]*)?"')


def _slash(html):
    """внутренние ссылки на статичные страницы — со «/» на конце: сервер отдаёт папку …/index.html без переадресации.
    canonical (rel="canonical") остаётся без «/» — как адреса старого сайта."""
    return _SLASH_RE.sub(lambda m: 'href="%s/%s"' % (m.group(1), m.group(2) or ''), html)


def page(title, body_class, main, scripts=('catalog.js?v=61',)):
    h = fix(head)
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, h)
    # прототип каталога не индексируем до переноса на Astro (дубли steelline.store)
    h = re.sub(r'\s*<link rel="canonical"[^>]*>', '', h)
    h = re.sub(r'\s*<meta name="yandex-verification"[^>]*>', '', h)
    h = re.sub(r'\s*<meta property="og:[^>]*>', '', h)  # превью главной; у статичных страниц — свои
    h = h.replace('<meta name="viewport" content="width=device-width, initial-scale=1">',
                  '<meta name="viewport" content="width=device-width, initial-scale=1">\n  <meta name="robots" content="noindex, nofollow">', 1)
    h += '  <link rel="stylesheet" href="catalog.css?v=85">\n</head>\n'
    nav_header = fix(header)
    return _slash(h + '<body class="%s">\n\n  ' % body_class + nav_header + '\n\n' + main + '\n\n  ' + fix(cookie) +
            '\n\n  ' + fix(sticky).replace('href="../#contacts"', 'href="#"') + '\n\n  ' + fix(bonus) + '\n\n  ' + fix(callback) + '\n\n  ' + fix(footer) + '\n\n  ' +
            fix(lead) + '\n\n  ' + fix(script) + ''.join('\n  <script src="%s"></script>' % x for x in scripts) + '\n</body>\n</html>\n')


catalog_main = '''  <main class="cat" id="cat">
    <div class="cat__head wrap">
      <nav class="crumbs" aria-label="Хлебные крошки"><a href="../">Главная</a><span>/</span><a href="catalog.html">Каталог</a><span class="js-crumb-cat" hidden>/</span><span class="js-crumb-cat-name"></span></nav>
      <p class="cat__kicker js-cat-kicker" hidden></p>
      <h1 class="cat__title js-cat-title">Каталог входных дверей</h1>
      <p class="cat__lead js-cat-lead">Двери для дома и квартиры собственного производства «Стальной линии». Выберите раздел или настройте фильтры — а если сложно определиться, подберём дверь по&nbsp;фото проёма.</p>
    </div>

    <nav class="cat-kinds wrap js-kinds" aria-label="Вид дверей"></nav>
    <nav class="cat-tabs wrap js-tabs" aria-label="Разделы каталога"></nav>

    <section class="sale-banner wrap js-sale" hidden aria-label="Распродажа склада">
      <div class="sale-banner__inner">
        <div class="sale-banner__badge"><span>скидка на&nbsp;полотна</span><b>−40%</b></div>
        <div class="sale-banner__text">
          <p class="sale-banner__kicker">Aurum doors</p>
          <h2 class="sale-banner__title">Распродажа склада в&nbsp;Екатеринбурге</h2>
          <p class="sale-banner__lead">Скидка 40% на&nbsp;полотна коллекции Кобальт. 400 полотен в&nbsp;наличии — забрать можно сразу.</p>
          <a class="btn sale-banner__btn" href="/catalog/mezhkom/kobalt">Смотреть двери Кобальт <img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt=""></a>
        </div>
        <div class="sale-banner__doors js-sale-doors" aria-hidden="true"></div>
      </div>
      <!-- на телефоне вместо баннера — готовая картинка распродажи -->
      <a class="sale-banner__photo" href="/catalog/mezhkom/kobalt">
        <picture>
          <source media="(max-width: 767px)" srcset="img/aurum/sale-mobile.webp">
          <img src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" width="1200" height="800" fetchpriority="high" alt="Распродажа склада межкомнатных дверей Aurum Doors: скидка 40%. Екатеринбург, ИЦ Аструм, 6 уровень, галерея А">
        </picture>
      </a>
    </section>

    <div class="cat__body wrap">
      <aside class="cat-filters js-filters" aria-label="Фильтры">
        <div class="cat-filters__head">
          <span class="cat-filters__title">Фильтры</span>
          <button class="cat-filters__reset js-reset" type="button">Сбросить</button>
          <button class="cat-filters__close js-filters-close" type="button" aria-label="Закрыть фильтры"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
        </div>
        <div class="js-filter-groups"></div>
        <button class="btn btn--gradient btn--lg cat-filters__apply js-filters-close" type="button">Показать модели</button>
      </aside>

      <section class="cat__list">
        <div class="cat-toolbar">
          <p class="cat-toolbar__count js-count"></p>
          <button class="btn btn--outline cat-toolbar__filters js-filters-open" type="button"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 7h10M18 7h2M4 17h4M12 17h8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="16" cy="7" r="2" stroke="currentColor" stroke-width="1.6"/><circle cx="10" cy="17" r="2" stroke="currentColor" stroke-width="1.6"/></svg>Фильтры<span class="cat-toolbar__badge js-active-count" hidden></span></button>
          <label class="cat-sort"><span class="cat-sort__label">Сортировка</span>
            <select class="cat-sort__select js-sort">
              <option value="popular">Сначала популярные</option>
              <option value="price-asc">Сначала дешевле</option>
              <option value="price-desc">Сначала дороже</option>
              <option value="name">По названию</option>
            </select>
          </label>
        </div>
        <div class="cat-grid js-grid"></div>
        <div class="cat-empty js-empty" hidden>
          <p class="cat-empty__title">Таких моделей не нашлось</p>
          <p class="cat-empty__text">Попробуйте убрать часть фильтров — или пришлите фото проёма, и мы подберём дверь сами.</p>
          <div class="cat-empty__actions">
            <button class="btn btn--outline btn--lg js-reset" type="button">Сбросить фильтры</button>
            <a class="btn btn--gradient btn--lg" href="#" data-open-form="catalog-empty">Подобрать дверь</a>
          </div>
        </div>
        <button class="btn btn--outline btn--lg cat-more js-more" type="button" hidden>Показать ещё</button>
      </section>
    </div>

    <section class="cat-cta wrap">
      <div class="cat-cta__text">
        <h2 class="cat-cta__title">Не нашли подходящую модель?</h2>
        <p class="cat-cta__lead">Пришлите фото проёма — подберём дверь под ваш дом, стиль и&nbsp;бюджет. Бесплатно.</p>
      </div>
      <a class="btn btn--gradient btn--lg" href="#" data-open-form="catalog-cta">Получить подбор двери <img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt=""></a>
    </section>
  </main>'''

model_main = '''  <main class="model-page" id="model">
    <div class="wrap">
      <nav class="crumbs js-crumbs" aria-label="Хлебные крошки"></nav>
    </div>

    <article class="model wrap">
      <div class="model__gallery">
        <button class="model__photo js-photo" type="button" aria-label="Открыть фото крупно"><img class="js-photo-img" alt=""></button>
        <div class="model__thumbs js-thumbs"></div>
      </div>

      <div class="model__info">
        <div class="model__tags js-tags"></div>
        <p class="model__kicker js-kicker" hidden></p>
        <h1 class="model__title js-title"></h1>
        <p class="model__price"><span class="js-price"></span></p>
        <p class="model__kit js-kit" hidden></p>
        <p class="model__note js-note">Цена — за дверь в базовой комплектации. Итог зависит от размера, отделки и фурнитуры.</p>

        <div class="model__colors js-colors-wrap" hidden>
          <p class="model__label">Цвет: <b class="js-color-name"></b></p>
          <div class="model__swatches js-colors" role="radiogroup" aria-label="Цвет двери"></div>
        </div>

        <div class="model__series js-series-wrap" hidden>
          <p class="model__label">Серия</p>
          <div class="model__series-list js-series"></div>
        </div>

        <dl class="model__params js-params"></dl>

        <div class="model__actions">
          <a class="btn btn--gradient btn--lg" href="#" data-open-form="model">Получить подбор двери <img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt=""></a>
          <a class="btn btn--outline btn--lg" href="#" data-open-form="contact">Записаться на подбор</a>
        </div>

        <ul class="model__perks js-perks">
          <li><b>30 лет</b> производства</li>
          <li><b>2 года</b> гарантии на дверь и монтаж</li>
          <li><b>Хранение</b> двери на складе до установки</li>
        </ul>

        <p class="model__salon">Посмотреть вживую — в салоне ИЦ ASTROOM, ул.&nbsp;Цвиллинга,&nbsp;1, 6&nbsp;этаж · <a href="tel:+79222077552">+7&nbsp;(922)&nbsp;207-75-52</a></p>
      </div>
    </article>

    <section class="model-specs wrap">
      <h2 class="model-specs__title">Характеристики</h2>
      <div class="js-specs"></div>
    </section>

    <section class="model-molding wrap js-molding-wrap" hidden>
      <h2 class="model-specs__title">Погонаж</h2>
      <p class="model-molding__lead">Коробка, наличники и доборы — в цвет полотна.</p>
      <div class="js-molding"></div>
    </section>

    <section class="model-similar wrap">
      <div class="model-similar__head">
        <h2 class="model-similar__title">Похожие модели</h2>
        <a class="btn btn--outline js-similar-all" href="catalog.html">Все модели раздела</a>
      </div>
      <!-- лента: листается пальцем, мышью (data-drag в script.js) и стрелками по краям — появляются при наведении -->
      <div class="similar-wrap">
        <button class="similar-arrow js-similar-prev" type="button" aria-label="Предыдущие модели"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        <div class="similar-track scroller js-similar" data-drag></div>
        <button class="similar-arrow similar-arrow--next js-similar-next" type="button" aria-label="Следующие модели"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      </div>
    </section>

    <dialog class="photo-view js-photo-view" aria-label="Фото двери">
      <button class="photo-view__close js-photo-close" type="button" aria-label="Закрыть"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
      <img class="photo-view__img js-photo-view-img" alt="">
    </dialog>
  </main>'''

# Данные для страниц каталога: у межкомнатных — облегчённый список для карточек и фильтров (подробности — только на странице модели),
# плюс счётчики для переключателя «Входные / Межкомнатные», чтобы не загружать ради них второй файл
def _json(name):
    return json.load(open(os.path.join(OUT, 'data', name), encoding='utf-8'))
_aurum, _entry = _json('aurum.json'), _json('catalog.json')
# адреса страниц межкомнатных дверей: /catalog/mezhkom/<коллекция>/<модель>
for _p in _aurum['products']:
    _p['url'] = '/catalog/%s/%s' % (_p['cats'][0], _p['slug'])
json.dump(_aurum, open(os.path.join(OUT, 'data', 'aurum.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
_keep = ['id', 'kind', 'title', 'url', 'collection', 'collectionName', 'cats', 'price', 'priceKit', 'photos', 'colorNames',
         'style', 'window', 'inStock', 'sale', 'scene', 'colorNote']
_list = [dict({k: p[k] for k in _keep if k in p}, colors=[{'name': c['name'], 'swatch': c['swatch']} for c in p['colors']])
         for p in _aurum['products']]
json.dump({'categories': _aurum['categories'], 'products': _list}, open(os.path.join(OUT, 'data', 'aurum-list.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
json.dump({'entry': len(_entry['products']), 'interior': len(_aurum['products'])}, open(os.path.join(OUT, 'data', 'counts.json'), 'w', encoding='utf-8'))

open(os.path.join(OUT, 'catalog.html'), 'w', encoding='utf-8').write(page('Каталог входных дверей — Стальная линия', 'page-catalog', catalog_main))
open(os.path.join(OUT, 'model.html'), 'w', encoding='utf-8').write(page('Модель двери — Стальная линия', 'page-model', model_main))

portfolio_main = '''  <main class="port" id="port">
    <div class="wrap">
      <nav class="crumbs port-crumbs" aria-label="Хлебные крошки"><a href="../">Главная</a><span>/</span><span>Наши работы</span></nav>
      <div class="port-headline">
        <h1 class="cat__title port-title">Наши работы</h1>
        <ul class="port-badges js-port-badges"></ul>
      </div>
      <p class="cat__lead port-lead js-port-lead"></p>

      <div class="port-bar">
        <div class="port-tabs js-port-regions" role="group" aria-label="Город"></div>
        <div class="csel port-type">
          <select class="cat-sort__select js-port-type" aria-label="Вид двери"></select>
          <button type="button" class="csel__btn js-port-type-btn" aria-haspopup="listbox" aria-expanded="false" aria-controls="port-type-list"></button>
          <ul class="csel__list js-port-type-list" id="port-type-list" role="listbox" tabindex="-1" hidden></ul>
        </div>
      </div>
    </div>

    <section class="port__body wrap">
      <p class="cat-toolbar__count js-port-count"></p>
      <div class="port-grid js-port-grid"></div>
      <button class="btn btn--outline btn--lg cat-more js-port-more" type="button" hidden>Показать ещё</button>
    </section>

    <section class="cat-cta wrap">
      <div class="cat-cta__text">
        <h2 class="cat-cta__title">Хотите такую же дверь?</h2>
        <p class="cat-cta__lead">Пришлите фото проёма — подберём модель, рассчитаем стоимость и&nbsp;установим. Гарантия на&nbsp;монтаж 2&nbsp;года.</p>
      </div>
      <a class="btn btn--gradient btn--lg" href="#" data-open-form="portfolio-cta">Получить подбор двери <img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt=""></a>
    </section>

    <dialog class="port-view js-port-view" aria-label="Проект">
      <button class="port-view__close js-pv-close" type="button" aria-label="Закрыть"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
      <button class="port-view__nav port-view__nav--prev js-pv-prev" type="button" aria-label="Предыдущий проект"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      <button class="port-view__nav port-view__nav--next js-pv-next" type="button" aria-label="Следующий проект"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9 5l7 7-7 7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      <div class="port-view__media"><img class="port-view__img js-pv-img" alt=""></div>
      <div class="port-view__side">
        <span class="tag tag--blue port-view__city js-pv-city"></span>
        <h2 class="port-view__title js-pv-title"></h2>
        <div class="port-view__thumbs js-pv-thumbs"></div>
        <div class="port-view__actions">
          <a class="btn btn--gradient btn--lg" href="#" data-open-form="portfolio">Хочу такую дверь</a>
          <a class="btn btn--outline btn--lg js-pv-model" href="#" hidden>Модель в каталоге</a>
        </div>
        <p class="port-view__count js-pv-count"></p>
      </div>
    </dialog>
  </main>'''

open(os.path.join(OUT, 'portfolio.html'), 'w', encoding='utf-8').write(page('Наши работы — Стальная линия', 'page-portfolio', portfolio_main, ('portfolio.js?v=14',)))

print('ok')

stores_main = '''  <main class="port shops" id="shops">
    <div class="wrap">
      <nav class="crumbs port-crumbs" aria-label="Хлебные крошки"><a href="../">Главная</a><span>/</span><span>Наши магазины</span></nav>
      <div class="port-headline">
        <h1 class="cat__title port-title">Наши магазины</h1>
        <ul class="port-badges js-shops-badges"></ul>
      </div>
      <p class="cat__lead port-lead">Приходите посмотреть двери вживую: образцы отделок, фурнитура и&nbsp;замки. Главный салон в&nbsp;Екатеринбурге&nbsp;— в&nbsp;интерьерном центре ASTROOM.</p>

      <div class="port-bar">
        <div class="port-tabs js-shops-regions" role="group" aria-label="Регион"></div>
      </div>
    </div>

    <section class="shops__body wrap">
      <div class="shops-list js-shops-list"></div>
    </section>

    <section class="cat-cta wrap">
      <div class="cat-cta__text">
        <h2 class="cat-cta__title">Нет салона в&nbsp;вашем городе?</h2>
        <p class="cat-cta__lead">Пришлите фото проёма&nbsp;— подберём дверь дистанционно, рассчитаем стоимость и&nbsp;расскажем, как заказать в&nbsp;вашем городе.</p>
      </div>
      <a class="btn btn--gradient btn--lg" href="#" data-open-form="stores-cta">Получить подбор двери <img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt=""></a>
    </section>

    <dialog class="shop-view js-shop-view" aria-label="Фото салона">
      <button class="port-view__close js-sv-close" type="button" aria-label="Закрыть"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
      <button class="port-view__nav port-view__nav--prev js-sv-prev" type="button" aria-label="Предыдущее фото"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      <button class="port-view__nav shop-view__next js-sv-next" type="button" aria-label="Следующее фото"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9 5l7 7-7 7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      <img class="shop-view__img js-sv-img" alt="">
      <p class="shop-view__cap js-sv-cap"></p>
    </dialog>
  </main>'''

open(os.path.join(OUT, 'stores.html'), 'w', encoding='utf-8').write(page('Наши магазины — Стальная линия', 'page-portfolio page-stores', stores_main, ('stores.js?v=13',)))


# ---------- Адреса страниц моделей (статичные страницы — в конце файла) ----------
from urllib.parse import urlparse


def _translit(s):
    t = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c',
         'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'}
    return re.sub(r'[^a-z0-9]+', '-', ''.join(t.get(c, c) for c in s.lower())).strip('-')


# адреса моделей: путь со старого сайта; опечатка «caralog» исправлена; если адрес у двух моделей совпал
# (ошибка старого сайта) — вторая получает свой адрес по названию
# у «Мадрида» на старом сайте в данных ошибочно стоит адрес «Бремена»; настоящий адрес найден в карте старого сайта
_URL_FIX = {'605064485219': '/catalog/dom/nestandart/madriddvup'}
_seen = set()
for _p in _entry['products']:
    path = _URL_FIX.get(_p['id']) or urlparse(_p['oldUrl']).path.rstrip('/').replace('/caralog/', '/catalog/')
    if path in _seen:
        path = path.rsplit('/', 1)[0] + '/' + _translit(_p['title'])
        while path in _seen:
            path += '-2'
    _seen.add(path)
    _p['url'] = path
json.dump(_entry, open(os.path.join(OUT, 'data', 'catalog.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
_url_by_id = {p['id']: p['url'] for p in _entry['products']}


def _model_href(pid):
    return _url_by_id.get(pid, 'model.html?id=' + pid)


# в портфолио — ссылка «Модель в каталоге» на страницу модели
_port = _json('portfolio.json')
for _pr in _port.get('projects', []):
    if _pr.get('model') and _pr['model'].get('id') in _url_by_id:
        _pr['model']['url'] = _url_by_id[_pr['model']['id']]
json.dump(_port, open(os.path.join(OUT, 'data', 'portfolio.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))


# ---------- Гид по продукту (перенос steelline.store/gid) ----------
# Ролики и обложки — те же, что в окне «Видеообзоры» на главной; видео о фабрике и технологии — data/gid.json (catalog-source/gid.py)
import html as _html
_gid = _json('gid.json')
_ids = {p['title']: p['id'] for p in _entry['products'] if p.get('cats') and p['cats'][0].startswith('dom/')}  # заменяются на адреса страниц ниже
player = part('<dialog class="player" id="player"', '</dialog>')


def _reels(group_title):
    i = src.index('<h3 class="reels__group-title">%s</h3>' % group_title.replace(' ', '\xa0'))
    j = src.index('</section>', i)
    cards = re.findall(r'<article class="video-card">.*?</article>', src[i:j], re.S)
    out = []
    for c in cards:
        c = c.replace('<h4 class="video-card__title">', '<h3 class="video-card__title">').replace('</h4>', '</h3>')
        m = re.search(r'«([^»]+)»', c)
        # «Модель в каталоге» — для обзоров моделей; второй ролик «Сага» на старом сайте подписан так же, ссылку даём обоим
        if m and m.group(1) in _ids:
            c = c.replace('</article>', '  <a class="gid-reel__link" href="%s">Модель в каталоге</a>\n          </article>' % _model_href(_ids[m.group(1)]))
        out.append(c)
    # пути лендинга → из папки прототипа (у роликов ещё и data-video)
    return fix('\n          '.join(out)).replace('data-video="assets/', 'data-video="../assets/')


def _dur(sec):
    return '%d:%02d' % (sec // 60, sec % 60)


def _rt(v, big=False):
    return ('<article class="rt-card%s">' % (' rt-card--big' if big else '') +
            '<button type="button" class="rt-card__media" data-rutube="%s" aria-label="Смотреть видео: %s">' % (v['id'], _html.escape(v['title'])) +
            '<img src="%s" alt="" loading="lazy" decoding="async">' % v['poster'] +
            '<span class="rt-card__play" aria-hidden="true"><svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5.5v13l11-6.5-11-6.5Z"/></svg></span>' +
            '<span class="video-card__badge rt-card__dur">%s</span></button>' % _dur(v['duration']) +
            '<h3 class="rt-card__title">%s</h3></article>' % _html.escape(v['title']))


def _tech_card(t, i):
    return ('<button type="button" class="tech-card" data-tech="%d">' % i +
            '<span class="tech-card__media"><img src="%s" alt="" width="400" height="300" loading="lazy" decoding="async"></span>' % t['img'] +
            '<span class="tech-card__title">%s</span>' % _html.escape(t['title']) +
            '<span class="tech-card__lead">%s</span></button>' % _html.escape(t['lead']))


_v = _gid['videos']
gid_main = '''  <main class="port gid" id="gid">
    <div class="wrap">
      <nav class="crumbs port-crumbs" aria-label="Хлебные крошки"><a href="../">Главная</a><span>/</span><a href="catalog.html">Каталог</a><span>/</span><span>Гид по продукту</span></nav>
      <h1 class="cat__title port-title gid-title">Гид по продукту</h1>
      <p class="cat__lead port-lead">Всё, что стоит знать перед выбором двери: обзоры моделей, ответы на частые вопросы и&nbsp;технологии фабрики.</p>
      <nav class="gid-nav" aria-label="Разделы гида">
        <a class="cat-tab" href="#factory">О фабрике</a>
        <a class="cat-tab" href="#models">Обзоры моделей</a>
        <a class="cat-tab" href="#faq">Вопросы и ответы</a>
        <a class="cat-tab" href="#tech">Технологии и отделка</a>
      </nav>
    </div>

    <section class="gid-sec wrap" id="factory" aria-labelledby="factory-title">
      <h2 class="gid-sec__title" id="factory-title">О фабрике</h2>
      <div class="gid-factory">
        ''' + _rt(_v[0], True) + '''
        <div class="gid-factory__side">
          ''' + '\n          '.join(_rt(v) for v in _v[1:]) + '''
        </div>
      </div>
    </section>

    <section class="gid-sec wrap" id="models" aria-labelledby="models-title">
      <div class="gid-sec__head">
        <h2 class="gid-sec__title" id="models-title">Обзоры моделей</h2>
        <p class="gid-sec__lead">Можно выбрать готовое решение из&nbsp;каталога или собрать своё: отделку, фрезеровку, цвет двери и&nbsp;коробки, фурнитуру и&nbsp;декор. Изготовим практически любой размер.</p>
      </div>
      <div class="similar-wrap gid-track-wrap">
        <button class="similar-arrow gid-arrow gid-arrow--prev" type="button" aria-label="Назад"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        <div class="gid-reels gid-reels--track" data-drag>
          ''' + _reels('Обзоры моделей') + '''
        </div>
        <button class="similar-arrow similar-arrow--next gid-arrow gid-arrow--next" type="button" aria-label="Дальше"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      </div>
    </section>

    <section class="gid-sec wrap" id="faq" aria-labelledby="faq-title">
      <div class="gid-sec__head">
        <h2 class="gid-sec__title" id="faq-title">Вопросы и ответы</h2>
        <p class="gid-sec__lead">Короткие ролики из&nbsp;салона: отвечаем на&nbsp;то, о&nbsp;чём спрашивают чаще всего.</p>
      </div>
      <div class="similar-wrap gid-track-wrap">
        <button class="similar-arrow gid-arrow gid-arrow--prev" type="button" aria-label="Назад"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
        <div class="gid-reels gid-reels--track" data-drag>
          ''' + _reels('Полезная информация') + '''
        </div>
        <button class="similar-arrow similar-arrow--next gid-arrow gid-arrow--next" type="button" aria-label="Дальше"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
      </div>
    </section>

    <section class="gid-sec wrap" id="tech" aria-labelledby="tech-title">
      <div class="gid-sec__head">
        <h2 class="gid-sec__title" id="tech-title">Технологии и&nbsp;отделка</h2>
        <p class="gid-sec__lead">Фирменные покрытия, панели из&nbsp;дерева, окна, витражи и&nbsp;индивидуальные решения фабрики «Стальная линия».</p>
      </div>
      <div class="tech-grid">
        ''' + '\n        '.join(_tech_card(t, i) for i, t in enumerate(_gid['tech'])) + '''
        <a class="tech-card tech-card--cta" href="#" data-open-form="gid-tech">
          <span class="tech-card__title">Не нашли нужное?</span>
          <span class="tech-card__lead">Расскажите, какую дверь хотите&nbsp;— подберём отделку и&nbsp;рассчитаем стоимость.</span>
          <span class="tech-card__go">Записаться на подбор <img src="../assets/icons/arrow-right-white-2.svg" width="20" height="20" alt=""></span>
        </a>
      </div>
    </section>

    <section class="cat-cta wrap">
      <div class="cat-cta__text">
        <h2 class="cat-cta__title">Не знаете, что выбрать?</h2>
        <p class="cat-cta__lead">Пришлите фото проёма&nbsp;— подберём модель и&nbsp;отделку, рассчитаем стоимость и&nbsp;установим. Гарантия на&nbsp;монтаж 2&nbsp;года.</p>
      </div>
      <a class="btn btn--gradient btn--lg" href="#" data-open-form="gid-cta">Записаться на подбор <img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt=""></a>
    </section>

    <dialog class="tech-view js-tech-view" aria-labelledby="tech-view-title">
      <button class="port-view__close js-tv-close" type="button" aria-label="Закрыть"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
      <div class="tech-view__media"><img class="js-tv-img" alt=""></div>
      <div class="tech-view__body">
        <h2 class="tech-view__title js-tv-title" id="tech-view-title"></h2>
        <p class="tech-view__lead js-tv-lead"></p>
        <dl class="tech-view__points js-tv-points"></dl>
        <div class="tech-view__nav">
          <button type="button" class="btn btn--outline js-tv-prev">Назад</button>
          <button type="button" class="btn btn--outline js-tv-next">Дальше</button>
        </div>
      </div>
    </dialog>
    <script type="application/json" id="tech-data">''' + json.dumps(_gid['tech'], ensure_ascii=False).replace('</', '<\\/') + '''</script>
  </main>

  ''' + fix(player)

open(os.path.join(OUT, 'gid.html'), 'w', encoding='utf-8').write(page('Гид по продукту — Стальная линия', 'page-portfolio page-gid', gid_main, ('gid.js?v=2',)))


# ---------- Дизайнерам и архитекторам (перенос steelline.store/diz) ----------
# На старом сайте всё — слайды презентации EXCLUSIVE; текст перенесён сюда, фото вырезаны из слайдов (catalog-source/designers.py)
_e = _html.escape


def _scheme(leaves, left=False, right=False, top=False):
    """Схема проёма: полотна (белые, с ручкой), боковые доборы и фрамуга (тёмные). SVG 120×150."""
    W, H, s, f = 120, 150, 20, 20
    x0, x1, y0 = (s if left else 0), (W - s if right else W), (f if top else 0)
    out = ['<svg viewBox="-2 -2 124 154" width="120" height="150" aria-hidden="true">']
    out.append('<rect x="0" y="0" width="%d" height="%d" fill="none" stroke="currentColor" stroke-width="2"/>' % (W, H))
    if top:
        out.append('<rect x="0" y="0" width="%d" height="%d" class="sch-fill"/>' % (W, f))
    if left:
        out.append('<rect x="0" y="%d" width="%d" height="%d" class="sch-fill"/>' % (y0, s, H - y0))
    if right:
        out.append('<rect x="%d" y="%d" width="%d" height="%d" class="sch-fill"/>' % (W - s, y0, s, H - y0))
    lw = (x1 - x0) / leaves
    for i in range(leaves):
        lx = x0 + i * lw
        out.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" fill="none" stroke="currentColor" stroke-width="1.5"/>' % (lx + 3, y0 + 3, lw - 6, H - y0 - 3))
        hx = lx + lw - 10 if (leaves == 1 or i == 0) else lx + 10
        if leaves == 2:
            hx = lx + lw - 9 if i == 0 else lx + 9
        hy = y0 + (H - y0) * 0.5
        out.append('<path d="M%.1f %.1fv12" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>' % (hx, hy - 6))
    out.append('</svg>')
    return ''.join(out)


_S1 = [('Однопольная', '1П', dict(), 'max высота 2380 мм, ширина 1080 мм (серия 100)'),
       ('С правым боковым добором', '1П+ПД', dict(right=True), 'Серии 60, 60-ВН, 70, 100'),
       ('С левым боковым добором', '1П+ЛД', dict(left=True), 'Серии 60, 60-ВН, 70, 100, 100-ВН'),
       ('С двумя боковыми доборами', '1П+2Д', dict(left=True, right=True), 'Серии 100, 100-ВН'),
       ('С верхней фрамугой', '1П+Ф', dict(top=True), 'Серии 60, 60-ВН, 70, 100, 100-ВН'),
       ('С правым добором и фрамугой', '1П+ПД+Ф', dict(right=True, top=True), 'Серии 100, 100-ВН'),
       ('С левым добором и фрамугой', '1П+ЛД+Ф', dict(left=True, top=True), 'Серии 100, 100-ВН'),
       ('С двумя доборами и фрамугой', '1П+2Д+Ф', dict(left=True, right=True, top=True), 'Серии 100, 100-ВН')]
_S2 = [('Двупольная', '2П', dict(), 'Серии 70, 80, 100, 100-ВН'),
       ('С левым боковым добором', '2П+ЛД', dict(left=True), 'Серии 100, 100-ВН'),
       ('С правым боковым добором', '2П+ПД', dict(right=True), 'Серии 100, 100-ВН'),
       ('С двумя боковыми доборами', '2П+2Д', dict(left=True, right=True), 'Серии 100, 100-ВН'),
       ('С верхней фрамугой', '2П+Ф', dict(top=True), 'Серии 100, 100-ВН'),
       ('С левым добором и фрамугой', '2П+ЛД+Ф', dict(left=True, top=True), 'Серии 100, 100-ВН'),
       ('С правым добором и фрамугой', '2П+ПД+Ф', dict(right=True, top=True), 'Серии 100, 100-ВН'),
       ('С двумя доборами и фрамугой', '2П+2Д+Ф', dict(left=True, right=True, top=True), 'Серии 100, 100-ВН')]


def _schemes(items, leaves):
    return ''.join('<li class="sch"><span class="sch__pic">%s</span><span class="sch__name">%s <b>%s</b></span><span class="sch__note">%s</span></li>'
                   % (_scheme(leaves, **kw), _e(n), _e(code), _e(note)) for n, code, kw, note in items)


def _fig(img, cap, cls=''):
    return '<figure class="dz-fig %s"><span class="dz-fig__media"><img src="img/diz/%s.webp?v=5" alt="" loading="lazy" decoding="async"></span><figcaption>%s</figcaption></figure>' % (cls, img, cap)


def _chips(prefix, names, patina=True):
    return '<ul class="dz-chips">' + ''.join(
        '<li><img src="img/diz/%s-%d.webp" alt="" loading="lazy" decoding="async"><span>%s</span></li>' % (prefix, i + 1, _e(n))
        for i, n in enumerate(names)) + '</ul>'


_ICON = {
    'profit': '<path d="M4 20h16"/><path d="M6 16v-3M10 16V9M14 16v-5M18 16V6"/><path d="M14 4h4v4"/>',
    'manager': '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/><path d="m12 15 1.5 3-1.5 3-1.5-3z"/>',
    'install': '<path d="M14 6a4 4 0 0 0-5 5l-6 6 2 2 6-6a4 4 0 0 0 5-5l-3 3-2-2z"/>',
    'drop': '<path d="M12 3s-6 7-6 11a6 6 0 0 0 12 0c0-4-6-11-6-11z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    'rings': '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5.5"/><circle cx="12" cy="12" r="2"/>',
}


def _icon(k):
    return '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % _ICON[k]


def _finish(key, title, text, door, extra, palette=''):
    return ('<article class="dz-finish" id="%s"><div class="dz-finish__media"><img src="img/diz/%s.webp" alt="" loading="lazy" decoding="async"></div>'
            '<div class="dz-finish__body"><p class="dz-kicker">SteelLak®</p><h3 class="dz-finish__title">%s</h3><p>%s</p>%s%s</div></article>'
            % (key, door, title, text, extra, palette))


def _panel(key, title, origin, text, door, prefix, names, note=''):
    return ('<article class="dz-panel" id="%s"><div class="dz-panel__door"><img src="img/diz/%s.webp" alt="" loading="lazy" decoding="async"></div>'
            '<div class="dz-panel__body"><h3 class="dz-panel__title">%s</h3><p class="dz-panel__origin">%s</p><p>%s</p>%s%s</div></article>'
            % (key, door, title, origin, text, _chips(prefix, names), note))


designers_main = '''  <main class="dz" id="designers">
    <section class="dz-hero wrap">
      <div class="dz-hero__text">
        <nav class="crumbs" aria-label="Хлебные крошки"><a href="../">Главная</a><span>/</span><span>Дизайнерам и&nbsp;архитекторам</span></nav>
        <p class="dz-kicker">Exclusive · для профессионалов</p>
        <h1 class="dz-hero__title">Дизайнерам и&nbsp;архитекторам</h1>
        <p class="dz-hero__lead">Любой проект&nbsp;— это история с&nbsp;индивидуальными желаниями и&nbsp;особенностями. Мы вдохновляемся концепциями дизайнеров и&nbsp;архитекторов и&nbsp;воплощаем самые смелые идеи: двери любого размера, цвета и&nbsp;отделки для проектов любого уровня.</p>
        <p class="dz-hero__who">Приглашаем к&nbsp;сотрудничеству дизайнеров, архитекторов, застройщиков и&nbsp;строительно-ремонтные организации.</p>
        <div class="dz-hero__actions">
          <a class="btn btn--gradient btn--lg" href="#" data-open-form="designers">Стать партнёром <img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt=""></a>
          <a class="btn btn--outline btn--outline-soft btn--lg" href="#size">Возможности фабрики</a>
        </div>
      </div>
      <div class="dz-hero__media"><img src="img/diz/hero-wood.webp" alt="Входная дверь «Стальная линия» с отделкой под дерево и фрезеровкой в светлой прихожей" fetchpriority="high"></div>
    </section>

    <section class="dz-sec wrap" aria-labelledby="dz-terms">
      <h2 class="dz-title" id="dz-terms">Условия сотрудничества</h2>
      <div class="dz-terms">
        <article class="dz-term"><span class="dz-term__icon">''' + _icon('profit') + '''</span><h3>Повышенный коэффициент прибыли</h3><p>Выстраиваем индивидуальные условия с&nbsp;каждым специалистом и&nbsp;повышаем процент от&nbsp;сделок для лояльных партнёров.</p></article>
        <article class="dz-term"><span class="dz-term__icon">''' + _icon('manager') + '''</span><h3>Персональное сопровождение</h3><p>Отдел по&nbsp;работе с&nbsp;дизайнерами ведёт заказ от&nbsp;заявки и&nbsp;подбора дверей до&nbsp;сдачи на&nbsp;объекте, включая логистику и&nbsp;подъём на&nbsp;этаж.</p></article>
        <article class="dz-term"><span class="dz-term__icon">''' + _icon('install') + '''</span><h3>Аккредитованные монтажники</h3><p>Устанавливают специалисты с&nbsp;большим стажем, на&nbsp;их&nbsp;работу&nbsp;— юридически закреплённая гарантия.</p></article>
      </div>
    </section>

    <section class="dz-sec wrap" aria-labelledby="dz-facts">
      <h2 class="dz-title" id="dz-facts">«Стальная линия» в&nbsp;цифрах</h2>
      <ul class="dz-stats">
        <li><b>30</b><span>лет производим входные двери: от&nbsp;простых конструктивов до&nbsp;нестандартных моделей</span></li>
        <li><b>30&nbsp;000 м²</b><span>площадь производства, мощность&nbsp;— свыше 54&nbsp;000 дверей в&nbsp;год</span></li>
        <li><b>20</b><span>стран, где представлена продукция: от&nbsp;Крайнего Севера России до&nbsp;США</span></li>
        <li><b>350+</b><span>точек продаж</span></li>
        <li><b>3&nbsp;млн+</b><span>вариантов дверей</span></li>
        <li><b>25</b><span>конструктивов дверей</span></li>
        <li><b>2&nbsp;000+</b><span>цветов и&nbsp;вариантов отделки</span></li>
        <li><b>251</b><span>фрезеровка</span></li>
      </ul>
      <div class="dz-awards">
        <div class="dz-awards__list">
          <h3 class="dz-sub">Награды</h3>
          <ul>
            <li><b>Производитель №1 входных дверей в&nbsp;Беларуси*</b><span>2017, 2019, 2020, 2021</span></li>
            <li><b>«Лучшие товары Беларуси»**</b><span>2015–2021</span></li>
            <li><b>«Лучший строительный продукт года»</b><span>2014</span></li>
          </ul>
          <p class="dz-note">* по&nbsp;уведомлению о&nbsp;победе бренда «Стальная линия» в&nbsp;номинации «Белорусский производитель входных металлических дверей» конкурса «Выбор года».<br>** по&nbsp;результатам конкурса «Лучшие товары Республики Беларусь» в&nbsp;номинации «Промышленные товары».</p>
        </div>
        <div class="dz-awards__media"><img src="img/diz/awards.webp" alt="Вручение премии «Выбор года» бренду «Стальная линия»" loading="lazy" decoding="async"></div>
      </div>
    </section>

    <section class="dz-sec wrap" id="size" aria-labelledby="dz-size">
      <div class="dz-head">
        <div><p class="dz-kicker">Более 7&nbsp;000 размеров</p><h2 class="dz-title" id="dz-size">Двери любого размера</h2></div>
        <p class="dz-head__lead">Обустроим проём любой входной группы от&nbsp;800×1800 до&nbsp;3000×3500&nbsp;мм. Боковые доборы, верхние фрамуги и&nbsp;двупольные двери позволяют вписать дверь в&nbsp;проём практически любой ширины и&nbsp;высоты. Создавайте своё решение&nbsp;— мы&nbsp;воплотим его.</p>
      </div>
      <div class="dz-figs dz-figs--3 dz-figs--photo">
        ''' + _fig('size-1', '<b>С боковым и верхним добором.</b> 1380×2460 мм, фрезеровка КЛ-4, Oak Panel «Белый», патина золото') + '''
        ''' + _fig('size-2', '<b>С верхним и боковыми доборами.</b> 1760×2500 мм, фрезеровка заказчика, SteelLak® NCS S 1020-R60B, структурный') + '''
        ''' + _fig('size-3', '<b>Двупольная с фрамугой.</b> 1580×2900 мм, фрезеровка заказчика, Bjork Panel «Либерика», патина чёрная') + '''
      </div>
      <div class="dz-schemes">
        <div class="dz-schemes__head">
          <h3 class="dz-sub">Варианты для нестандартных проёмов</h3>
          <div class="dz-switch" role="tablist" aria-label="Тип двери">
            <button type="button" class="cat-tab is-active" role="tab" aria-selected="true" data-sch="1">Однопольные <span>от 800×1800</span></button>
            <button type="button" class="cat-tab" role="tab" aria-selected="false" data-sch="2">Двупольные <span>до 3000×3500</span></button>
          </div>
        </div>
        <ul class="dz-sch-list" data-sch-list="1">''' + _schemes(_S1, 1) + '''</ul>
        <ul class="dz-sch-list" data-sch-list="2" hidden>''' + _schemes(_S2, 2) + '''</ul>
        <p class="dz-note">Тёмным показаны боковые доборы и&nbsp;верхняя фрамуга. Максимальные размеры однопольной двери указаны для серии 100, у&nbsp;других серий они отличаются.</p>
      </div>
    </section>

    <section class="dz-sec wrap" aria-labelledby="dz-false">
      <div class="dz-split">
        <div class="dz-split__text">
          <h2 class="dz-title" id="dz-false">Фальш-панели</h2>
          <p class="dz-text">Стандартный проём, но&nbsp;хочется необычного решения или нужно поддержать стилистику интерьера? Фальш-панели могут быть практически любых размеров*: входная группа становится частью интерьера без дополнительных строительных работ.</p>
          <div class="dz-figs dz-figs--2">
            ''' + _fig('false-1', 'Фальш-панели 1335×2670 мм, полотно 960×2060 мм. Фрезеровка CV2.01, SteelLak® «Нефрит» RAL 6036, гладкий с эффектом металлик, вставка&nbsp;— чёрный молдинг') + '''
            ''' + _fig('false-2', 'Фальш-панели 1540×2445 мм, полотно 950×2050 мм. Фрезеровка CL1.04, SteelLak® «Антрацит» RAL 7016, гладкий') + '''
          </div>
          <p class="dz-note">* по&nbsp;согласованию с&nbsp;производственно-техническим отделом</p>
        </div>
        <div class="dz-split__media"><img src="img/diz/false-room.webp?v=2" alt="Дверь с фальш-панелями под дерево в шоуруме" loading="lazy" decoding="async"></div>
      </div>
    </section>

    <section class="dz-sec wrap" id="color" aria-labelledby="dz-color">
      <div class="dz-head">
        <div><p class="dz-kicker">Более 2&nbsp;000 цветовых решений</p><h2 class="dz-title" id="dz-color">Двери любого цвета</h2></div>
        <p class="dz-head__lead">Цвет первым формирует образ пространства, поэтому мы&nbsp;точно воспроизводим выбранные решения: любой цвет из&nbsp;палитр RAL Classic и&nbsp;NCS. Фирменная технология окраски SteelLak® делает покрытие прочным, защищает от&nbsp;стирания и&nbsp;царапин&nbsp;— дверь сохраняет вид весь срок службы.</p>
      </div>
      <div class="dz-figs dz-figs--4">
        ''' + _fig('color-1', 'Внутреннее открывание, 1380×2060 мм, фрезеровка Н-76, SteelLak® Brilliant «Рубиновый»') + '''
        ''' + _fig('color-2', '1010×2080 мм, SteelLak® RAL 4006, гладкий, фрезеровка П-36') + '''
        ''' + _fig('color-3', '1020×2140 мм, SteelLak® RAL 6036, гладкий, фрезеровка КЛ-2') + '''
        ''' + _fig('color-4', '860×2050 мм, фрезеровка CFД-18, SteelLak® «Небесно-голубой» NCS S 3030-R90B, структурный') + '''
      </div>
      <h3 class="dz-sub dz-sub--gap">Авторские покрытия, которым нет аналогов на&nbsp;рынке</h3>
      <div class="dz-finishes">
        ''' + _finish('brilliant', 'Brilliant', 'Металлическая блёстка создаёт эффект звёздного неба и&nbsp;выгодно подчёркивает порталы, наличники и&nbsp;витражи. Дверь становится акцентом интерьера.', 'brilliant',
                      '<ul class="dz-swatches"><li><img src="img/diz/brilliant-ruby.webp" alt="" loading="lazy"><span>«Рубиновый»</span></li><li><img src="img/diz/brilliant-violet.webp" alt="" loading="lazy"><span>«Фиолетовый»</span></li></ul>') + '''
        ''' + _finish('pearl', 'Перламутр', 'Глубокие переливы цвета: благодаря 3D-эффекту фактура играет на&nbsp;свету и&nbsp;дополняет современный интерьер. Цвета&nbsp;— «Чёрный оникс» и&nbsp;«Изумруд».', 'pearl',
                      '<div class="dz-macro"><img src="img/diz/pearl-macro.webp" alt="" loading="lazy"></div>') + '''
        ''' + _finish('chameleon', 'Хамелеон', 'Голографический эффект: оттенок двери меняется в&nbsp;зависимости от&nbsp;освещения.', 'chameleon',
                      '<ul class="dz-swatches dz-swatches--6">' + ''.join('<li><img src="img/diz/ch-%d.webp" alt="" loading="lazy"><span>%s</span></li>' % (i + 1, n) for i, n in enumerate(['«Жемчужно-розовый»', '«Жемчужно-голубой»', '«Розовый»', '«Голубой»', '«Фиолетовый»', '«Фиолетовый металлик»'])) + '</ul>') + '''
        ''' + _finish('metallic', 'Metallic', 'Наносится на&nbsp;любой цвет и&nbsp;покрывается лаком: поверхность переливается металлическими искрами в&nbsp;лучах солнца. В&nbsp;палитре 20 базовых цветов, но&nbsp;мерцающий эффект можно придать любому цвету RAL Classic и&nbsp;NCS.', 'metallic',
                      '<div class="dz-macro"><img src="img/diz/metallic-macro.webp" alt="" loading="lazy"></div>') + '''
      </div>
    </section>

    <section class="dz-sec wrap" id="wood" aria-labelledby="dz-wood">
      <div class="dz-split dz-split--rev">
        <div class="dz-split__text">
          <h2 class="dz-title" id="dz-wood">Отделка из&nbsp;дерева</h2>
          <p class="dz-text">Натуральный материал даёт простор фантазии: каждый интерьер получает уникальную фактуру и&nbsp;гамму оттенков. У&nbsp;нас три отделки из&nbsp;дерева&nbsp;— Oak Panel, Bjork Panel и&nbsp;Concord Panel. Они различаются фактурой, палитрой и&nbsp;ценой, но&nbsp;в&nbsp;главном схожи:</p>
          <ul class="dz-benefits">
            <li><span class="dz-term__icon">''' + _icon('drop') + '''</span><div><b>Атмосферостойкость</b><p>Устойчивы к&nbsp;влаге и&nbsp;перепадам температур, защищены от&nbsp;выгорания специальными лаками.</p></div></li>
            <li><span class="dz-term__icon">''' + _icon('sun') + '''</span><div><b>Защита от&nbsp;выгорания</b><p>Колористы разработали окраску полупрозрачными красителями и&nbsp;плотными эмалями&nbsp;— отделка сохраняет яркость и&nbsp;глубину цвета.</p></div></li>
            <li><span class="dz-term__icon">''' + _icon('rings') + '''</span><div><b>Неповторимый рисунок</b><p>Верхний слой передаёт рисунок натурального дерева; тон&nbsp;— от&nbsp;спокойных древесных оттенков до&nbsp;акцентных.</p></div></li>
          </ul>
        </div>
        <div class="dz-split__media"><img src="img/diz/wood-house.webp" alt="Дверь с отделкой из дерева на фасаде дома" loading="lazy" decoding="async"></div>
      </div>
      <div class="dz-panels">
        ''' + _panel('oak', 'Oak Panel', 'Италия · шпон дуба на основе из африканского дерева сейба',
                     'Многослойная панель прошла испытания 360 часами под водой и&nbsp;доказала высокую атмосферостойкость. Для неё разработаны фрезеровки с&nbsp;багетными рамками из&nbsp;массива дуба&nbsp;— они придают двери аристократичный вид.',
                     'oak', 'oak', ['«Тёмный»', '«Мокка»', '«Коньячный»', '«Натуральный»', '«Слоновая кость»', '«Белый»', '«Серый»', '«Натуральный зелёный»', '«Ультрамарин»', 'Любой цвет RAL']) + '''
        ''' + _panel('concord', 'Concord Panel', 'Россия · многослойная панель с дубовым шпоном',
                     'В&nbsp;мельчайших деталях передаёт фактурный рисунок дуба.',
                     'concord', 'cc', ['«Янтарь»', '«Маджента»', '«Эбен»', '«Шабо»', '«Аметист»', '«Калабрия»', '«Терра»', '«Либерика»', '«Верде»', '«Браун»'],
                     '<p class="dz-note">Все цвета&nbsp;— с&nbsp;чёрной патиной.</p>') + '''
        ''' + _panel('bjork', 'Bjork Panel', 'Россия · многослойная панель с берёзовым шпоном',
                     'Гладкая поверхность и&nbsp;волнообразный, немного хаотичный рисунок дерева.',
                     'bjork', 'bj', ['«Изумруд»', '«Аметист»', '«Индиго»', '«Либерика»', '«Терра»', '«Калабрия»', '«Маджента»', '«Эбен»', '«Янтарь»', '«Шабо»'],
                     '<p class="dz-note">Все цвета&nbsp;— с&nbsp;чёрной патиной.</p>') + '''
      </div>
    </section>

    <section class="dz-cta wrap">
      <div class="dz-cta__media"><img src="img/diz/cta-green.webp" alt="Зелёная входная дверь «Стальная линия» с арочной фрезеровкой и стеклом в светлой прихожей" loading="lazy" decoding="async"></div>
      <div class="dz-cta__body">
        <h2 class="dz-title">Обсудим ваш проект</h2>
        <p class="dz-text">Расскажите о&nbsp;проекте&nbsp;— персональный менеджер подберёт решения, рассчитает стоимость и&nbsp;расскажет об&nbsp;условиях партнёрства. Образцы отделок можно посмотреть вживую в&nbsp;шоуруме в&nbsp;ИЦ ASTROOM.</p>
        <div class="dz-hero__actions">
          <a class="btn btn--gradient btn--lg" href="#" data-open-form="designers-cta">Стать партнёром <img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt=""></a>
          <a class="btn btn--outline btn--outline-soft btn--lg" href="/magazines">Адреса салонов</a>
        </div>
      </div>
    </section>
  </main>'''

# версия картинок: при перерезке/повышении резкости образцов браузер должен взять новые файлы
designers_main = re.sub(r'(img/diz/[a-z0-9-]+\.webp)"', r'\1?v=6"', designers_main)
open(os.path.join(OUT, 'designers.html'), 'w', encoding='utf-8').write(page('Дизайнерам и архитекторам — Стальная линия', 'page-designers', designers_main, ('designers.js?v=1',)))


# ================= Статичные страницы для поисковиков =================
# Каждая модель входной двери и каждый раздел — отдельная готовая HTML-страница по адресу старого сайта
# (steelline.store/catalog/dom/svarnie/agios → /catalog/dom/svarnie/agios/index.html), с заголовком, описанием,
# хлебными крошками, фото, ценой, характеристиками, похожими моделями и микроразметкой прямо в коде.
# Скрипт каталога на этих страницах работает как обычно (берёт модель/раздел из data-атрибута <body>).
# Ресурсы прототипа подключаются через <base href="/prototype-catalog/">.
# Переезд: SITE_URL=https://steelline.store INDEX=1 python3 build.py — снимает noindex и пишет sitemap.xml.
# сайт уже на основном домене: по умолчанию сборка для steelline.store с открытой индексацией
# (для тестовой копии: SITE_URL=https://promo.steelline.store INDEX=0 python3 build.py)
SITE_URL = os.environ.get('SITE_URL', 'https://steelline.store').rstrip('/')
INDEX = os.environ.get('INDEX', '1') == '1'
STATIC_ROOT = ROOT  # /catalog/... в корне сайта


def _rub(n):
    return '{:,}'.format(int(round(n))).replace(',', ' ') + ' ₽'


_cats = {c['slug']: c for c in _entry['categories']}
_PARENTS = {'dom': ('Двери в дом', 'Входные двери для частного дома и коттеджа: тёплые, с терморазрывом, для нестандартных проёмов и по спец цене.'),
            'kvartira': ('Двери в квартиру', 'Надёжные входные двери для квартиры: классика и современный дизайн, умные замки.')}
_SNOW = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2v20M4.2 6.5l15.6 11M4.2 17.5l15.6-11M9 3.5l3 2.5 3-2.5M9 20.5l3-2.5 3 2.5M3 10.2l3.6.8-1 3.6M21 13.8l-3.6-.8 1-3.6M3 13.8l3.6-.8-1-3.6M21 10.2l-3.6.8 1 3.6"/></svg>'


def _cat_url(slug=''):
    return '/catalog' + ('/' + slug if slug else '')


def _meta_line(p):
    bits = []
    if p.get('series'): bits.append('Серия ' + ' / '.join(p['series']))
    if p.get('style'): bits.append(p['style'][0])
    if p.get('coating'): bits.append(p['coating'][0])
    return ' · '.join(bits)


def _card(p):
    """Карточка модели — та же разметка, что строит catalog.js"""
    photos = ''.join('<img class="pcard__photo" src="%s" alt="%s" loading="lazy">' % (_e(src), '' if i else 'Входная дверь ' + _e(p['title']))
                     for i, src in enumerate(p['photos'][:2]))
    warm = ('<span class="pcard__warm pcard__warm--husky" title="Тёплая серия «Хаски»">' + _SNOW + 'Хаски</span>') if 'dom/husky' in p['cats'] else \
           ('<span class="pcard__warm" title="Дверь с терморазрывом — не промерзает">' + _SNOW + 'Терморазрыв</span>') if p.get('thermo') else ''
    return ('<a class="pcard" href="%s"><div class="pcard__media">%s%s%s'
            '<span class="pcard__go" aria-hidden="true"><img src="../assets/icons/idea2-circle-40.svg" width="40" height="40" alt=""><img class="corner" src="../assets/icons/idea2-corner-10.svg" width="10" height="10" alt=""></span>'
            '</div><div class="pcard__body"><h3 class="pcard__title">%s</h3><p class="pcard__meta">%s</p><p class="pcard__price">от %s</p></div></a>'
            % (p['url'], photos, '<span class="pcard__badge">Спецпредложение</span>' if p.get('special') else '', warm,
               _e(p['title']), _e(_meta_line(p)), _rub(p['price'])))


def _ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def _crumbs_ld(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE_URL + u} for i, (n, u) in enumerate(items)]}


def _static_page(path, title, desc, body_class, body_attrs, main, scripts, ld=(), image=''):
    """Готовая страница на основе шаблона прототипа: свой title/description/canonical/og, base на ресурсы прототипа"""
    html = page(title, body_class, main, scripts)
    url = SITE_URL + path
    head_extra = ('\n  <base href="/prototype-catalog/">'
                  '\n  <link rel="canonical" href="%s">'
                  '\n  <meta property="og:type" content="website">\n  <meta property="og:site_name" content="Стальная линия">'
                  '\n  <meta property="og:title" content="%s">\n  <meta property="og:description" content="%s">\n  <meta property="og:url" content="%s">'
                  % (url, _e(title), _e(desc), url))
    if image:
        head_extra += '\n  <meta property="og:image" content="%s">' % (SITE_URL + '/prototype-catalog/' + image)
    head_extra += ''.join('\n  ' + _ld(x) for x in ld)
    # base — сразу после <meta charset>, до любых относительных адресов
    html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + head_extra.split('\n  <link rel="canonical"')[0], 1)
    html = html.replace('</head>', '\n  <link rel="canonical"' + head_extra.split('\n  <link rel="canonical"', 1)[1] + '\n</head>', 1)
    html = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % _e(desc), html, count=1)
    if INDEX:
        html = html.replace('\n  <meta name="robots" content="noindex, nofollow">', '')
    html = html.replace('<body class="%s">' % body_class, '<body class="%s"%s>' % (body_class, body_attrs), 1)
    # якоря на этой же странице: из-за <base> «#footer» вёл бы в папку прототипа
    html = re.sub(r'href="#([^"]+)"', lambda m: 'href="%s/#%s"' % (path.rstrip('/'), m.group(1)), html)
    # все адреса страниц — со «/» на конце, как их отдаёт сервер (адрес без «/» он переадресует): ссылки, canonical, og:url, микроразметка
    html = _slash(html)
    html = re.sub(re.escape(SITE_URL) + r'(/(?:catalog|magazines|gid|port|diz|blog|sert|st\d+)[^"\s<]*?)(?<!/)(?=")', lambda m: SITE_URL + m.group(1) + '/', html)
    out = os.path.join(STATIC_ROOT, path.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w', encoding='utf-8').write(html)
    return path


_sitemap = []
# каталог статичных страниц собирается заново целиком — чтобы не оставались страницы удалённых моделей
import shutil
shutil.rmtree(os.path.join(STATIC_ROOT, 'catalog'), ignore_errors=True)

# ---- страницы моделей ----
for p in _entry['products']:
    cat = _cats.get(p['cats'][0])
    parent = p['cats'][0].split('/')[0]
    crumbs = [('Главная', '/'), ('Каталог', _cat_url())] + ([(cat['name'], _cat_url(cat['slug']))] if cat else []) + [(p['title'], p['url'])]
    crumbs_html = '<span>/</span>'.join('<a href="%s">%s</a>' % (u, _e(n)) for n, u in crumbs[:-1]) + '<span>/</span><span>%s</span>' % _e(p['title'])
    kind = 'в квартиру' if parent == 'kvartira' else 'в дом'
    feats = []
    if 'dom/husky' in p['cats']: feats.append('тёплая серия «Хаски»')
    elif p.get('thermo'): feats.append('с терморазрывом')
    if p.get('style'): feats.append({'Классика': 'классический стиль', 'Современный': 'современный дизайн', 'Неоклассика': 'неоклассика'}.get(p['style'][0], p['style'][0].lower()))
    if p.get('coating'): feats.append('отделка ' + p['coating'][0])
    if p.get('series'): feats.append('серия ' + ' / '.join(p['series']))
    title = 'Входная дверь %s %s — купить в Екатеринбурге, цена от %s | Стальная линия' % (kind, p['title'], _rub(p['price']).replace(' ', ' '))
    desc = ('Входная дверь «%s» %s фабрики «Стальная линия»: %s. Цена от %s. Изготовление и установка в Екатеринбурге, гарантия 2 года.'
            % (p['title'], kind, ', '.join(feats) or 'стальная дверь', _rub(p['price']).replace(' ', ' '))).replace(':, ', ': ')
    # содержимое — как после работы catalog.js
    tags = ('<span class="tag tag--blue">%s</span>' % _e(cat['name']) if cat else '') + ('<span class="tag tag--blue">Спецпредложение</span>' if p.get('special') else '')
    photo = p['photos'][0] if p['photos'] else ''
    thumbs = ''.join('<button class="model__thumb%s" type="button" aria-label="Фото %d"><img src="%s" alt=""></button>' % (' is-active' if i == 0 else '', i + 1, _e(s))
                     for i, s in enumerate(p['photos'])) if len(p['photos']) > 1 else ''
    rows = [('Внешняя панель', (p.get('panels') or {}).get('outer')), ('Внутренняя панель', (p.get('panels') or {}).get('inner')),
            ('Стиль', ', '.join(p.get('style', []))), ('Покрытие', ', '.join(p.get('coating', []))), ('Окно', ', '.join(p.get('window', []))),
            ('Серия', ' / '.join(p.get('series', [])))]
    params = ''.join('<dt>%s</dt><dd>%s</dd>' % (a, _e(b)) for a, b in rows if b)
    keys = [k for k in (p.get('specSeries') or []) if k in _entry.get('seriesSpecs', {})]
    own = {s['title']: s for s in p.get('specs', [])}
    base_rows = _entry['seriesSpecs'][keys[0]]['rows'] if keys else []
    spec_list = [own.pop(s['title'], s) for s in base_rows] + [s for s in p.get('specs', []) if s['title'] in own]
    specs = (('<p class="specs-note">Серия %s</p>' % keys[0] if keys else '') + '<dl class="specs">' +
             ''.join('<div class="specs__row"><dt>%s</dt><dd>%s</dd></div>' % (_e(s['title']), _e(s['value'])) for s in spec_list) + '</dl>') if spec_list else \
        '<div class="specs-empty"><b>Характеристики уточняйте у&nbsp;менеджера</b>Подскажем толщину полотна, утепление, замки и&nbsp;фурнитуру для этой модели — оставьте заявку или позвоните.</div>'
    similar = sorted([x for x in _entry['products'] if x['id'] != p['id'] and p['cats'][0] in x['cats']],
                     key=lambda x: -(x.get('style', [None])[:1] == p.get('style', [None])[:1]))[:12]
    main = model_main
    main = main.replace('<nav class="crumbs js-crumbs" aria-label="Хлебные крошки"></nav>', '<nav class="crumbs js-crumbs" aria-label="Хлебные крошки">%s</nav>' % crumbs_html)
    main = main.replace('<img class="js-photo-img" alt="">', '<img class="js-photo-img" src="%s" alt="Входная дверь %s">' % (_e(photo), _e(p['title'])))
    main = main.replace('<div class="model__thumbs js-thumbs"></div>', '<div class="model__thumbs js-thumbs">%s</div>' % thumbs)
    main = main.replace('<div class="model__tags js-tags"></div>', '<div class="model__tags js-tags">%s</div>' % tags)
    main = main.replace('<h1 class="model__title js-title"></h1>', '<h1 class="model__title js-title">%s</h1>' % _e(p['title']))
    main = main.replace('<span class="js-price"></span>', '<span class="js-price">от %s</span>' % _rub(p['price']))
    main = main.replace('<dl class="model__params js-params"></dl>', '<dl class="model__params js-params">%s</dl>' % params)
    main = main.replace('<div class="js-specs"></div>', '<div class="js-specs">%s</div>' % specs)
    main = main.replace('<div class="similar-track scroller js-similar" data-drag></div>', '<div class="similar-track scroller js-similar" data-drag>%s</div>' % ''.join(map(_card, similar)))
    if cat:
        main = main.replace('<a class="btn btn--outline js-similar-all" href="catalog.html">', '<a class="btn btn--outline js-similar-all" href="%s">' % _cat_url(cat['slug']))
    product_ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': 'Входная дверь ' + p['title'], 'description': desc,
                  'brand': {'@type': 'Brand', 'name': 'Стальная линия'}, 'sku': p['id'],
                  'image': [SITE_URL + '/prototype-catalog/' + s for s in p['photos']],
                  'offers': {'@type': 'Offer', 'priceCurrency': 'RUB', 'price': int(round(p['price'])), 'availability': 'https://schema.org/InStock',
                             'url': SITE_URL + p['url'], 'seller': {'@type': 'Organization', 'name': 'Стальная линия'}}}
    _sitemap.append(_static_page(p['url'], title, desc, 'page-model', ' data-model-id="%s"' % p['id'], main, ('catalog.js?v=61',),
                                 ld=(product_ld, _crumbs_ld(crumbs)), image=photo))

# ---- страницы разделов ----
_cat_pages = [('', 'Каталог входных дверей', 'Двери для дома и квартиры собственного производства «Стальной линии». Выберите раздел или настройте фильтры — а если сложно определиться, подберём дверь по фото проёма.')]
_cat_pages += [(k, v[0], v[1]) for k, v in _PARENTS.items()]
_cat_pages += [(c['slug'], c['name'], c['lead']) for c in _entry['categories']]
for slug, name, lead in _cat_pages:
    items = [p for p in _entry['products'] if not slug or any(c == slug or c.startswith(slug + '/') for c in p['cats'])]
    if not items:
        continue
    path = _cat_url(slug)
    crumbs = [('Главная', '/'), ('Каталог', _cat_url())] + ([(name, path)] if slug else [])
    if slug and '/' in slug:
        par = slug.split('/')[0]
        crumbs = crumbs[:2] + [(_PARENTS[par][0], _cat_url(par))] + crumbs[2:]
    prices = [p['price'] for p in items if p['price']]
    title = '%s в Екатеринбурге — %d %s от %s | Стальная линия' % (name if slug else 'Входные двери', len(items),
            'модель' if len(items) % 10 == 1 and len(items) % 100 != 11 else 'модели' if 2 <= len(items) % 10 <= 4 and not 12 <= len(items) % 100 <= 14 else 'моделей',
            _rub(min(prices)).replace(' ', ' '))
    desc = lead + ' Цены от %s. Изготовление и установка в Екатеринбурге, гарантия 2 года.' % _rub(min(prices)).replace(' ', ' ')
    main = catalog_main
    main = main.replace('<h1 class="cat__title js-cat-title">Каталог входных дверей</h1>', '<h1 class="cat__title js-cat-title">%s</h1>' % _e(name))
    main = re.sub(r'<p class="cat__lead js-cat-lead">.*?</p>', '<p class="cat__lead js-cat-lead">%s</p>' % _e(lead), main, count=1, flags=re.S)
    if slug:
        main = main.replace('<span class="js-crumb-cat" hidden>/</span><span class="js-crumb-cat-name"></span>',
                            '<span class="js-crumb-cat">/</span><span class="js-crumb-cat-name">%s</span>' % _e(name))
    main = main.replace('<a href="../">Главная</a><span>/</span><a href="catalog.html">Каталог</a>', '<a href="/">Главная</a><span>/</span><a href="/catalog">Каталог</a>', 1)
    # первые 24 карточки (дальше — «Показать ещё» скриптом); у раздела — список всех моделей в микроразметке
    grid_m = re.search(r'<div class="cat-grid js-grid"[^>]*></div>', main)
    if grid_m:
        main = main.replace(grid_m.group(0), grid_m.group(0)[:-6] + ''.join(map(_card, items[:24])) + '</div>', 1)
    list_ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': name,
               'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': SITE_URL + p['url'], 'name': p['title']} for i, p in enumerate(items)]}
    _sitemap.append(_static_page(path, title, desc, 'page-catalog', ' data-cat="%s"' % slug, main, ('catalog.js?v=61',),
                                 ld=(list_ld, _crumbs_ld(crumbs)), image=items[0]['photos'][0] if items[0]['photos'] else ''))

# ---- межкомнатные двери Aurum: страницы моделей и разделов ----
_ABOUT_AURUM = 'Фабрика Aurum Doors — один из крупнейших производителей межкомнатных дверей. Полотна делают на оборудовании Barberan (Испания), Weinig (Германия) и Plasmek (Турция) из материалов Egger, Kronostar, Kastamonu, Renolit и Kleiberit.'
_acats = {c['slug']: c for c in _aurum['categories']}


def _plural(n, a, b, c):
    return a if n % 10 == 1 and n % 100 != 11 else b if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else c


def _sale_price(p):
    return round(p['price'] * 0.6) if p.get('sale') and p.get('price') else p.get('price')


def _price_html(p):
    if p.get('price'):
        return 'от %s%s<small> за полотно</small>' % (_rub(_sale_price(p)), ' <s>%s</s>' % _rub(p['price']) if p.get('sale') else '')
    return 'от %s<small> за комплект</small>' % _rub(p['priceKit']) if p.get('priceKit') else 'Цена по запросу'


def _card_in(p):
    sw = ''.join('<span class="pcard__swatch" style="background-image:url(%s)" title="%s"></span>' % (_e(c['swatch']), _e(c['name'])) for c in p['colors'][:7])
    if len(p['colors']) > 7:
        sw += '<span class="pcard__swatch-more">+%d</span>' % (len(p['colors']) - 7)
    badge = '<span class="pcard__badge pcard__badge--sale">Акция −40%</span>' if p.get('sale') else '<span class="pcard__badge">В наличии</span>' if p.get('inStock') else ''
    return ('<a class="pcard pcard--interior%s" href="%s"><div class="pcard__media">%s%s'
            '<span class="pcard__go" aria-hidden="true"><img src="../assets/icons/idea2-circle-40.svg" width="40" height="40" alt=""><img class="corner" src="../assets/icons/idea2-corner-10.svg" width="10" height="10" alt=""></span>'
            '</div><div class="pcard__body"><h3 class="pcard__title">%s</h3><p class="pcard__meta">Коллекция %s%s</p>%s<p class="pcard__price">%s</p></div></a>'
            % (' pcard--scene' if p.get('scene') else '', p['url'],
               '<img class="pcard__photo" src="%s" alt="Межкомнатная дверь %s" loading="lazy">' % (_e(p['photos'][0]), _e(p['title'])) if p['photos'] else '', badge,
               _e(p['title']), _e(p['collectionName']), ' · ' + _e(p['style'][0]) if p.get('style') else '',
               ('<div class="pcard__swatches" aria-label="%d %s">%s</div>' % (len(p['colors']), _plural(len(p['colors']), 'цвет', 'цвета', 'цветов'), sw)) if sw else
               ('<p class="pcard__ral">Любой цвет по RAL</p>' if p.get('colorNote') else ''), _price_html(p).replace(' <s>', ' <s>')))


def _intro_in(p):
    """своё вступление у каждой модели — из её данных (цвета, остекление, стиль, цена)"""
    style = {'Современный': ' в современном стиле', 'Неоклассика': ' в стиле неоклассика', 'Классика': ' в классическом стиле',
             'Минимализм': ' в стиле минимализм'}.get((p.get('style') or [''])[0], '')
    glass = ', со стеклом' if 'Со стеклом' in p.get('window', []) else ', глухое полотно'
    parts = ['%s — межкомнатная дверь%s%s. Коллекция %s фабрики Aurum Doors.' % (p['title'], style, glass, p['collectionName'])]
    if p['colors']:
        names = [c['name'] for c in p['colors']]
        parts.append('%d %s на выбор: %s%s.' % (len(names), _plural(len(names), 'цвет', 'цвета', 'цветов'), ', '.join(names[:4]), ' и другие' if len(names) > 4 else ''))
    elif p.get('colorNote'):
        parts.append('Окрашивается в любой цвет по палитре RAL.')
    if p.get('glass'):
        parts.append('Варианты стекла: %s.' % ', '.join(p['glass'][:4]).lower())
    if p.get('price'):
        parts.append('Полотно — от %s%s%s.' % (_rub(_sale_price(p)).replace(' ', ' '), ' (со скидкой 40%)' if p.get('sale') else '',
                                              ', комплект с коробкой и наличниками — от %s' % _rub(round(p['priceKit'] - p['price'] * 0.4) if p.get('sale') else p['priceKit']).replace(' ', ' ') if p.get('priceKit') else ''))
    parts.append('Посмотреть и заказать в Екатеринбурге можно в салоне «Стальной линии» в ИЦ ASTROOM' + (' — модель есть на складе.' if p.get('inStock') else '.'))
    return ' '.join(parts)


for p in _aurum['products']:
    cat = _acats.get(p['cats'][0])
    crumbs = [('Главная', '/'), ('Межкомнатные двери', _cat_url('mezhkom'))] + ([(cat['name'], _cat_url(cat['slug']))] if cat else []) + [(p['title'], p['url'])]
    crumbs_html = '<span>/</span>'.join('<a href="%s">%s</a>' % (u, _e(n)) for n, u in crumbs[:-1]) + '<span>/</span><span>%s</span>' % _e(p['title'])
    price_txt = (_rub(_sale_price(p)) if p.get('price') else _rub(p['priceKit']) if p.get('priceKit') else '').replace(' ', ' ')
    title = 'Межкомнатная дверь %s (коллекция %s) — купить в Екатеринбурге%s | Стальная линия' % (p['title'], p['collectionName'], ', цена от ' + price_txt if price_txt else '')
    intro = p['intro'] = _intro_in(p)  # сохраняется и в aurum.json — его показывает и catalog.js
    desc = intro[:240].rsplit(' ', 1)[0] + '…' if len(intro) > 250 else intro
    first = next((c for c in p['colors'] if c.get('photo')), None)
    photo = (first or {}).get('photo') or (p['photos'][0] if p['photos'] else '')
    tags = '<span class="tag tag--blue">Коллекция %s</span>' % _e(p['collectionName']) + ('<span class="tag tag--sale">Акция −40%</span>' if p.get('sale') else '') + ('<span class="tag tag--blue">В наличии</span>' if p.get('inStock') else '')
    spec = lambda t: next((s['value'] for s in p['specs'] if s['title'] == t), '')
    rows = [('Коллекция', p['collectionName']), ('Стиль', ', '.join(p.get('style', []))), ('Толщина полотна', spec('Толщина полотна')),
            ('Стекло и вставки', ', '.join(p.get('glass', []))), ('Размеры', p.get('sizes', ''))]
    params = ''.join('<dt>%s</dt><dd>%s</dd>' % (a, _e(b)) for a, b in rows if b)
    lst = [x for x in p['specs'] if x['title'] != 'Стиль']
    specs = ('<p class="specs-lead">%s</p>' % _e(intro) + ('<p class="specs-lead">%s</p>' % _e(p['desc']) if p.get('desc') else '') +
             ('<dl class="specs specs--text">%s</dl>' % ''.join('<div class="specs__row"><dt>%s</dt><dd>%s</dd></div>' % (_e(x['title']), _e(x['value'])) for x in lst) if lst else '') +
             '<div class="about-maker"><b>О фабрике</b><p>%s</p></div>' % _ABOUT_AURUM)
    swatches = ''.join('<button type="button" role="radio" aria-checked="%s" data-i="%d" title="%s" aria-label="%s" style="background-image:url(%s)"%s></button>'
                       % ('true' if c is first else 'false', i, _e(c['name']), _e(c['name']), _e(c['swatch']), ' class="is-active"' if c is first else '') for i, c in enumerate(p['colors']))
    similar = [x for x in _aurum['products'] if x['id'] != p['id'] and x['collection'] == p['collection']][:12]
    if len(similar) < 8:
        similar += [x for x in _aurum['products'] if x['id'] != p['id'] and x['collection'] != p['collection']][:8 - len(similar)]
    main = model_main
    main = main.replace('<nav class="crumbs js-crumbs" aria-label="Хлебные крошки"></nav>', '<nav class="crumbs js-crumbs" aria-label="Хлебные крошки">%s</nav>' % crumbs_html)
    main = main.replace('<img class="js-photo-img" alt="">', '<img class="js-photo-img" src="%s" alt="Межкомнатная дверь %s">' % (_e(photo), _e(p['title'])))
    main = main.replace('<div class="model__tags js-tags"></div>', '<div class="model__tags js-tags">%s</div>' % tags)
    main = main.replace('<p class="model__kicker js-kicker" hidden></p>', '<p class="model__kicker js-kicker">Межкомнатная дверь Aurum Doors</p>')
    main = main.replace('<h1 class="model__title js-title"></h1>', '<h1 class="model__title js-title">%s</h1>' % _e(p['title']))
    main = main.replace('<span class="js-price"></span>', '<span class="js-price">%s</span>' % _price_html(p))
    if p['colors']:
        main = main.replace('<div class="model__colors js-colors-wrap" hidden>', '<div class="model__colors js-colors-wrap">')
        main = main.replace('<b class="js-color-name"></b>', '<b class="js-color-name">%s</b>' % _e(first['name'] if first else p['colors'][0]['name']))
        main = main.replace('<div class="model__swatches js-colors" role="radiogroup" aria-label="Цвет двери"></div>', '<div class="model__swatches js-colors" role="radiogroup" aria-label="Цвет двери">%s</div>' % swatches)
    main = main.replace('<dl class="model__params js-params"></dl>', '<dl class="model__params js-params">%s</dl>' % params)
    main = main.replace('<div class="js-specs"></div>', '<div class="js-specs">%s</div>' % specs)
    main = main.replace('<div class="similar-track scroller js-similar" data-drag></div>', '<div class="similar-track scroller js-similar" data-drag>%s</div>' % ''.join(map(_card_in, similar)))
    main = main.replace('<a class="btn btn--outline js-similar-all" href="catalog.html">', '<a class="btn btn--outline js-similar-all" href="%s">' % _cat_url(cat['slug'] if cat else 'mezhkom'))
    offer_price = _sale_price(p) or p.get('priceKit')
    product_ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': 'Межкомнатная дверь ' + p['title'], 'description': intro,
                  'brand': {'@type': 'Brand', 'name': 'Aurum Doors'}, 'sku': p['id'],
                  'image': [SITE_URL + '/prototype-catalog/' + x for x in ([photo] if photo else [])]}
    if offer_price:
        product_ld['offers'] = {'@type': 'Offer', 'priceCurrency': 'RUB', 'price': int(offer_price), 'availability': 'https://schema.org/InStock',
                                'url': SITE_URL + p['url'], 'seller': {'@type': 'Organization', 'name': 'Стальная линия'}}
    _sitemap.append(_static_page(p['url'], title, desc, 'page-model', ' data-model-id="%s"' % p['id'], main, ('catalog.js?v=61',),
                                 ld=(product_ld, _crumbs_ld(crumbs)), image=photo))

json.dump(_aurum, open(os.path.join(OUT, 'data', 'aurum.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

_icats = [('mezhkom', 'Межкомнатные двери Aurum Doors', _ABOUT_AURUM + ' В каталоге — царговые и каркасно-щитовые коллекции, двери в эмали и скрытые двери под покраску.')]
_icats += [(c['slug'], c['name'], c['lead']) for c in _aurum['categories']]
for slug, name, lead in _icats:
    items = [p for p in _aurum['products'] if slug == 'mezhkom' or slug in p['cats']]
    if not items:
        continue
    # распродажа первой (как в каталоге по умолчанию)
    items = sorted(items, key=lambda p: (not p.get('sale'), (_sale_price(p) or 0) if p.get('sale') else 0))
    path = _cat_url(slug)
    crumbs = [('Главная', '/'), ('Межкомнатные двери', _cat_url('mezhkom'))] + ([(name, path)] if slug != 'mezhkom' else [])
    prices = [(_sale_price(p) or p.get('priceKit')) for p in items if (_sale_price(p) or p.get('priceKit'))]
    h1 = name if slug == 'mezhkom' else name
    title = ('%s в Екатеринбурге — %d %s от %s | Стальная линия' % ('Межкомнатные двери Aurum' if slug == 'mezhkom' else 'Межкомнатные двери ' + name + ' (Aurum)',
             len(items), _plural(len(items), 'модель', 'модели', 'моделей'), _rub(min(prices)).replace(' ', ' ')))
    desc = lead + ' Цены от %s, салон в Екатеринбурге — ИЦ ASTROOM.' % _rub(min(prices)).replace(' ', ' ')
    main = catalog_main
    main = main.replace('<h1 class="cat__title js-cat-title">Каталог входных дверей</h1>', '<h1 class="cat__title js-cat-title">%s</h1>' % _e(h1))
    if slug != 'mezhkom':
        main = main.replace('<p class="cat__kicker js-cat-kicker" hidden></p>', '<p class="cat__kicker js-cat-kicker">Межкомнатные двери Aurum Doors</p>')
        main = main.replace('<span class="js-crumb-cat" hidden>/</span><span class="js-crumb-cat-name"></span>',
                            '<span class="js-crumb-cat">/</span><span class="js-crumb-cat-name">%s</span>' % _e(name))
    main = re.sub(r'<p class="cat__lead js-cat-lead">.*?</p>', '<p class="cat__lead js-cat-lead">%s</p>' % _e(lead), main, count=1, flags=re.S)
    main = main.replace('<a href="../">Главная</a><span>/</span><a href="catalog.html">Каталог</a>', '<a href="/">Главная</a><span>/</span><a href="/catalog/mezhkom">Межкомнатные двери</a>', 1)
    grid_m = re.search(r'<div class="cat-grid js-grid"[^>]*></div>', main)
    if grid_m:
        main = main.replace(grid_m.group(0), grid_m.group(0)[:-6] + ''.join(map(_card_in, items[:24])) + '</div>', 1)
    list_ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': name,
               'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': SITE_URL + p['url'], 'name': p['title']} for i, p in enumerate(items)]}
    _sitemap.append(_static_page(path, title, desc, 'page-catalog', ' data-cat="%s"' % slug, main, ('catalog.js?v=61',),
                                 ld=(list_ld, _crumbs_ld(crumbs)), image=items[0]['photos'][0] if items[0]['photos'] else ''))


# ---- статьи (/blog, /st1 …) и сертификаты (/sert) — данные catalog-source/blog.py ----
_blog = _json('blog.json')
_ARROW = '<img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt="">'


def _art_card(a):
    return ('<a class="art-card" href="/%s"><span class="art-card__media"><img src="%s" alt="" loading="lazy" decoding="async"></span>'
            '<span class="art-card__cat">%s</span><span class="art-card__title">%s</span><span class="art-card__lead">%s</span></a>'
            % (a['slug'], a['cover'], _e(a['cat']), _e(a['title']), _e(a['lead'])))


def _art_body(a):
    out = []
    for b in a['body']:
        if b[0] == 'p':
            out.append('<p>%s</p>' % _e(b[1]))
        elif b[0] == 'h':
            out.append('<h2>%s</h2>' % _e(b[1]))
        elif b[0] == 'ul':
            out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % _e(x) for x in b[1]))
        elif b[0] == 'quote':
            out.append('<blockquote>%s</blockquote>' % _e(b[1]))
        elif b[0] == 'img':
            out.append('<figure><img src="%s" alt="%s" loading="lazy" decoding="async"><figcaption>%s</figcaption></figure>' % (b[1], _e(b[2]), _e(b[2])))
    return '\n        '.join(out)


_cats_order = []
for _a in _blog['articles']:
    if _a['cat'] not in _cats_order:
        _cats_order.append(_a['cat'])

_sections = ''.join(
    '    <section class="blog-sec wrap">\n      <h2 class="gid-sec__title">%s</h2>\n      <div class="art-grid">%s</div>\n    </section>\n'
    % (_e(c), ''.join(_art_card(a) for a in _blog['articles'] if a['cat'] == c)) for c in _cats_order)
blog_main = (
    '  <main class="port blog" id="blog">\n'
    '    <div class="wrap">\n'
    '      <nav class="crumbs port-crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a><span>/</span><span>Статьи</span></nav>\n'
    '      <h1 class="cat__title port-title blog-title">Полезные статьи</h1>\n'
    '      <p class="cat__lead port-lead">Как выбрать надёжную входную дверь, чем отличаются отделки и&nbsp;как подготовиться к&nbsp;доставке и&nbsp;установке.</p>\n'
    '    </div>\n' + _sections +
    '    <section class="cat-cta wrap blog-cta">\n'
    '      <div class="cat-cta__text">\n'
    '        <h2 class="cat-cta__title">Остались вопросы?</h2>\n'
    '        <p class="cat-cta__lead">Расскажем о&nbsp;моделях, отделках и&nbsp;монтаже, подберём дверь под ваш дом или квартиру.</p>\n'
    '      </div>\n'
    '      <a class="btn btn--gradient btn--lg" href="#" data-open-form="blog">Записаться на подбор ' + _ARROW + '</a>\n'
    '    </section>\n'
    '  </main>')

_sitemap.append(_static_page('/blog', 'Статьи о входных дверях — как выбрать, отделки, доставка | Стальная линия',
                             'Полезные статьи «Стальной линии»: как выбрать входную дверь в квартиру и в частный дом, панели OakPanel, экошпон, витражи, доборы и доставка.',
                             'page-portfolio page-blog', '', blog_main, (), image=_blog['articles'][0]['cover']))

for a in _blog['articles']:
    path = '/' + a['slug']
    more = [x for x in _blog['articles'] if x['slug'] != a['slug']]
    more = [x for x in more if x['cat'] == a['cat']] + [x for x in more if x['cat'] != a['cat']]
    cta_href, cta_attr = (a['cta'][1], '') if not a['cta'][1].startswith('#') else ('#', ' data-open-form="article"')
    main = (
        '  <main class="article-page" id="article">\n'
        '    <div class="wrap">\n'
        '      <nav class="crumbs port-crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a><span>/</span><a href="/blog">Статьи</a><span>/</span><span>%s</span></nav>\n'
        '    </div>\n'
        '    <article class="article wrap">\n'
        '      <header class="article__head">\n'
        '        <p class="article__cat">%s</p>\n'
        '        <h1 class="article__title">%s</h1>\n'
        '        <p class="article__lead">%s</p>\n'
        '      </header>\n'
        '      <figure class="article__cover"><img src="%s" alt="%s" fetchpriority="high"></figure>\n'
        '      <div class="article__body">\n        %s\n      </div>\n'
        '      <div class="article__cta">\n'
        '        <a class="btn btn--gradient btn--lg" href="%s"%s>%s %s</a>\n'
        '        <a class="btn btn--outline btn--lg" href="#" data-open-form="contact">Задать вопрос</a>\n'
        '      </div>\n'
        '    </article>\n'
        '    <section class="blog-sec wrap">\n'
        '      <h2 class="gid-sec__title">Другие статьи</h2>\n'
        '      <div class="art-grid">%s</div>\n'
        '    </section>\n'
        '  </main>') % (_e(a['title']), _e(a['cat']), _e(a['title']), _e(a['lead']), a['cover'], _e(a['title']), _art_body(a),
                        cta_href, cta_attr, _e(a['cta'][0]), _ARROW, ''.join(map(_art_card, more[:3])))
    crumbs = [('Главная', '/'), ('Статьи', '/blog'), (a['title'], path)]
    art_ld = {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['lead'],
              'image': SITE_URL + '/prototype-catalog/' + a['cover'], 'author': {'@type': 'Organization', 'name': 'Стальная линия'},
              'publisher': {'@type': 'Organization', 'name': 'Стальная линия'}, 'mainEntityOfPage': SITE_URL + path}
    _sitemap.append(_static_page(path, a['title'] + ' — статья | Стальная линия', a['lead'], 'page-article', '', main, (),
                                 ld=(art_ld, _crumbs_ld(crumbs)), image=a['cover']))

_cert_cards = ''.join(
    '<button type="button" class="cert" data-cert="%d"><span class="cert__media"><img src="%s" alt="%s" loading="lazy" decoding="async"></span>'
    '<span class="cert__title">%s</span><span class="cert__num">№ %s · действует до %s</span></button>'
    % (i, c['thumb'], _e(c['title']), _e(c['title']), _e(c['num']), c['until']) for i, c in enumerate(_blog['certs']))
_cert_data = json.dumps([{'img': c['img'], 'cap': c['title'] + ' · № ' + c['num']} for c in _blog['certs']], ensure_ascii=False)
_ICON_X = '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>'
_ICON_L = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M15 5l-7 7 7 7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
_ICON_R = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9 5l7 7-7 7" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
cert_main = (
    '  <main class="port certs" id="certs">\n'
    '    <div class="wrap">\n'
    '      <nav class="crumbs port-crumbs" aria-label="Хлебные крошки"><a href="/">Главная</a><span>/</span><span>Сертификаты</span></nav>\n'
    '      <h1 class="cat__title port-title blog-title">Сертификаты</h1>\n'
    '      <p class="cat__lead port-lead">Входные двери «Стальная линия» сертифицированы: продукция соответствует техническим регламентам, система менеджмента качества — стандарту ISO&nbsp;9001.</p>\n'
    '    </div>\n'
    '    <section class="blog-sec wrap">\n      <div class="cert-grid">' + _cert_cards + '</div>\n    </section>\n'
    '    <dialog class="shop-view js-cert-view" aria-label="Сертификат">\n'
    '      <button class="port-view__close js-cv-close" type="button" aria-label="Закрыть">' + _ICON_X + '</button>\n'
    '      <button class="port-view__nav port-view__nav--prev js-cv-prev" type="button" aria-label="Предыдущий">' + _ICON_L + '</button>\n'
    '      <button class="port-view__nav shop-view__next js-cv-next" type="button" aria-label="Следующий">' + _ICON_R + '</button>\n'
    '      <img class="shop-view__img cert-view__img js-cv-img" alt="">\n'
    '      <p class="shop-view__cap js-cv-cap"></p>\n'
    '    </dialog>\n'
    '    <script type="application/json" id="cert-data">' + _cert_data + '</script>\n'
    '    <script>\n'
    '    (function () {\n'
    "      var data = JSON.parse(document.getElementById('cert-data').textContent), view = document.querySelector('.js-cert-view');\n"
    "      var img = view.querySelector('.js-cv-img'), cap = view.querySelector('.js-cv-cap'), cur = 0;\n"
    "      function show(i) { cur = (i + data.length) % data.length; img.src = data[cur].img; cap.textContent = data[cur].cap + ' · ' + (cur + 1) + ' из ' + data.length; }\n"
    "      document.querySelectorAll('[data-cert]').forEach(function (b) { b.addEventListener('click', function () { show(+b.dataset.cert); view.showModal(); }); });\n"
    "      view.querySelector('.js-cv-close').onclick = function () { view.close(); };\n"
    "      view.querySelector('.js-cv-prev').onclick = function () { show(cur - 1); };\n"
    "      view.querySelector('.js-cv-next').onclick = function () { show(cur + 1); };\n"
    "      view.addEventListener('click', function (e) { if (e.target === view) view.close(); });\n"
    "      view.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') show(cur - 1); if (e.key === 'ArrowRight') show(cur + 1); });\n"
    '    })();\n'
    '    </script>\n'
    '  </main>')
# Сертификаты со старого сайта просрочены — страница не собирается, пока не будут загружены действующие (CERTS_READY=1)
shutil.rmtree(os.path.join(STATIC_ROOT, 'sert'), ignore_errors=True)
if os.environ.get('CERTS_READY') == '1':
  _sitemap.append(_static_page('/sert', 'Сертификаты на входные двери «Стальная линия»',
                             'Сертификаты соответствия на входные двери «Стальная линия» и сертификат системы менеджмента качества ISO 9001.',
                             'page-portfolio page-certs', '', cert_main, (), image=_blog['certs'][0]['thumb']))


# ---- разделы сайта по адресам старого сайта: /magazines, /gid, /port, /diz ----
_SECTIONS = [
    ('/magazines', 'Наши магазины — салоны «Стальной линии» в Екатеринбурге и 15 городах', 'Салоны входных дверей «Стальная линия»: интерьерный центр ASTROOM в Екатеринбурге, Арамиль, Тюмень, Сургут, Челябинск, Пермь и другие города. Адреса, телефоны, часы работы и фото салонов.',
     'page-portfolio page-stores', stores_main, ('stores.js?v=13',), 'img/stores/astroom.jpg'),
    ('/gid', 'Гид по продукту — обзоры моделей, ответы на вопросы и технологии | Стальная линия', 'Всё, что стоит знать перед выбором входной двери: видеообзоры моделей, ответы на частые вопросы, покрытия SteelLak и SteelTex, панели из дерева, витражи и двери любого размера.',
     'page-portfolio page-gid', gid_main + '\n\n  ', ('gid.js?v=2',), 'img/gid/rt-1.webp'),
    ('/port', 'Наши работы — установленные входные двери «Стальная линия»', 'Фото установленных входных дверей «Стальная линия» в домах и квартирах Екатеринбурга, Свердловской области, Тюмени и других городов.',
     'page-portfolio', portfolio_main, ('portfolio.js?v=14',), ''),
    ('/diz', 'Дизайнерам и архитекторам — сотрудничество со «Стальной линией»', 'Партнёрство для дизайнеров, архитекторов и застройщиков: двери любого размера и цвета, фальш-панели, авторские покрытия SteelLak и отделка из дерева. Повышенный процент и персональное сопровождение заказа.',
     'page-designers', designers_main, ('designers.js?v=1',), 'img/diz/hero-wood.webp'),
]
for _path, _title, _desc, _cls, _main, _scripts, _img in _SECTIONS:
    _sitemap.append(_static_page(_path, _title, _desc, _cls, '', _main, _scripts, image=_img))

print('статичных страниц:', len(_sitemap))
