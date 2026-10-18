/* Прототип каталога: раздел (catalog.html?cat=…) и страница модели (model.html?id=…) на данных из data/catalog.json */
(function () {
  var PAGE = 24;
  var GROUPS = [
    { key: 'place', title: 'Назначение' },
    { key: 'style', title: 'Стиль' },
    { key: 'coating', title: 'Покрытие' },
    { key: 'window', title: 'Окно' },
    { key: 'series', title: 'Серия', label: function (v) { return 'Серия ' + v; } }
  ];

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

  fetch('data/catalog.json?v=2').then(function (r) { return r.json(); }).then(function (data) {
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
      kvartira: { slug: 'kvartira', name: 'Двери в квартиру', lead: 'Надёжные входные двери для квартиры: классика и современный дизайн, умные замки.' }
    };
    var cat = data.categories.filter(function (c) { return c.slug === catSlug; })[0] || PARENTS[catSlug];
    var base = !cat ? data.products : data.products.filter(function (p) {
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
    // разделы
    var tabs = '<a class="cat-tab' + (cat ? '' : ' is-active') + '" href="catalog.html">Все модели <span>' + data.products.length + '</span></a>';
    ['dom', 'kvartira'].forEach(function (k) {
      var n = data.products.filter(function (p) { return p.cats.some(function (c) { return c.indexOf(k + '/') === 0; }); }).length;
      tabs += '<a class="cat-tab' + (cat && cat.slug === k ? ' is-active' : '') + '" href="catalog.html?cat=' + k + '">' + PARENTS[k].name + ' <span>' + n + '</span></a>';
    });
    data.categories.forEach(function (c) {
      tabs += '<a class="cat-tab' + (cat && cat.slug === c.slug ? ' is-active' : '') + '" href="catalog.html?cat=' + c.slug + '">' + esc(c.name) + ' <span>' + c.count + '</span></a>';
    });
    document.querySelector('.js-tabs').innerHTML = tabs;

    // фильтры
    var state = { special: false, sort: 'popular', shown: PAGE };
    GROUPS.forEach(function (g) { state[g.key] = []; });
    var groupsEl = document.querySelector('.js-filter-groups');
    var html = '';
    GROUPS.forEach(function (g) {
      var vals = {};
      base.forEach(function (p) { p[g.key].forEach(function (v) { vals[v] = 1; }); });
      var list = Object.keys(vals).sort();
      if (list.length < 2) return; // нечего выбирать
      html += '<div class="fgroup" role="group" aria-label="' + g.title + '"><p class="fgroup__title">' + g.title + '</p>';
      list.forEach(function (v) {
        html += '<label class="fcheck"><input type="checkbox" data-key="' + g.key + '" value="' + esc(v) + '">' +
          esc(g.label ? g.label(v) : v) + '<span data-count></span></label>';
      });
      html += '</div>';
    });
    if (base.some(function (p) { return p.special.length; })) {
      html += '<div class="fgroup"><label class="fcheck"><input type="checkbox" data-key="special">Только спецпредложения<span data-count></span></label></div>';
    }
    groupsEl.innerHTML = html;

    function match(p, skip) {
      if (state.special && skip !== 'special' && !p.special.length) return false;
      return GROUPS.every(function (g) {
        if (g.key === skip || !state[g.key].length) return true;
        return p[g.key].some(function (v) { return state[g.key].indexOf(v) !== -1; });
      });
    }

    var grid = document.querySelector('.js-grid');
    var more = document.querySelector('.js-more');
    var empty = document.querySelector('.js-empty');

    function render() {
      var list = base.filter(function (p) { return match(p); });
      if (state.sort === 'price-asc') list.sort(function (a, b) { return a.price - b.price; });
      if (state.sort === 'price-desc') list.sort(function (a, b) { return b.price - a.price; });
      if (state.sort === 'name') list.sort(function (a, b) { return a.title.localeCompare(b.title, 'ru'); });

      grid.innerHTML = list.slice(0, state.shown).map(card).join('');
      grid.hidden = !list.length;
      empty.hidden = !!list.length;
      more.hidden = list.length <= state.shown;
      more.textContent = 'Показать ещё ' + Math.min(PAGE, list.length - state.shown);
      document.querySelector('.js-count').textContent = 'Найдено ' + list.length + ' ' + plural(list.length, 'модель', 'модели', 'моделей');

      // счётчики у вариантов: сколько будет, если отметить
      groupsEl.querySelectorAll('input').forEach(function (inp) {
        var key = inp.dataset.key, n;
        if (key === 'special') n = base.filter(function (p) { return match(p, 'special') && p.special.length; }).length;
        else n = base.filter(function (p) { return match(p, key) && p[key].indexOf(inp.value) !== -1; }).length;
        var label = inp.closest('.fcheck');
        label.querySelector('[data-count]').textContent = n;
        label.classList.toggle('is-zero', !n && !inp.checked);
      });
      var active = GROUPS.reduce(function (s, g) { return s + state[g.key].length; }, 0) + (state.special ? 1 : 0);
      var badge = document.querySelector('.js-active-count');
      badge.hidden = !active; badge.textContent = active;
      document.querySelectorAll('.cat-filters__reset').forEach(function (b) { b.disabled = !active; });
      document.querySelector('.cat-filters__apply').textContent = 'Показать ' + list.length + ' ' + plural(list.length, 'модель', 'модели', 'моделей');
    }

    groupsEl.addEventListener('change', function (e) {
      var inp = e.target; var key = inp.dataset.key;
      if (key === 'special') state.special = inp.checked;
      else {
        var arr = state[key]; var i = arr.indexOf(inp.value);
        if (inp.checked && i === -1) arr.push(inp.value);
        if (!inp.checked && i !== -1) arr.splice(i, 1);
      }
      state.shown = PAGE; render();
    });
    document.querySelector('.js-sort').addEventListener('change', function (e) { state.sort = e.target.value; render(); });
    more.addEventListener('click', function () { state.shown += PAGE; render(); });
    document.querySelectorAll('.js-reset').forEach(function (b) {
      b.addEventListener('click', function () {
        GROUPS.forEach(function (g) { state[g.key] = []; }); state.special = false; state.shown = PAGE;
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
      });
    }

    var rows = [['Стиль', p.style.join(', ')], ['Покрытие', p.coating.join(', ')], ['Окно', p.window.join(', ')], ['Серия', p.series.join(' / ')]];
    var paramsEl = document.querySelector('.js-params');
    paramsEl.innerHTML = rows.filter(function (r) { return r[1]; })
      .map(function (r) { return '<dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd>'; }).join('');
    paramsEl.hidden = !paramsEl.innerHTML; // у части моделей параметров нет — не показываем пустой блок

    document.querySelector('.js-specs').innerHTML = p.specs.length
      ? '<dl class="specs">' + p.specs.map(function (s) { return '<div class="specs__row"><dt>' + esc(s.title) + '</dt><dd>' + esc(s.value) + '</dd></div>'; }).join('') + '</dl>'
      : '<div class="specs-empty"><b>Здесь будут характеристики модели</b>Толщина полотна, утепление, контуры уплотнения, замки, шумоизоляция — заполним по&nbsp;данным производителя. В&nbsp;прототипе этот блок показывает, где они появятся.</div>';

    // похожие: из того же раздела, сначала той же стилистики
    var similar = data.products.filter(function (x) { return x.id !== p.id && x.cats.indexOf(p.cats[0]) !== -1; })
      .sort(function (a, b) { return (b.style[0] === p.style[0]) - (a.style[0] === p.style[0]); }).slice(0, 4);
    document.querySelector('.js-similar').innerHTML = similar.map(card).join('');
    if (cat) document.querySelector('.js-similar-all').href = 'catalog.html?cat=' + cat.slug;
  }
})();
