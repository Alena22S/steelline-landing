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

  fetch('data/portfolio.json?v=2').then(function (r) { return r.json(); }).then(init);

  function init(data) {
    var all = data.projects;
    var state = { region: '', type: '', shown: PAGE };
    var list = all;

    document.querySelector('.js-port-lead').textContent = data.intro;
    var cities = {};
    all.forEach(function (p) { cities[p.city] = 1; });
    var nc = Object.keys(cities).length;
    var badgesEl = document.querySelector('.js-port-badges');
    // бейджи-факты с иконками
    if (badgesEl) badgesEl.innerHTML =
      badge('door', '<path pathLength="1" d="M4 21h16"/><path pathLength="1" d="M6 21V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v17"/><g class="port-badge__leaf"><path pathLength="1" d="M7 21V4h7.5v17"/><path pathLength="1" d="M12.5 12.5v.01"/></g>', all.length, plural(all.length, 'установленная дверь', 'установленные двери', 'установленных дверей')) +
      badge('pin', '<g class="port-badge__pin"><path pathLength="1" d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21Z"/><circle pathLength="1" cx="12" cy="9.5" r="2.5"/></g>', nc, plural(nc, 'город', 'города', 'городов')) +
      badge('shield', '<path pathLength="1" d="M12 3 5 6v5.5c0 4.3 3 8 7 9.5 4-1.5 7-5.2 7-9.5V6l-7-3Z"/><path class="port-badge__check" pathLength="1" d="m9 12 2 2 4-4"/>', '2 года', 'гарантии на&nbsp;монтаж');
    function badge(kind, icon, num, text) {
      return '<li class="port-badge port-badge--' + kind + '"><span class="port-badge__icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + icon + '</svg></span>' +
        '<span><b>' + num + '</b> ' + text + '</span></li>';
    }

    function count(key, v) {
      return all.filter(function (p) {
        var okR = key === 'region' ? (!v || p.region === v) : (!state.region || p.region === state.region);
        var okT = key === 'type' ? (!v || p.tags.indexOf(v) !== -1) : (!state.type || p.tags.indexOf(state.type) !== -1);
        return okR && okT;
      }).length;
    }

    // Города — чипсы, как разделы каталога
    function tabs(el) {
      el.innerHTML = [''].concat(REGIONS).map(function (v) {
        var n = count('region', v);
        return '<button type="button" class="cat-tab' + (state.region === v ? ' is-active' : '') + '" aria-pressed="' + (state.region === v) + '" data-v="' + esc(v) + '"' + (n ? '' : ' disabled') + '>' +
          (v || 'Все города') + '<span>' + n + '</span></button>';
      }).join('');
    }

    // Вид двери — выпадашка в стиле сортировки каталога; на телефоне CSS показывает системный <select>
    var tSelect = document.querySelector('.js-port-type');
    var tBtn = document.querySelector('.js-port-type-btn');
    var tList = document.querySelector('.js-port-type-list');
    // если браузер взял из кэша старую страницу без выпадашки — пропускаем её, карточки всё равно рисуем
    var tWrap = tBtn && tBtn.parentNode;
    var tActive = 0;
    function typeLabel(v) { return v || 'Все двери'; }
    function typeMenu() {
      if (!tWrap) return;
      var vals = [''].concat(TYPES);
      tSelect.innerHTML = vals.map(function (v) {
        var n = count('type', v);
        return '<option value="' + esc(v) + '"' + (state.type === v ? ' selected' : '') + (n ? '' : ' disabled') + '>' + typeLabel(v) + ' (' + n + ')</option>';
      }).join('');
      tList.innerHTML = vals.map(function (v) {
        var n = count('type', v);
        return '<li class="csel__opt' + (n ? '' : ' is-disabled') + '" role="option" data-v="' + esc(v) + '" aria-selected="' + (state.type === v) + '"' + (n ? '' : ' aria-disabled="true"') + '>' +
          typeLabel(v) + '<span>' + n + '</span></li>';
      }).join('');
      tBtn.textContent = typeLabel(state.type);
    }
    function tOpts() { return tList.querySelectorAll('.csel__opt'); }
    function tHighlight(i) {
      var o = tOpts(); tActive = (i + o.length) % o.length;
      o.forEach(function (li, j) { li.classList.toggle('is-active', j === tActive); });
    }
    function tOpen() {
      tList.hidden = false; tWrap.classList.add('is-open'); tBtn.setAttribute('aria-expanded', 'true');
      tHighlight(Math.max(0, [''].concat(TYPES).indexOf(state.type))); tList.focus();
    }
    function tClose(focusBtn) {
      tList.hidden = true; tWrap.classList.remove('is-open'); tBtn.setAttribute('aria-expanded', 'false');
      if (focusBtn) tBtn.focus();
    }
    function setType(v) { state.type = v; state.shown = PAGE; render(); }
    function tChoose(li) {
      if (!li || li.classList.contains('is-disabled')) return;
      tClose(true); if (li.dataset.v !== state.type) setType(li.dataset.v);
    }
    if (tWrap) {
    tBtn.addEventListener('click', function () { tList.hidden ? tOpen() : tClose(); });
    tBtn.addEventListener('keydown', function (e) { if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); tOpen(); } });
    tList.addEventListener('click', function (e) { tChoose(e.target.closest('.csel__opt')); });
    tList.addEventListener('mousemove', function (e) { var li = e.target.closest('.csel__opt'); if (li) tHighlight(Array.prototype.indexOf.call(tOpts(), li)); });
    tList.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); tHighlight(tActive + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); tHighlight(tActive - 1); }
      else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); tChoose(tOpts()[tActive]); }
      else if (e.key === 'Escape' || e.key === 'Tab') { tClose(e.key === 'Escape'); }
    });
    document.addEventListener('click', function (e) { if (!tWrap.contains(e.target) && !tList.hidden) tClose(); });
    tSelect.addEventListener('change', function () { setType(tSelect.value); });
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
      if (regionsEl) tabs(regionsEl);
      typeMenu();
      grid.innerHTML = list.slice(0, state.shown).map(card).join('');
      more.hidden = list.length <= state.shown;
      more.textContent = 'Показать ещё ' + Math.min(PAGE, list.length - state.shown);
      document.querySelector('.js-port-count').textContent = 'Найдено ' + list.length + ' ' + plural(list.length, 'проект', 'проекта', 'проектов');
    }

    var regionsEl = document.querySelector('.js-port-regions');
    regionsEl && regionsEl.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b || b.disabled) return;
      state.region = b.dataset.v; state.shown = PAGE; render();
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
      if (p.model) { modelLink.href = p.model.url ? p.model.url + '/' : 'model.html?id=' + p.model.id; modelLink.textContent = 'Модель «' + p.model.title + '» в каталоге'; }
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
