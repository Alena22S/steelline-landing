/* Прототип «Наши работы»: проекты из data/portfolio.json, фильтры по городу и типу, просмотр проекта */
(function () {
  var PAGE = 24;
  var REGIONS = ['Екатеринбург', 'Свердловская область', 'Тюмень', 'Беларусь', 'Другие города'];
  var TYPES = ['Для дома', 'Для квартиры', 'Хаски', 'Нестандарт и индивидуальный проект'];

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function plural(n, one, few, many) {
    var m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
  }

  fetch('data/portfolio.json?v=1').then(function (r) { return r.json(); }).then(init);

  function init(data) {
    var all = data.projects;
    var state = { region: '', type: '', shown: PAGE };
    var list = all;

    document.querySelector('.js-port-lead').textContent = data.intro;
    var cities = {};
    all.forEach(function (p) { cities[p.city] = 1; });
    document.querySelector('.js-port-stats').innerHTML =
      '<li><b>' + all.length + '</b>' + plural(all.length, 'установленная дверь', 'установленные двери', 'установленных дверей') + ' в&nbsp;портфолио</li>' +
      '<li><b>' + Object.keys(cities).length + '</b>' + plural(Object.keys(cities).length, 'город', 'города', 'городов') + ' — от&nbsp;Екатеринбурга до&nbsp;Нью-Йорка</li>' +
      '<li><b>2 года</b>гарантии на&nbsp;монтаж собственной бригадой</li>';

    function chips(el, key, values) {
      function count(v) {
        return all.filter(function (p) {
          var okR = key === 'region' ? (!v || p.region === v) : (!state.region || p.region === state.region);
          var okT = key === 'type' ? (!v || p.tags.indexOf(v) !== -1) : (!state.type || p.tags.indexOf(state.type) !== -1);
          return okR && okT;
        }).length;
      }
      el.innerHTML = [''].concat(values).map(function (v) {
        var n = count(v);
        return '<button type="button" class="cat-tab' + (state[key] === v ? ' is-active' : '') + '" data-v="' + esc(v) + '"' + (n ? '' : ' disabled') + '>' +
          (v || (key === 'region' ? 'Все города' : 'Все двери')) + ' <span>' + n + '</span></button>';
      }).join('');
    }

    var grid = document.querySelector('.js-port-grid');
    var more = document.querySelector('.js-port-more');

    function card(p, i) {
      var photos = p.photos.slice(0, 2).map(function (src, k) {
        return '<img class="port-card__photo" src="' + esc(src) + '" alt="' + (k ? '' : esc(p.title + ', ' + p.city)) + '" loading="lazy">';
      }).join('');
      return '<button type="button" class="port-card" data-i="' + i + '">' +
        '<span class="port-card__media">' + photos + (p.photos.length > 1 ? '<span class="port-card__more">' + p.photos.length + ' фото</span>' : '') + '</span>' +
        '<span class="port-card__city">' + esc(p.city) + '</span>' +
        '<span class="port-card__title">' + esc(p.title) + '</span></button>';
    }

    function render() {
      list = all.filter(function (p) {
        return (!state.region || p.region === state.region) && (!state.type || p.tags.indexOf(state.type) !== -1);
      });
      chips(document.querySelector('.js-port-regions'), 'region', REGIONS);
      chips(document.querySelector('.js-port-types'), 'type', TYPES);
      grid.innerHTML = list.slice(0, state.shown).map(card).join('');
      more.hidden = list.length <= state.shown;
      more.textContent = 'Показать ещё ' + Math.min(PAGE, list.length - state.shown);
      document.querySelector('.js-port-count').textContent = 'Найдено ' + list.length + ' ' + plural(list.length, 'проект', 'проекта', 'проектов');
    }

    document.querySelector('.js-port-regions').addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b || b.disabled) return;
      state.region = b.dataset.v; state.shown = PAGE; render();
    });
    document.querySelector('.js-port-types').addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b || b.disabled) return;
      state.type = b.dataset.v; state.shown = PAGE; render();
    });
    more.addEventListener('click', function () { state.shown += PAGE; render(); });

    /* Просмотр проекта */
    var view = document.querySelector('.js-port-view');
    var img = document.querySelector('.js-pv-img');
    var thumbs = document.querySelector('.js-pv-thumbs');
    var modelLink = document.querySelector('.js-pv-model');
    var cur = 0;
    function show(i, k) {
      cur = (i + list.length) % list.length;
      var p = list[cur];
      img.src = p.photos[k || 0];
      img.alt = p.title + ', ' + p.city;
      document.querySelector('.js-pv-city').textContent = p.city + (p.country !== 'Россия' && p.city !== p.country ? ', ' + p.country : '');
      document.querySelector('.js-pv-title').textContent = p.title;
      thumbs.innerHTML = p.photos.length > 1 ? p.photos.map(function (src, j) {
        return '<button type="button" class="' + (j === (k || 0) ? 'is-active' : '') + '" data-k="' + j + '"><img src="' + esc(src) + '" alt=""></button>';
      }).join('') : '';
      modelLink.hidden = !p.model;
      if (p.model) { modelLink.href = 'model.html?id=' + p.model.id; modelLink.textContent = 'Модель «' + p.model.title + '» в каталоге'; }
      document.querySelector('.js-pv-count').textContent = (cur + 1) + ' из ' + list.length;
    }
    grid.addEventListener('click', function (e) {
      var c = e.target.closest('.port-card'); if (!c) return;
      show(+c.dataset.i); view.showModal(); document.body.classList.add('has-modal');
      window.siteGoal && window.siteGoal('portfolio_open');
    });
    thumbs.addEventListener('click', function (e) { var b = e.target.closest('button'); if (b) show(cur, +b.dataset.k); });
    document.querySelector('.js-pv-prev').addEventListener('click', function () { show(cur - 1); });
    document.querySelector('.js-pv-next').addEventListener('click', function () { show(cur + 1); });
    document.querySelector('.js-pv-close').addEventListener('click', function () { view.close(); });
    view.addEventListener('click', function (e) { if (e.target === view) view.close(); });
    view.addEventListener('close', function () { document.body.classList.remove('has-modal'); });
    view.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') show(cur - 1);
      if (e.key === 'ArrowRight') show(cur + 1);
    });
    // «Хочу такую дверь» открывает общую форму заявки — окно просмотра закрываем, чтобы форма была сверху
    view.querySelector('[data-open-form]').addEventListener('click', function () { view.close(); });

    render();
  }
})();
