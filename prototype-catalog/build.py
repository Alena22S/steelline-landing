"""Собирает прототипы страниц каталога из частей лендинга (шапка, подвал, форма заявки, уведомление о cookie).
Запуск: python3 prototype-catalog/build.py  → prototype-catalog/catalog.html и model.html
В Astro эти части станут общими компонентами; здесь — только для согласования дизайна.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'prototype-catalog')
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()


def part(start, end):
    i = src.index(start)
    j = src.index(end, i) + len(end)
    return src[i:j]


head = src[src.index('<!doctype html>'):src.index('</head>')]
header = part('<header class="header"', '</header>')
footer = part('<footer class="footer">', '</footer>')
cookie = part('<div class="cookie"', '</div>\n  </div>')
sticky = part('<a class="btn btn--gradient sticky-cta"', '</a>')
lead = part('<dialog class="lead" id="lead"', '</dialog>')
callback = part('<button class="callback-fab"', '</dialog>')
script = re.search(r'<script src="script\.js\?v=\d+"></script>', src).group(0)


def fix(html):
    """Пути лендинга → пути из папки прототипа."""
    html = re.sub(r'(src|href|srcset)="(assets/|favicon|styles\.css|script\.js|privacy\.html|consent\.html|send\.php)',
                  r'\1="../\2', html)
    html = html.replace('action="send.php"', 'action="../send.php"')
    html = html.replace('href="#top"', 'href="../"')
    html = html.replace('href="prototype-catalog/', 'href="')  # ссылки лендинга на каталог — изнутри папки каталога
    html = re.sub(r'href="#(?!")', 'href="../#', html)
    return html


def page(title, body_class, main):
    h = fix(head)
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % title, h)
    h += '  <link rel="stylesheet" href="catalog.css?v=13">\n</head>\n'
    nav_header = fix(header)
    return (h + '<body class="%s">\n\n  ' % body_class + nav_header + '\n\n' + main + '\n\n  ' + fix(cookie) +
            '\n\n  ' + fix(sticky).replace('href="../#contacts"', 'href="#"') + '\n\n  ' + fix(callback) + '\n\n  ' + fix(footer) + '\n\n  ' +
            fix(lead) + '\n\n  ' + fix(script) + '\n  <script src="catalog.js?v=10"></script>\n</body>\n</html>\n')


catalog_main = '''  <main class="cat" id="cat">
    <div class="cat__head wrap">
      <nav class="crumbs" aria-label="Хлебные крошки"><a href="../">Главная</a><span>/</span><a href="catalog.html">Каталог</a><span class="js-crumb-cat" hidden>/</span><span class="js-crumb-cat-name"></span></nav>
      <h1 class="cat__title js-cat-title">Каталог входных дверей</h1>
      <p class="cat__lead js-cat-lead">Двери для дома и квартиры собственного производства «Стальной линии». Выберите раздел или настройте фильтры — а если сложно определиться, подберём дверь по&nbsp;фото проёма.</p>
    </div>

    <nav class="cat-tabs wrap js-tabs" aria-label="Разделы каталога"></nav>

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
        <h1 class="model__title js-title"></h1>
        <p class="model__price"><span class="js-price"></span></p>
        <p class="model__note">Цена — за дверь в базовой комплектации. Итог зависит от размера, отделки и фурнитуры.</p>

        <div class="model__series js-series-wrap" hidden>
          <p class="model__label">Серия</p>
          <div class="model__series-list js-series"></div>
        </div>

        <dl class="model__params js-params"></dl>

        <div class="model__actions">
          <a class="btn btn--gradient btn--lg" href="#" data-open-form="model">Получить подбор двери <img src="../assets/icons/arrow-right-white-2.svg" width="24" height="24" alt=""></a>
          <a class="btn btn--outline btn--lg" href="#" data-open-form="contact">Записаться на подбор</a>
        </div>

        <ul class="model__perks">
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

    <section class="model-similar wrap">
      <div class="model-similar__head">
        <h2 class="model-similar__title">Похожие модели</h2>
        <a class="btn btn--outline js-similar-all" href="catalog.html">Все модели раздела</a>
      </div>
      <div class="cat-grid cat-grid--4 js-similar"></div>
    </section>

    <dialog class="photo-view js-photo-view" aria-label="Фото двери">
      <button class="photo-view__close js-photo-close" type="button" aria-label="Закрыть"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
      <img class="photo-view__img js-photo-view-img" alt="">
    </dialog>
  </main>'''

open(os.path.join(OUT, 'catalog.html'), 'w', encoding='utf-8').write(page('Каталог входных дверей — Стальная линия', 'page-catalog', catalog_main))
open(os.path.join(OUT, 'model.html'), 'w', encoding='utf-8').write(page('Модель двери — Стальная линия', 'page-model', model_main))
print('ok')
