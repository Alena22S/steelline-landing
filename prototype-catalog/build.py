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


def page(title, body_class, main, scripts=('catalog.js?v=56',)):
    h = fix(head)
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, h)
    # прототип каталога не индексируем до переноса на Astro (дубли steelline.store)
    h = re.sub(r'\s*<link rel="canonical"[^>]*>', '', h)
    h = re.sub(r'\s*<meta name="yandex-verification"[^>]*>', '', h)
    h = h.replace('<meta name="viewport" content="width=device-width, initial-scale=1">',
                  '<meta name="viewport" content="width=device-width, initial-scale=1">\n  <meta name="robots" content="noindex, nofollow">', 1)
    h += '  <link rel="stylesheet" href="catalog.css?v=84">\n</head>\n'
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
          <a class="btn btn--outline btn--outline-soft btn--lg" href="stores.html">Адреса салонов</a>
        </div>
      </div>
    </section>
  </main>'''

# версия картинок: при перерезке/повышении резкости образцов браузер должен взять новые файлы
designers_main = re.sub(r'(img/diz/[a-z0-9-]+\.webp)"', r'\1?v=6"', designers_main)
open(os.path.join(OUT, 'designers.html'), 'w', encoding='utf-8').write(page('Дизайнерам и архитекторам — Стальная линия', 'page-designers', designers_main, ('designers.js?v=1',)))
