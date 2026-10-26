/* Прототип каталога: раздел (catalog.html?cat=…) и страница модели (model.html?id=…).
   Входные двери — data/catalog.json, межкомнатные (Aurum) — data/aurum.json. */
(function () {
  var PAGE = 24;
  // флажки «да/нет»: терморазрыв — отдельной группой «Утепление», остальные — «Предложения»
  var FLAGS = [
    { key: 'thermo', label: 'С терморазрывом', test: function (p) { return p.thermo; } },
    { key: 'specialPrice', label: 'По спец цене', test: function (p) { return p.specialPrice; } },
    { key: 'special', label: 'Спецпредложения', test: function (p) { return p.special.length > 0; } }
  ];
  var GROUPS = [
    { key: 'place', title: 'Назначение' },
    { key: 'style', title: 'Стиль' },
    { key: 'coating', title: 'Покрытие' },
    { key: 'window', title: 'Окно' },
    { key: 'series', title: 'Серия', label: function (v) { return 'Серия ' + v; } }
  ];
  // межкомнатные двери: свои фильтры
  var FLAGS_IN = [
    { key: 'sale', label: 'Акция −40%', test: function (p) { return p.sale; } },
    { key: 'inStock', label: 'В наличии', test: function (p) { return p.inStock; } }
  ];
  var GROUPS_IN = [
    { key: 'collectionName', title: 'Коллекция', many: false },
    { key: 'style', title: 'Стиль' },
    { key: 'colorNames', title: 'Цвет' },
    { key: 'window', title: 'Остекление' }
  ];
  function isInterior(p) { return p.kind === 'interior'; }
  var ABOUT_AURUM = 'Фабрика Aurum Doors — один из крупнейших производителей межкомнатных дверей. Полотна делают на оборудовании Barberan (Испания), Weinig (Германия) и Plasmek (Турция) из материалов Egger, Kronostar, Kastamonu, Renolit и Kleiberit.';
  // новые блоки страниц: если браузер показал старую страницу из кэша, их нет — работаем с пустышкой, а не падаем
  function q(sel) { return document.querySelector(sel) || document.createElement('div'); }
  // межкомнатные: кнопка открывает короткую форму «Получите скидку 40%» (режим sale у формы обратного звонка)
  function toSaleButton(b, text, model) {
    if (!b || !b.firstChild || !document.getElementById('callback')) return; // старая страница из кэша — оставляем как есть
    b.firstChild.nodeValue = text + ' ';
    b.removeAttribute('data-open-form');
    b.dataset.openCallback = 'sale';
    b.classList.add('is-sale'); // на телефоне показываем только кнопку распродажи
    if (model) b.dataset.model = model;
  }
  // «Похожие модели»: стрелки листают ленту на ширину видимой части; у краёв — неактивны, без прокрутки — скрыты
  function similarArrows() {
    var track = document.querySelector('.js-similar');
    var prev = document.querySelector('.js-similar-prev'), next = document.querySelector('.js-similar-next');
    if (!track || !prev || !next) return;
    function sync() {
      var media = track.querySelector('.pcard__media');
      if (media) prev.style.top = next.style.top = (media.offsetHeight / 2) + 'px'; // середина фото
      var max = track.scrollWidth - track.clientWidth;
      prev.hidden = next.hidden = max <= 2;
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= max - 2;
    }
    function step(dir) { track.scrollBy({ left: dir * track.clientWidth, behavior: 'smooth' }); }
    prev.onclick = function () { step(-1); };
    next.onclick = function () { step(1); };
    track.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', sync);
    sync();
  }
  function saleSticky(model) { toSaleButton(document.querySelector('.sticky-cta'), 'Заказать дверь со скидкой', model); }
  // распродажа склада: −40% на полотно; в комплекте дешевеет только полотно
  var SALE = 0.4;
  function salePrice(p) { return p.sale && p.price ? Math.round(p.price * (1 - SALE)) : p.price; }
  function saleKit(p) { return p.sale && p.price && p.priceKit ? Math.round(p.priceKit - p.price * SALE) : p.priceKit; }

  function rub(n) { return Math.round(n).toLocaleString('ru-RU').replace(/\s/g, ' ') + ' ₽'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function plural(n, one, few, many) {
    var m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
  }
  function meta(p) {
    var bits = [];
    if (p.series.length) bits.push('Серия ' + p.series.join(' / '));
    if (p.style[0]) bits.push(p.style[0]);
    if (p.coating[0]) bits.push(p.coating[0]);
    return bits.join(' · ');
  }
  // Тёплая дверь: «Хаски» — со снежинкой, остальные с терморазрывом — отметка «Терморазрыв» (внизу слева на фото)
  var ICON_SNOW = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2v20M4.2 6.5l15.6 11M4.2 17.5l15.6-11M9 3.5l3 2.5 3-2.5M9 20.5l3-2.5 3 2.5M3 10.2l3.6.8-1 3.6M21 13.8l-3.6-.8 1-3.6M3 13.8l3.6-.8-1-3.6M21 10.2l-3.6.8 1 3.6"/></svg>';
  var ICON_THERMO = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 14.8V4a2 2 0 1 0-4 0v10.8a4 4 0 1 0 4 0Z"/><path d="M12 9v7"/></svg>';
  function warmBadge(p) {
    if (p.cats.indexOf('dom/husky') !== -1) return '<span class="pcard__warm pcard__warm--husky" title="Тёплая серия «Хаски»">' + ICON_SNOW + 'Хаски</span>';
    if (p.thermo) return '<span class="pcard__warm" title="Дверь с терморазрывом — не промерзает">' + ICON_THERMO + 'Терморазрыв</span>';
    return '';
  }
  function card(p) {
    if (isInterior(p)) return cardInterior(p);
    var photos = p.photos.slice(0, 2).map(function (src, i) {
      return '<img class="pcard__photo" src="' + esc(src) + '" alt="' + (i ? '' : 'Входная дверь ' + esc(p.title)) + '" loading="lazy">';
    }).join('');
    return '<a class="pcard" href="model.html?id=' + p.id + '">' +
      '<div class="pcard__media">' + photos +
      (p.special.length ? '<span class="pcard__badge">Спецпредложение</span>' : '') + warmBadge(p) +
      '<span class="pcard__go" aria-hidden="true"><img src="../assets/icons/idea2-circle-40.svg" width="40" height="40" alt=""><img class="corner" src="../assets/icons/idea2-corner-10.svg" width="10" height="10" alt=""></span>' +
      '</div><div class="pcard__body"><h3 class="pcard__title">' + esc(p.title) + '</h3>' +
      '<p class="pcard__meta">' + esc(meta(p)) + '</p>' +
      '<p class="pcard__price">от ' + rub(p.price) + '</p></div></a>';
  }
  // межкомнатная: фото на белом фоне, кружки цветов, цена за полотно
  function cardInterior(p) {
    var sw = p.colors.slice(0, 7).map(function (c) {
      return '<span class="pcard__swatch" style="background-image:url(' + esc(c.swatch) + ')" title="' + esc(c.name) + '"></span>';
    }).join('') + (p.colors.length > 7 ? '<span class="pcard__swatch-more">+' + (p.colors.length - 7) + '</span>' : '');
    return '<a class="pcard pcard--interior' + (p.scene ? ' pcard--scene' : '') + '" href="model.html?id=' + p.id + '">' +
      '<div class="pcard__media">' +
      (p.photos[0] ? '<img class="pcard__photo" src="' + esc(p.photos[0]) + '" alt="Межкомнатная дверь ' + esc(p.title) + '" loading="lazy">' : '') +
      (p.sale ? '<span class="pcard__badge pcard__badge--sale">Акция −40%</span>' : p.inStock ? '<span class="pcard__badge">В наличии</span>' : '') +
      '<span class="pcard__go" aria-hidden="true"><img src="../assets/icons/idea2-circle-40.svg" width="40" height="40" alt=""><img class="corner" src="../assets/icons/idea2-corner-10.svg" width="10" height="10" alt=""></span>' +
      '</div><div class="pcard__body"><h3 class="pcard__title">' + esc(p.title) + '</h3>' +
      '<p class="pcard__meta">Коллекция ' + esc(p.collectionName) + (p.style[0] ? ' · ' + esc(p.style[0]) : '') + '</p>' +
      (sw ? '<div class="pcard__swatches" aria-label="' + p.colors.length + ' ' + plural(p.colors.length, 'цвет', 'цвета', 'цветов') + '">' + sw + '</div>' :
        (p.colorNote ? '<p class="pcard__ral">Любой цвет по RAL</p>' : '')) +
      '<p class="pcard__price">' + (p.price ? 'от ' + rub(salePrice(p)) + (p.sale ? ' <s>' + rub(p.price) + '</s>' : '') + '<small> за полотно</small>' : p.priceKit ? 'от ' + rub(p.priceKit) + '<small> за комплект</small>' : 'Цена по запросу') + '</p></div></a>';
  }

  /* Своя выпадашка в стиле сайта поверх обычного <select> (на телефоне остаётся системный список).
     <select> остаётся источником значения: при выборе меняем его и шлём 'change'. */
  function customSelect(select) {
    var wrap = document.createElement('div');
    wrap.className = 'csel';
    var id = 'csel-' + Math.random().toString(36).slice(2, 8);
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'csel__btn';
    btn.setAttribute('aria-haspopup', 'listbox');
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', id);
    var list = document.createElement('ul');
    list.className = 'csel__list';
    list.id = id;
    list.setAttribute('role', 'listbox');
    list.tabIndex = -1;
    list.hidden = true;
    Array.prototype.forEach.call(select.options, function (o, i) {
      var li = document.createElement('li');
      li.className = 'csel__opt';
      li.setAttribute('role', 'option');
      li.dataset.value = o.value;
      li.textContent = o.textContent;
      list.appendChild(li);
    });
    select.parentNode.insertBefore(wrap, select);
    wrap.appendChild(select);
    wrap.appendChild(btn);
    wrap.appendChild(list);
    var opts = list.querySelectorAll('.csel__opt');
    var active = select.selectedIndex;

    function sync() {
      btn.textContent = select.options[select.selectedIndex].textContent;
      opts.forEach(function (li, i) { li.setAttribute('aria-selected', i === select.selectedIndex ? 'true' : 'false'); });
    }
    function highlight(i) {
      active = (i + opts.length) % opts.length;
      opts.forEach(function (li, j) { li.classList.toggle('is-active', j === active); });
    }
    function open() {
      list.hidden = false; wrap.classList.add('is-open'); btn.setAttribute('aria-expanded', 'true');
      highlight(select.selectedIndex); list.focus();
    }
    function close(focusBtn) {
      list.hidden = true; wrap.classList.remove('is-open'); btn.setAttribute('aria-expanded', 'false');
      if (focusBtn) btn.focus();
    }
    function choose(i) {
      if (select.selectedIndex !== i) { select.selectedIndex = i; select.dispatchEvent(new Event('change', { bubbles: true })); }
      sync(); close(true);
    }
    btn.addEventListener('click', function () { list.hidden ? open() : close(); });
    btn.addEventListener('keydown', function (e) { if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); open(); } });
    list.addEventListener('click', function (e) { var li = e.target.closest('.csel__opt'); if (li) choose(Array.prototype.indexOf.call(opts, li)); });
    list.addEventListener('mousemove', function (e) { var li = e.target.closest('.csel__opt'); if (li) highlight(Array.prototype.indexOf.call(opts, li)); });
    list.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); highlight(active + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); highlight(active - 1); }
      else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); choose(active); }
      else if (e.key === 'Escape' || e.key === 'Tab') { close(e.key === 'Escape'); }
    });
    document.addEventListener('click', function (e) { if (!wrap.contains(e.target) && !list.hidden) close(); });
    select.addEventListener('change', sync);
    sync();
  }

  // загружаем только нужные данные: входные — data/catalog.json; межкомнатные — лёгкий список для каталога
  // или полный data/aurum.json для страницы модели; счётчики переключателя — data/counts.json
  var V = 8;
  function load(name) { return fetch('data/' + name + '?v=' + V).then(function (r) { return r.json(); }); }
  var qs = new URLSearchParams(location.search);
  var isCat = !!document.getElementById('cat');
  var wantInterior = isCat ? /^mezhkom(\/|$)/.test(qs.get('cat') || '') : /^au-/.test(qs.get('id') || '');
  Promise.all([
    load(wantInterior ? (isCat ? 'aurum-list.json' : 'aurum.json') : 'catalog.json'),
    isCat ? load('counts.json').catch(function () { return null; }) : null
  ]).then(function (res) {
    var data = res[0];
    data.counts = res[1];
    if (!wantInterior) data.products.forEach(function (p) { p.kind = 'entry'; });
    if (isCat) initCatalog(data);
    if (document.getElementById('model')) initModel(data);
  });

  /* ---------- Раздел каталога ---------- */
  function initCatalog(data) {
    var params = new URLSearchParams(location.search);
    var catSlug = params.get('cat') || '';
    // родительские разделы: все двери для дома / для квартиры
    var PARENTS = {
      dom: { slug: 'dom', name: 'Двери в дом', lead: 'Входные двери для частного дома и коттеджа: тёплые, с терморазрывом, для нестандартных проёмов и по спец цене.' },
      kvartira: { slug: 'kvartira', name: 'Двери в квартиру', lead: 'Надёжные входные двери для квартиры: классика и современный дизайн, умные замки.' },
      mezhkom: { slug: 'mezhkom', name: 'Межкомнатные двери', lead: ABOUT_AURUM + ' В каталоге — царговые и каркасно-щитовые коллекции, двери в эмали и скрытые двери под покраску.' }
    };
    var cat = data.categories.filter(function (c) { return c.slug === catSlug; })[0] || PARENTS[catSlug];
    // вид каталога: входные или межкомнатные двери — у каждого свои разделы и фильтры
    var interior = catSlug === 'mezhkom' || catSlug.indexOf('mezhkom/') === 0;
    var kindProducts = data.products.filter(function (p) { return isInterior(p) === interior; });
    var flags = interior ? FLAGS_IN : FLAGS;
    var groups = interior ? GROUPS_IN : GROUPS;
    var base = !cat || cat.slug === 'mezhkom' ? kindProducts : kindProducts.filter(function (p) {
      return p.cats.some(function (c) { return c === cat.slug || c.indexOf(cat.slug + '/') === 0; });
    });

    // шапка
    if (cat) {
      document.querySelector('.js-cat-title').textContent = cat.name;
      document.querySelector('.js-cat-lead').textContent = cat.lead;
      document.querySelector('.js-crumb-cat').hidden = false;
      document.querySelector('.js-crumb-cat-name').textContent = cat.name;
      document.title = cat.name + ' — Стальная линия';
    }
    // межкомнатные: бренд в заголовке — «Межкомнатные двери Aurum Doors», у коллекций — строкой над названием
    if (interior) {
      var BRAND = 'Межкомнатные двери Aurum Doors';
      if (cat.slug === 'mezhkom') {
        document.querySelector('.js-cat-title').textContent = BRAND;
        document.title = BRAND + ' — Стальная линия';
      } else {
        var kicker = q('.js-cat-kicker');
        kicker.textContent = BRAND; kicker.hidden = false;
        document.title = cat.name + ' — межкомнатные двери Aurum Doors — Стальная линия';
      }
    }
    // входные / межкомнатные
    var counts = data.counts || {};
    var nEntry = interior ? counts.entry : kindProducts.length;
    var nInterior = interior ? kindProducts.length : counts.interior;
    q('.js-kinds').innerHTML =
      '<a class="cat-kind' + (interior ? '' : ' is-active') + '" href="catalog.html"' + (interior ? '' : ' aria-current="page"') + '>Входные двери' + (nEntry ? ' <span>' + nEntry + '</span>' : '') + '</a>' +
      '<a class="cat-kind' + (interior ? ' is-active' : '') + '" href="catalog.html?cat=mezhkom"' + (interior ? ' aria-current="page"' : '') + '>Межкомнатные двери' + (nInterior ? ' <span>' + nInterior + '</span>' : '') + '</a>';
    if (interior) {
      saleSticky();
      // баннер распродажи склада: три двери Кобальт в разных цветах
      var picks = [['au-co7', 'Аляска'], ['au-co2', 'Антрацит'], ['au-co12', 'Deep Green']];
      var doors = picks.map(function (pk) {
        var p = data.products.filter(function (x) { return x.id === pk[0]; })[0];
        if (!p) return '';
        var c = p.colors.filter(function (c) { return c.name === pk[1] && c.photo; })[0];
        var src = c ? c.photo : p.photos[0];
        return src ? '<img src="' + esc(src) + '" alt="" loading="lazy">' : '';
      }).join('');
      q('.js-sale').hidden = false;
      q('.js-sale-doors').innerHTML = doors;
      if (cat && cat.slug === 'mezhkom/kobalt') q('.sale-banner__btn').hidden = true;
    }
    if (interior && cat && cat.slug === 'mezhkom') {
      document.querySelector('.js-crumb-cat').hidden = true;
      document.querySelector('.js-crumb-cat-name').textContent = '';
    }

    // разделы
    var tabs = '';
    if (interior) {
      tabs = '<a class="cat-tab' + (cat.slug === 'mezhkom' ? ' is-active' : '') + '" href="catalog.html?cat=mezhkom">Все межкомнатные <span>' + kindProducts.length + '</span></a>';
    } else {
      tabs = '<a class="cat-tab' + (cat ? '' : ' is-active') + '" href="catalog.html">Все входные <span>' + kindProducts.length + '</span></a>';
      ['dom', 'kvartira'].forEach(function (k) {
        var n = kindProducts.filter(function (p) { return p.cats.some(function (c) { return c.indexOf(k + '/') === 0; }); }).length;
        tabs += '<a class="cat-tab' + (cat && cat.slug === k ? ' is-active' : '') + '" href="catalog.html?cat=' + k + '">' + PARENTS[k].name + ' <span>' + n + '</span></a>';
      });
    }
    data.categories.forEach(function (c) {
      if ((c.slug.indexOf('mezhkom/') === 0) !== interior) return;
      tabs += '<a class="cat-tab' + (cat && cat.slug === c.slug ? ' is-active' : '') + '" href="catalog.html?cat=' + c.slug + '">' + esc(c.name) + ' <span>' + c.count + '</span></a>';
    });
    document.querySelector('.js-tabs').innerHTML = tabs;

    // фильтры
    var state = { sort: 'popular', shown: PAGE };
    flags.forEach(function (f) { state[f.key] = false; });
    groups.forEach(function (g) { state[g.key] = []; });
    var groupsEl = document.querySelector('.js-filter-groups');
    var html = '';
    groups.forEach(function (g) {
      // все группы показываем всегда, варианты — по всему каталогу; недоступные в разделе — бледные с нулём
      var vals = {};
      kindProducts.forEach(function (p) { [].concat(p[g.key] || []).forEach(function (v) { vals[v] = 1; }); });
      var list = Object.keys(vals).sort();
      html += '<div class="fgroup" role="group" aria-label="' + g.title + '"><p class="fgroup__title">' + g.title + '</p>';
      list.forEach(function (v) {
        html += '<label class="fcheck"><input type="checkbox" data-key="' + g.key + '" value="' + esc(v) + '">' +
          esc(g.label ? g.label(v) : v) + '<span data-count></span></label>';
      });
      html += '</div>';
    });
    function flagGroup(title, keys) {
      var list = flags.filter(function (f) { return keys.indexOf(f.key) !== -1; });
      return '<div class="fgroup" role="group" aria-label="' + title + '"><p class="fgroup__title">' + title + '</p>' + list.map(function (f) {
        return '<label class="fcheck"><input type="checkbox" data-flag="' + f.key + '">' + f.label + '<span data-count></span></label>';
      }).join('') + '</div>';
    }
    // порядок: Назначение, Стиль, Утепление, Предложения, Покрытие, Окно, Серия — главное видно без прокрутки
    if (interior) html = flagGroup('Наличие и акции', ['sale', 'inStock']) + html;
    else {
      var flagsHtml = flagGroup('Утепление', ['thermo']) + flagGroup('Предложения', ['specialPrice', 'special']);
      var anchor = '<div class="fgroup" role="group" aria-label="Покрытие">';
      html = html.indexOf(anchor) !== -1 ? html.replace(anchor, flagsHtml + anchor) : html + flagsHtml;
    }
    groupsEl.innerHTML = html;

    function match(p, skip) {
      if (!flags.every(function (f) { return !state[f.key] || skip === f.key || f.test(p); })) return false;
      return groups.every(function (g) {
        if (g.key === skip || !state[g.key].length) return true;
        return [].concat(p[g.key] || []).some(function (v) { return state[g.key].indexOf(v) !== -1; });
      });
    }

    var grid = document.querySelector('.js-grid');
    // сколько карточек в ряду сейчас (3 на десктопе, 2 на телефоне)
    function gridCols() {
      var t = getComputedStyle(grid).gridTemplateColumns;
      return t && t !== 'none' ? t.split(' ').length : 3;
    }
    // ряд дорогих, ряд доступных. Порог — 100 000 ₽; если доступных в разделе меньше ряда — делим раздел пополам по цене
    // Витрина входных дверей (порядок важен; 24 — первая страница, 9 — три ряда по три). Вариант выбирается в адресе: ?vitrina=u|s|e|h|m|a|b|c
    var FEATURED_SETS = {
      // «Ваш порядок» (основной): первые 9 — по списку заказчика (26.10.2026), дальше 15 из варианта «Схема первого экрана»
      u: ['707455349952', '727126755161', '485789465810', // Эльвина 143, Беверли 175, Норд (Хаски) 168
          '196224552391', '801440556623', '410582299302', // Фрейзер (Хаски) 150, Арктик (Хаски) 121, Фрамос 267
          '644465989481', '715888846891', '696101749782', // Мельбурн (Хаски) 198, Сага 217, Анкона лайт 190
          '511659300162', '639850174542', '391274640701', // Мерибель (Хаски), Гринвич, Авенида (Хаски)
          '544618535592', '885997904470', '160668509411', // Канзас, Монарх, Атлантик (Хаски)
          '865382261322', '358597898613', '662226044462', // Шинон, Амидон, Квадро
          '799710543723', '388584810892', '997742215971', // Алерт (Хаски), Рифлессо, Кэмпер
          '352267633451', '417186517882', '834251478301'], // Бангалор (Хаски), Эдда, Бронкс
      // «Схема первого экрана, эффектный» (вариант 2): та же ценовая схема, самые эффектные модели — рейки, камень, витражи, арки
      e: ['109028430073', '715888846891', '865382261322', // Борнео (Хаски) 150, Сага 217, Шинон 129
          '834251478301', '867324225502', '212925614541', // Бронкс 163 (дерево), Сатори 282 (витраж с ковкой), Барроу (Хаски) 143
          '662226044462', '639850174542', '358597898613', // Квадро 156, Гринвич 206, Амидон 94
          '544618535592', '889359502682', '388584810892', // Канзас 158, Акира 2 355 (витраж), Рифлессо 186
          '997742215971', '352267633451', '417186517882', // Кэмпер, Бангалор (Хаски), Эдда
          '511659300162', '479383539752', '140522037811', // Мерибель (Хаски), Лейден, Шамони
          '190049193841', '644465989481', '290363837272', // Конфер, Мельбурн (Хаски), Тонфер
          '984652554512', '391274640701', '645622433032'], // Этьен, Авенида (Хаски), Шарль
      // «Схема первого экрана» (основной). Первые 12 по ценовой схеме: 110–160 тыс. — 5, 160–250 — 3, до 110 — 1–2, от 250 — 2.
      // 1 современная тёмная ~150, 2 премиальный дизайн, 3 стильная доступнее, 4 отделка под дерево, 5 эксклюзив с витражом, 6 тёплая «Хаски»;
      // дальше 12 популярных дверей для дома с терморазрывом. Дверей для дома дешевле 110 тыс. в каталоге одна — Амидон (без терморазрыва).
      s: ['511659300162', '639850174542', '391274640701', // Мерибель (Хаски) 152, Гринвич 206, Авенида (Хаски) 114
          '544618535592', '885997904470', '160668509411', // Канзас 158, Монарх 255 (двупольная, витраж), Атлантик (Хаски) 143
          '865382261322', '715888846891', '358597898613', // Шинон 129, Сага 217, Амидон 94
          '662226044462', '799710543723', '388584810892', // Квадро 156, Алерт (Хаски, витраж) 292, Рифлессо 186
          '997742215971', '352267633451', '417186517882', // Кэмпер, Бангалор (Хаски), Эдда
          '834251478301', '479383539752', '140522037811', // Бронкс, Лейден, Шамони
          '190049193841', '644465989481', '290363837272', // Конфер, Мельбурн (Хаски), Тонфер
          '984652554512', '109028430073', '645622433032'], // Этьен, Борнео (Хаски), Шарль
      // «Первые 24 для дома» (основной): только двери с терморазрывом и «Хаски» — для частных домов Екатеринбурга;
      // сначала тренды и доступные (114–206 тыс.), дальше популярные средние, классика — ближе к концу; светлые и тёмные чередуются
      h: ['865382261322', '109028430073', '662226044462', // Шинон, Борнео (Хаски), Квадро
          '391274640701', '639850174542', '388584810892', // Авенида (Хаски), Гринвич, Рифлессо
          '997742215971', '511659300162', '417186517882', // Кэмпер, Мерибель (Хаски), Эдда
          '544618535592', '715888846891', '479383539752', // Канзас, Сага, Лейден
          '352267633451', '834251478301', '290363837272', // Бангалор (Хаски), Бронкс, Тонфер
          '140522037811', '190049193841', '984652554512', // Шамони, Конфер, Этьен
          '644465989481', '875937646681', '954933960452', // Мельбурн (Хаски), Квинс, Степ
          '645622433032', '747351151292', '552629762921'], // Шарль, Авиор, Бонди
      // «Тренды + доступные» (основной): рейки из дерева, камень, рифление, бежевые арки; доступные и средние чередуются
      // Шинон, Гринвич, Эдда (квартира), Рифлессо, Тюринген, Сага, Кобург (квартира), Квадро, Бангалор (Хаски)
      m: ['865382261322', '639850174542', '588806952612', '388584810892', '299646641482', '715888846891', '127364557481', '662226044462', '352267633451'],
      // «Стильные и доступные» (92–156 тыс.): спокойная палитра, светлые и тёмные чередуются
      // Кобург (квартира), Шинон, Амидон, Кэмпер, Тюринген, Эдда (квартира), Мерибель (Хаски), Квадро, Софико
      c: ['127364557481', '865382261322', '358597898613', '997742215971', '299646641482', '588806952612', '511659300162', '662226044462', '139240906642'],
      // «Стильные»: спокойная палитра — тёмные, древесные, серые и бежевые; светлые и тёмные чередуются
      // Гринвич, Шамони, Сага, Конфер, Рифлессо, Шарль, Бангалор (Хаски), Клеон (квартира), Амальфи
      b: ['639850174542', '140522037811', '715888846891', '190049193841', '388584810892', '645622433032', '352267633451', '481348959631', '775199909552'],
      // «Яркие»: Бореалис, Бонди, Гринвич, Шарль, Пиктор, Бавария, Мельбурн (Хаски), Кери (квартира), Бенвиль
      a: ['569161028601', '552629762921', '639850174542', '645622433032', '365283486141', '904487537271', '644465989481', '148091394782', '240455563612']
    };
    // По умолчанию — исходный порядок (ряды дорогие/доступные) без витрины; только очень дорогая Рапсодия 2 (468 тыс.)
    // меняется местами с Агиосом (204 тыс.). Варианты витрины — ?vitrina=o|u|s|e|h|m|a|b|c (o — поднятые модели вперемешку с доступными)
    // сначала Рапсодия 2 ↔ Агиос (Агиос — первым), затем Рапсодия 2 ↔ Аклавик: Аклавик встаёт на её место, она уходит ниже
    // и Рифлессо ↔ Эльвина (Эльвина — в первом ряду)
    var SWAP = [['694852897071', '319409221712'], ['694852897071', '326236939772'], ['388584810892', '707455349952']];
    // Подняты наверх по просьбе заказчика (26.10.2026), в этом порядке; дальше — исходные ряды
    // Бронкс, Агиос, Кинсейл, Альфор, Алон, Винсент, Неаполь, Авентура, Плимут, Дакота, Квинс, Онтарио, Лансберг (для дома, 187 тыс.)
    FEATURED_SETS.o = ['834251478301', '319409221712', '994876706952', '865796705801', '875074858852', '596742865482', '930320278203',
                       '173462420701', '648595438322', '503738967651', '875937646681', '314633226901', '640672711431'];
    var FEATURED = FEATURED_SETS[(location.search.match(/[?&]vitrina=([ousehmabc])/) || [])[1]] || [];
    function alternateRows(list, cols) {
      var limit = 100000;
      if (list.filter(function (p) { return p.price < limit; }).length < cols) {
        var prices = list.map(function (p) { return p.price; }).sort(function (a, b) { return a - b; });
        limit = prices[Math.floor(prices.length / 2)] || limit;
      }
      var hi = list.filter(function (p) { return p.price >= limit; });
      var lo = list.filter(function (p) { return p.price < limit; });
      var out = [], i = 0, j = 0;
      while (i < hi.length || j < lo.length) {
        out = out.concat(hi.slice(i, i + cols)); i += cols;
        out = out.concat(lo.slice(j, j + cols)); j += cols;
      }
      return out;
    }
    var more = document.querySelector('.js-more');
    var empty = document.querySelector('.js-empty');

    function render() {
      var list = base.filter(function (p) { return match(p); });
      var pr = function (p) { return isInterior(p) ? (salePrice(p) || p.priceKit || 0) : p.price; };
      // входные: по умолчанию ряды чередуются — дорогие и доступные (до 100 000 ₽), чтобы не казалось, что всё дорого
      if (!interior && state.sort === 'popular') {
        // «витрина»: красивые модели в разных стилях из середины ценового диапазона — первыми, остальные рядами дорогие/доступные
        var top = FEATURED.map(function (id) { return list.filter(function (p) { return p.id === id; })[0]; }).filter(Boolean);
        var rest = list.filter(function (p) { return top.indexOf(p) === -1; });
        if (FEATURED === FEATURED_SETS.o) {
          // поднятые модели — рядами вперемешку с рядами доступных дверей для дома (до 160 тыс., сначала с терморазрывом и подешевле)
          var cols = gridCols();
          var pool = rest.filter(function (p) { return p.place.indexOf('Для дома') !== -1 && p.price < 160000; })
            .sort(function (a, b) { return (b.thermo ? 1 : 0) - (a.thermo ? 1 : 0) || a.price - b.price; });
          var mixed = [];
          for (var k = 0; k < top.length; k += cols) {
            mixed = mixed.concat(top.slice(k, k + cols));
            mixed = mixed.concat(pool.splice(0, cols));
          }
          rest = rest.filter(function (p) { return mixed.indexOf(p) === -1; });
          top = mixed;
        }
        list = top.concat(alternateRows(rest, gridCols()));
        if (!FEATURED.length) SWAP.forEach(function (pair) {
          var a = -1, b = -1;
          list.forEach(function (p, k) { if (p.id === pair[0]) a = k; if (p.id === pair[1]) b = k; });
          if (a !== -1 && b !== -1) { var t = list[a]; list[a] = list[b]; list[b] = t; }
        });
      }
      // межкомнатные: по умолчанию сначала двери на распродаже — от самых дешёвых (цена со скидкой), потом остальные в прежнем порядке
      if (interior && state.sort === 'popular') list.sort(function (a, b) {
        if (a.sale !== b.sale) return (b.sale ? 1 : 0) - (a.sale ? 1 : 0);
        return a.sale ? pr(a) - pr(b) : 0;
      });
      if (state.sort === 'price-asc') list.sort(function (a, b) { return pr(a) - pr(b); });
      if (state.sort === 'price-desc') list.sort(function (a, b) { return pr(b) - pr(a); });
      if (state.sort === 'name') list.sort(function (a, b) { return a.title.localeCompare(b.title, 'ru'); });

      grid.innerHTML = list.slice(0, state.shown).map(card).join('');
      grid.hidden = !list.length;
      empty.hidden = !!list.length;
      more.hidden = list.length <= state.shown;
      more.textContent = 'Показать ещё ' + Math.min(PAGE, list.length - state.shown);
      document.querySelector('.js-count').textContent = 'Найдено ' + list.length + ' ' + plural(list.length, 'модель', 'модели', 'моделей');

      // счётчики у вариантов: сколько будет, если отметить
      groupsEl.querySelectorAll('input').forEach(function (inp) {
        var key = inp.dataset.key, flag = inp.dataset.flag, n;
        if (flag) {
          var f = flags.filter(function (x) { return x.key === flag; })[0];
          n = base.filter(function (p) { return match(p, flag) && f.test(p); }).length;
        } else n = base.filter(function (p) { return match(p, key) && [].concat(p[key] || []).indexOf(inp.value) !== -1; }).length;
        var label = inp.closest('.fcheck');
        label.querySelector('[data-count]').textContent = n;
        label.classList.toggle('is-zero', !n && !inp.checked);
        inp.disabled = !n && !inp.checked; // в этом разделе таких моделей нет — нечего выбирать
      });
      var active = groups.reduce(function (s, g) { return s + state[g.key].length; }, 0) + flags.filter(function (f) { return state[f.key]; }).length;
      var badge = document.querySelector('.js-active-count');
      badge.hidden = !active; badge.textContent = active;
      document.querySelectorAll('.cat-filters__reset').forEach(function (b) { b.disabled = !active; });
      document.querySelector('.cat-filters__apply').textContent = 'Показать ' + list.length + ' ' + plural(list.length, 'модель', 'модели', 'моделей');
    }

    groupsEl.addEventListener('change', function (e) {
      var inp = e.target; var key = inp.dataset.key;
      if (inp.dataset.flag) state[inp.dataset.flag] = inp.checked;
      else {
        var arr = state[key]; var i = arr.indexOf(inp.value);
        if (inp.checked && i === -1) arr.push(inp.value);
        if (!inp.checked && i !== -1) arr.splice(i, 1);
      }
      state.shown = PAGE; render();
    });
    var sortSelect = document.querySelector('.js-sort');
    sortSelect.addEventListener('change', function (e) { state.sort = e.target.value; render(); });
    customSelect(sortSelect);
    more.addEventListener('click', function () { state.shown += PAGE; render(); });
    document.querySelectorAll('.js-reset').forEach(function (b) {
      b.addEventListener('click', function () {
        groups.forEach(function (g) { state[g.key] = []; }); flags.forEach(function (f) { state[f.key] = false; }); state.shown = PAGE;
        groupsEl.querySelectorAll('input').forEach(function (i) { i.checked = false; });
        render();
      });
    });

    // мобильная панель фильтров
    var panel = document.querySelector('.js-filters');
    function setPanel(open) { panel.classList.toggle('is-open', open); document.body.classList.toggle('filters-open', open); }
    document.querySelector('.js-filters-open').addEventListener('click', function () { setPanel(true); });
    document.querySelectorAll('.js-filters-close').forEach(function (b) { b.addEventListener('click', function () { setPanel(false); }); });
    document.addEventListener('click', function (e) { if (document.body.classList.contains('filters-open') && !panel.contains(e.target) && !e.target.closest('.js-filters-open')) setPanel(false); });

    var lastCols = gridCols();
    window.addEventListener('resize', function () { var c = gridCols(); if (c !== lastCols) { lastCols = c; render(); } });
    render();
  }

  /* ---------- Страница модели ---------- */
  function initModel(data) {
    var id = new URLSearchParams(location.search).get('id');
    var p = data.products.filter(function (x) { return x.id === id; })[0] || data.products[0];
    if (isInterior(p)) return initInterior(p, data);
    var cat = data.categories.filter(function (c) { return c.slug === p.cats[0]; })[0];
    document.title = 'Входная дверь ' + p.title + ' — Стальная линия';

    document.querySelector('.js-crumbs').innerHTML = '<a href="../">Главная</a><span>/</span><a href="catalog.html">Каталог</a><span>/</span>' +
      (cat ? '<a href="catalog.html?cat=' + cat.slug + '">' + esc(cat.name) + '</a><span>/</span>' : '') + '<span>' + esc(p.title) + '</span>';
    document.querySelector('.js-title').textContent = p.title;

    var tags = '';
    if (cat) tags += '<span class="tag tag--blue">' + esc(cat.name) + '</span>';
    if (p.special.length) tags += '<span class="tag tag--blue">Спецпредложение</span>';
    document.querySelector('.js-tags').innerHTML = tags;

    // галерея
    var photo = document.querySelector('.js-photo-img');
    var thumbs = document.querySelector('.js-thumbs');
    function showPhoto(i) {
      photo.src = p.photos[i]; photo.alt = 'Входная дверь ' + p.title + (i ? ', вид изнутри' : '');
      thumbs.querySelectorAll('.model__thumb').forEach(function (t, j) { t.classList.toggle('is-active', i === j); });
    }
    thumbs.innerHTML = p.photos.length > 1 ? p.photos.map(function (src, i) {
      return '<button class="model__thumb" type="button" aria-label="Фото ' + (i + 1) + '"><img src="' + esc(src) + '" alt=""></button>';
    }).join('') : '';
    thumbs.querySelectorAll('.model__thumb').forEach(function (t, i) { t.addEventListener('click', function () { showPhoto(i); }); });
    showPhoto(0);

    var view = document.querySelector('.js-photo-view');
    document.querySelector('.js-photo').addEventListener('click', function () {
      document.querySelector('.js-photo-view-img').src = photo.src;
      view.showModal();
    });
    document.querySelector('.js-photo-close').addEventListener('click', function () { view.close(); });
    view.addEventListener('click', function (e) { if (e.target === view) view.close(); });

    // серия и цена
    var priceEl = document.querySelector('.js-price');
    var bySeries = {};
    p.editions.forEach(function (e) { if (e.series && e.price && (!bySeries[e.series] || e.price < bySeries[e.series])) bySeries[e.series] = e.price; });
    var series = Object.keys(bySeries).sort(function (a, b) { return a - b; });
    priceEl.textContent = 'от ' + rub(p.price);
    if (series.length > 1) {
      document.querySelector('.js-series-wrap').hidden = false;
      var sl = document.querySelector('.js-series');
      sl.innerHTML = series.map(function (s) { return '<button type="button" data-s="' + s + '">Серия ' + s + '<span>от ' + rub(bySeries[s]) + '</span></button>'; }).join('');
      sl.addEventListener('click', function (e) {
        var b = e.target.closest('button'); if (!b) return;
        sl.querySelectorAll('button').forEach(function (x) { x.classList.toggle('is-active', x === b); });
        priceEl.textContent = 'от ' + rub(bySeries[b.dataset.s]);
        renderSpecs(b.dataset.s);
      });
    }

    var rows = [['Внешняя панель', p.panels && p.panels.outer], ['Внутренняя панель', p.panels && p.panels.inner],
      ['Стиль', p.style.join(', ')], ['Покрытие', p.coating.join(', ')], ['Окно', p.window.join(', ')], ['Серия', p.series.join(' / ')]];
    var paramsEl = document.querySelector('.js-params');
    paramsEl.innerHTML = rows.filter(function (r) { return r[1]; })
      .map(function (r) { return '<dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd>'; }).join('');
    paramsEl.hidden = !paramsEl.innerHTML; // у части моделей параметров нет — не показываем пустой блок

    // характеристики: общие для серии (92УТ, 100УТ) + собственные у модели, если есть
    var specsEl = document.querySelector('.js-specs');
    var specSeries = (p.specSeries || []).filter(function (k) { return data.seriesSpecs && data.seriesSpecs[k]; });
    function row(s) { return '<div class="specs__row"><dt>' + esc(s.title) + '</dt><dd>' + esc(s.value) + '</dd></div>'; }
    function renderSpecs(seriesNum) {
      var key = specSeries.filter(function (k) { return k.indexOf(seriesNum) === 0; })[0] || specSeries[0];
      var own = {};
      p.specs.forEach(function (s) { own[s.title] = s; });
      // строки модели точнее серийных: одноимённые заменяем, остальные добавляем в конец
      var list = (key ? data.seriesSpecs[key].rows : []).map(function (s) { var o = own[s.title]; if (o) delete own[s.title]; return o || s; })
        .concat(p.specs.filter(function (s) { return own[s.title]; }));
      if (!list.length) {
        specsEl.innerHTML = '<div class="specs-empty"><b>Характеристики уточняйте у&nbsp;менеджера</b>Подскажем толщину полотна, утепление, замки и&nbsp;фурнитуру для этой модели — оставьте заявку или позвоните.</div>';
        return;
      }
      var tabs = specSeries.length > 1 ? '<div class="specs-tabs">' + specSeries.map(function (k) {
        return '<button type="button" class="' + (k === key ? 'is-active' : '') + '" data-k="' + k + '">Серия ' + k + '</button>';
      }).join('') + '</div>' : (key ? '<p class="specs-note">Серия ' + key + '</p>' : '');
      specsEl.innerHTML = tabs + '<dl class="specs">' + list.map(row).join('') + '</dl>';
    }
    specsEl.addEventListener('click', function (e) {
      var b = e.target.closest('.specs-tabs button'); if (b) renderSpecs(b.dataset.k);
    });
    renderSpecs(series[0] || '');

    // похожие: из того же раздела, сначала той же стилистики
    var similar = data.products.filter(function (x) { return x.id !== p.id && x.cats.indexOf(p.cats[0]) !== -1; })
      .sort(function (a, b) { return (b.style[0] === p.style[0]) - (a.style[0] === p.style[0]); }).slice(0, 12);
    document.querySelector('.js-similar').innerHTML = similar.map(card).join('');
    similarArrows();
    if (cat) document.querySelector('.js-similar-all').href = 'catalog.html?cat=' + cat.slug;
  }

  /* ---------- Страница межкомнатной двери (Aurum) ---------- */
  function initInterior(p, data) {
    if (p.sale) { // у моделей без скидки кнопки остаются «Получить подбор двери»
      saleSticky(p.title);
      toSaleButton(document.querySelector('.model__actions [data-open-form="model"]'), 'Получить скидку 40%', p.title);
    }
    var cat = data.categories.filter(function (c) { return c.slug === p.cats[0]; })[0];
    document.title = 'Межкомнатная дверь Aurum Doors ' + p.title + ' — Стальная линия';
    var kicker = q('.js-kicker');
    kicker.textContent = 'Межкомнатная дверь Aurum Doors'; kicker.hidden = false;
    document.querySelector('.js-crumbs').innerHTML = '<a href="../">Главная</a><span>/</span><a href="catalog.html?cat=mezhkom">Межкомнатные двери</a><span>/</span>' +
      (cat ? '<a href="catalog.html?cat=' + cat.slug + '">' + esc(cat.name) + '</a><span>/</span>' : '') + '<span>' + esc(p.title) + '</span>';
    document.querySelector('.js-title').textContent = p.title;
    document.querySelector('.js-tags').innerHTML = '<span class="tag tag--blue">Коллекция ' + esc(p.collectionName) + '</span>' +
      (p.sale ? '<span class="tag tag--sale">Акция −40%</span>' : '') + (p.inStock ? '<span class="tag tag--blue">В наличии</span>' : '');

    // цена: за полотно и за комплект (полотно + коробка + наличники)
    document.querySelector('.js-price').innerHTML = p.price ? 'от ' + rub(salePrice(p)) + (p.sale ? ' <s>' + rub(p.price) + '</s>' : '') + ' <small>за полотно</small>' :
      p.priceKit ? 'от ' + rub(p.priceKit) + ' <small>за комплект</small>' : 'Цена по запросу';
    var kit = q('.js-kit');
    if (p.price && p.priceKit) { kit.hidden = false; kit.innerHTML = 'Комплект от <b>' + rub(saleKit(p)) + '</b>' + (p.sale ? ' <s>' + rub(p.priceKit) + '</s>' : '') + ' — полотно, коробка и наличники'; }
    q('.js-note').textContent = (p.sale ? 'Распродажа склада в Екатеринбурге: скидка 40% на полотна коллекции Кобальт. ' : '') +
      (p.notes[0] ? p.notes[0].replace(/^\*\s*/, '') + '. ' : '') + 'Итог зависит от размера, стекла и фурнитуры.';
    q('.js-perks').hidden = true; // пункты про входные двери здесь не подходят

    // фото и цвета: у каждого цвета своё фото двери
    var photo = document.querySelector('.js-photo-img');
    photo.parentNode.classList.toggle('is-scene', !!p.scene); // скрытые двери: фото в интерьере, а не дверь на белом
    var thumbs = document.querySelector('.js-thumbs');
    thumbs.innerHTML = '';
    var withPhoto = p.colors.filter(function (c) { return c.photo; });
    var start = withPhoto[0] || p.colors[0];
    function showColor(c) {
      photo.src = (c && c.photo) || p.photos[0] || '';
      photo.alt = 'Межкомнатная дверь ' + p.title + (c ? ', цвет ' + c.name : '');
      q('.js-color-name').textContent = c ? c.name + (c.surcharge ? ' · +10%' : '') : '';
      var ci = p.colors.indexOf(c); // номера цветов на страницах Aurum повторяются — различаем по порядку
      colorsEl.querySelectorAll('button').forEach(function (b, i) { var on = i === ci; b.classList.toggle('is-active', on); b.setAttribute('aria-checked', on); });
    }
    var colorsEl = q('.js-colors');
    if (p.colors.length) {
      q('.js-colors-wrap').hidden = false;
      colorsEl.innerHTML = p.colors.map(function (c, i) {
        return '<button type="button" role="radio" aria-checked="false" data-i="' + i + '" title="' + esc(c.name) + '" aria-label="' + esc(c.name) + '"' +
          ' style="background-image:url(' + esc(c.swatch) + ')"></button>';
      }).join('');
      colorsEl.addEventListener('click', function (e) {
        var b = e.target.closest('button'); if (!b) return;
        showColor(p.colors[+b.dataset.i]);
      });
    }
    if (start) showColor(start);
    else {
      // эмаль: цвет любой по RAL, вместо кружков — подпись; фото двери и палитра — миниатюрами
      if (p.colorNote) { q('.js-colors-wrap').hidden = false; q('.js-color-name').textContent = p.colorNote.replace(/^Любой цвет/, 'любой'); }
      var showPhoto = function (i) {
        photo.src = p.photos[i] || ''; photo.alt = 'Межкомнатная дверь ' + p.title + (i ? ', палитра цветов' : '');
        thumbs.querySelectorAll('.model__thumb').forEach(function (t, j) { t.classList.toggle('is-active', i === j); });
      };
      if (p.photos.length > 1) {
        thumbs.innerHTML = p.photos.map(function (src, i) { return '<button class="model__thumb" type="button" aria-label="Фото ' + (i + 1) + '"><img src="' + esc(src) + '" alt=""></button>'; }).join('');
        thumbs.querySelectorAll('.model__thumb').forEach(function (t, i) { t.addEventListener('click', function () { showPhoto(i); }); });
      }
      showPhoto(0);
    }

    var view = document.querySelector('.js-photo-view');
    document.querySelector('.js-photo').addEventListener('click', function () {
      document.querySelector('.js-photo-view-img').src = photo.src;
      view.showModal();
    });
    document.querySelector('.js-photo-close').addEventListener('click', function () { view.close(); });
    view.addEventListener('click', function (e) { if (e.target === view) view.close(); });

    // коротко под ценой
    var spec = function (t) { return (p.specs.filter(function (s) { return s.title === t; })[0] || {}).value; };
    var rows = [['Коллекция', p.collectionName], ['Стиль', p.style.join(', ')], ['Толщина полотна', spec('Толщина полотна')],
      ['Стекло и вставки', p.glass.join(', ')], ['Размеры', p.sizes]];
    var paramsEl = document.querySelector('.js-params');
    paramsEl.innerHTML = rows.filter(function (r) { return r[1]; }).map(function (r) { return '<dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd>'; }).join('');
    paramsEl.hidden = !paramsEl.innerHTML;

    // характеристики
    var list = p.specs.filter(function (s) { return s.title !== 'Стиль'; });
    document.querySelector('.js-specs').innerHTML = list.length
      ? (p.desc ? '<p class="specs-lead">' + esc(p.desc) + '</p>' : '') + '<dl class="specs specs--text">' + list.map(function (s) { return '<div class="specs__row"><dt>' + esc(s.title) + '</dt><dd>' + esc(s.value) + '</dd></div>'; }).join('') + '</dl>'
      : (p.desc ? '<p class="specs-lead">' + esc(p.desc) + '</p>' : '<div class="specs-empty"><b>Характеристики уточняйте у&nbsp;менеджера</b>Подскажем размеры, стекло и&nbsp;фурнитуру — оставьте заявку или позвоните.</div>');

    // о фабрике — после характеристик
    q('.js-specs').insertAdjacentHTML('beforeend', '<div class="about-maker"><b>О фабрике</b><p>' + ABOUT_AURUM + '</p></div>');

    // погонаж
    if (p.molding.length) {
      q('.js-molding-wrap').hidden = false;
      // погонаж по группам (у эмали: коробочный брус, наличники, капители)
      var mgroups = [];
      p.molding.forEach(function (m) { if (mgroups.indexOf(m.group) === -1) mgroups.push(m.group); });
      q('.js-molding').innerHTML = mgroups.map(function (g) {
        return (g ? '<h3 class="molding__group">' + esc(g) + '</h3>' : '') + '<div class="molding">' + p.molding.filter(function (m) { return m.group === g; }).map(function (m) {
          return '<figure class="molding__item"><span class="molding__media">' + (m.img ? '<img src="' + esc(m.img) + '" alt="" loading="lazy">' : '') + '</span>' +
            '<figcaption><b>' + esc(m.name) + '</b>' + (m.size ? '<span>' + esc(m.size) + ' мм</span>' : '') + '</figcaption></figure>';
        }).join('') + '</div>';
      }).join('');
    }

    // похожие: из той же коллекции
    var similar = data.products.filter(function (x) { return x.id !== p.id && isInterior(x) && x.collection === p.collection; }).slice(0, 12);
    if (similar.length < 8) similar = similar.concat(data.products.filter(function (x) { return isInterior(x) && x.id !== p.id && x.collection !== p.collection; }).slice(0, 8 - similar.length));
    document.querySelector('.js-similar').innerHTML = similar.map(card).join('');
    similarArrows();
    document.querySelector('.js-similar-all').href = 'catalog.html?cat=' + (cat ? cat.slug : 'mezhkom');
  }
})();
