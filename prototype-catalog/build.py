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


def page(title, body_class, main, scripts=('catalog.js?v=35',)):
    h = fix(head)
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, h)
    # прототип каталога не индексируем до переноса на Astro (дубли steelline.store)
    h = re.sub(r'\s*<link rel="canonical"[^>]*>', '', h)
    h = re.sub(r'\s*<meta name="yandex-verification"[^>]*>', '', h)
    h = h.replace('<meta name="viewport" content="width=device-width, initial-scale=1">',
                  '<meta name="viewport" content="width=device-width, initial-scale=1">\n  <meta name="robots" content="noindex, nofollow">', 1)
    h += '  <link rel="stylesheet" href="catalog.css?v=68">\n</head>\n'
    nav_header = fix(header)
    return (h + '<body class="%s">\n\n  ' % body_class + nav_header + '\n\n' + main + '\n\n  ' + fix(cookie) +
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
          <a class="btn sale-banner__btn" href="catalog.html?cat=mezhkom/kobalt">Смотреть двери Кобальт <img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt=""></a>
        </div>
        <div class="sale-banner__doors js-sale-doors" aria-hidden="true"></div>
      </div>
      <!-- на телефоне вместо баннера — готовая картинка распродажи -->
      <a class="sale-banner__photo" href="catalog.html?cat=mezhkom/kobalt">
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
_keep = ['id', 'kind', 'title', 'collection', 'collectionName', 'cats', 'price', 'priceKit', 'photos', 'colorNames',
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

open(os.path.join(OUT, 'portfolio.html'), 'w', encoding='utf-8').write(page('Наши работы — Стальная линия', 'page-portfolio', portfolio_main, ('portfolio.js?v=12',)))

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


# ---------- Гид по продукту (перенос steelline.store/gid) ----------
# Ролики и обложки — те же, что в окне «Видеообзоры» на главной; видео о фабрике и технологии — data/gid.json (catalog-source/gid.py)
import html as _html
_gid = _json('gid.json')
_ids = {p['title']: p['id'] for p in _entry['products'] if p.get('cats') and p['cats'][0].startswith('dom/')}
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
            c = c.replace('</article>', '  <a class="gid-reel__link" href="model.html?id=%s">Модель в каталоге</a>\n          </article>' % _ids[m.group(1)])
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
            '<span class="tech-card__media"><img src="%s" alt="" loading="lazy" decoding="async"></span>' % t['img'] +
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
