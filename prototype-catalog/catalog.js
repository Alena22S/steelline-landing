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
    if (model) b.dataset.model = model;
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
  function card(p) {
    if (isInterior(p)) return cardInterior(p);
    var photos = p.photos.slice(0, 2).map(function (src, i) {
      return '<img class="pcard__photo" src="' + esc(src) + '" alt="' + (i ? '' : 'Входная дверь ' + esc(p.title)) + '" loading="lazy">';
    }).join('');
    return '<a class="pcard" href="model.html?id=' + p.id + '">' +
      '<div class="pcard__media">' + photos +
      (p.special.length ? '<span class="pcard__badge">Спецпредложение</span>' : '') +
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

  Promise.all([
    fetch('data/catalog.json?v=5').then(function (r) { return r.json(); }),
    fetch('data/aurum.json?v=5').then(function (r) { return r.json(); }).catch(function () { return { categories: [], products: [] }; })
  ]).then(function (res) {
    var data = res[0], aurum = res[1];
    data.products.forEach(function (p) { p.kind = 'entry'; });
    data.products = data.products.concat(aurum.products);
    data.categories = data.categories.concat(aurum.categories);
    if (document.getElementById('cat')) initCatalog(data);
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
    var nEntry = data.products.filter(function (p) { return !isInterior(p); }).length;
    q('.js-kinds').innerHTML =
      '<a class="cat-kind' + (interior ? '' : ' is-active') + '" href="catalog.html"' + (interior ? '' : ' aria-current="page"') + '>Входные двери <span>' + nEntry + '</span></a>' +
      '<a class="cat-kind' + (interior ? ' is-active' : '') + '" href="catalog.html?cat=mezhkom"' + (interior ? ' aria-current="page"' : '') + '>Межкомнатные двери <span>' + (data.products.length - nEntry) + '</span></a>';
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
    var more = document.querySelector('.js-more');
    var empty = document.querySelector('.js-empty');

    function render() {
      var list = base.filter(function (p) { return match(p); });
      var pr = function (p) { return isInterior(p) ? (salePrice(p) || p.priceKit || 0) : p.price; };
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
      var list = (key ? data.seriesSpecs[key].rows : []).concat(p.specs);
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
      .sort(function (a, b) { return (b.style[0] === p.style[0]) - (a.style[0] === p.style[0]); }).slice(0, 4);
    document.querySelector('.js-similar').innerHTML = similar.map(card).join('');
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
    var similar = data.products.filter(function (x) { return x.id !== p.id && isInterior(x) && x.collection === p.collection; }).slice(0, 4);
    if (similar.length < 4) similar = similar.concat(data.products.filter(function (x) { return isInterior(x) && x.id !== p.id && x.collection !== p.collection; }).slice(0, 4 - similar.length));
    document.querySelector('.js-similar').innerHTML = similar.map(card).join('');
    document.querySelector('.js-similar-all').href = 'catalog.html?cat=' + (cat ? cat.slug : 'mezhkom');
  }
})();
