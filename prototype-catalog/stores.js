/* Прототип «Наши магазины»: салоны из data/stores.json, фильтр по городу, фото салона, карта */
(function () {
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function plural(n, one, few, many) {
    var m10 = n % 10, m100 = n % 100;
    if (m10 === 1 && m100 !== 11) return one;
    if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
    return many;
  }

  fetch('data/stores.json?v=5').then(function (r) { return r.json(); }).then(init);

  function init(data) {
    var all = data.stores;
    var cities = [];
    all.forEach(function (s) { if (cities.indexOf(s.city) === -1) cities.push(s.city); });
    var state = { city: '', region: '' };
    try { var h = decodeURIComponent(location.hash.slice(1)); if (cities.indexOf(h) !== -1) state.city = h; } catch (e) {}

    var badgesEl = document.querySelector('.js-shops-badges');
    if (badgesEl) badgesEl.innerHTML =
      badge('pin', '<g class="port-badge__pin"><path pathLength="1" d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21Z"/><circle pathLength="1" cx="12" cy="9.5" r="2.5"/></g>', all.length, plural(all.length, 'салон', 'салона', 'салонов')) +
      badge('door', '<path pathLength="1" d="M4 21h16"/><path pathLength="1" d="M6 21V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v17"/><g class="port-badge__leaf"><path pathLength="1" d="M7 21V4h7.5v17"/><path pathLength="1" d="M12.5 12.5v.01"/></g>', cities.length, plural(cities.length, 'город', 'города', 'городов'));
    function badge(kind, icon, num, text) {
      return '<li class="port-badge port-badge--' + kind + '"><span class="port-badge__icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + icon + '</svg></span>' +
        '<span><b>' + num + '</b> ' + text + '</span></li>';
    }

    var listEl = document.querySelector('.js-shops-list');
    var tabsEl = document.querySelector('.js-shops-regions');

    // Регионы вместо 16 городов: почти в каждом городе по одному салону, а так кнопок меньше и цифры осмысленные
    var REGIONS = [
      { name: 'Екатеринбург и область', cities: ['Екатеринбург', 'Арамиль', 'Нижний Тагил', 'Каменск-Уральский', 'Серов'] },
      { name: 'ХМАО и ЯНАО', cities: ['Сургут', 'Нижневартовск', 'Лангепас', 'Югорск', 'Новый Уренгой'] },
      { name: 'Тюмень', cities: ['Тюмень'] },
      { name: 'Челябинская область', cities: ['Челябинск', 'Миасс'] },
      { name: 'Пермь, Уфа, Курган', cities: ['Пермь', 'Уфа', 'Курган'] }
    ];
    function inRegion(s, r) { return !r || REGIONS.some(function (x) { return x.name === r && x.cities.indexOf(s.city) !== -1; }); }
    // ссылка вида #Тюмень или #Сургут — открываем регион этого города
    if (state.city) {
      var rr = REGIONS.filter(function (x) { return x.cities.indexOf(state.city) !== -1; })[0];
      state.region = rr ? rr.name : '';
      if (rr && rr.cities.length < 2) state.city = '';
    }
    try { var hr = decodeURIComponent(location.hash.slice(1)); if (REGIONS.some(function (x) { return x.name === hr; })) state.region = hr; } catch (e) {}

    // Кнопка региона со стрелкой: открывает список его городов. Выбранный город показывается на самой кнопке.
    var ARROW = '<svg class="cat-tab__arrow" width="12" height="8" viewBox="0 0 12 8" fill="none" aria-hidden="true"><path d="M1 1.5l5 5 5-5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>';
    function count(f) { return all.filter(f).length; }
    function tabs() {
      tabsEl.innerHTML = [{ name: '', cities: [] }].concat(REGIONS).map(function (r) {
        var v = r.name, active = state.region === v;
        var multi = r.cities.length > 1;
        var cityHere = active && state.city && r.cities.indexOf(state.city) !== -1;
        var n = cityHere ? count(function (s) { return s.city === state.city; }) : count(function (s) { return inRegion(s, v); });
        return '<button type="button" class="cat-tab' + (active ? ' is-active' : '') + (multi ? ' has-menu' : '') + '" aria-pressed="' + active + '" data-v="' + esc(v) + '"' +
          (multi ? ' aria-haspopup="listbox" aria-expanded="' + (menuFor === v) + '"' : '') + '>' +
          (cityHere ? esc(state.city) : (v || 'Все города')) + '<span>' + n + '</span>' + (multi ? ARROW : '') + '</button>';
      }).join('');
    }

    var menuEl = document.createElement('ul');
    menuEl.className = 'csel__list shops-menu';
    menuEl.setAttribute('role', 'listbox');
    menuEl.tabIndex = -1;
    menuEl.hidden = true;
    tabsEl.parentNode.appendChild(menuEl);
    var menuFor = null, menuActive = 0;

    function openMenu(btn) {
      var r = REGIONS.filter(function (x) { return x.name === btn.dataset.v; })[0];
      menuFor = r.name;
      var vals = [''].concat(r.cities);
      menuEl.innerHTML = vals.map(function (c) {
        var n = c ? count(function (s) { return s.city === c; }) : count(function (s) { return inRegion(s, r.name); });
        var sel = c ? state.city === c : !state.city;
        return '<li class="csel__opt' + (c ? '' : ' csel__opt--all') + '" role="option" data-c="' + esc(c) + '" aria-selected="' + sel + '">' +
          (c || 'Все города региона') + (n > 1 || !c ? '<span>' + n + '</span>' : '') + '</li>';
      }).join('');
      // под кнопкой (ряд кнопок на телефоне прокручивается — считаем от его положения)
      var bar = tabsEl.parentNode.getBoundingClientRect(), b = btn.getBoundingClientRect();
      menuEl.style.top = (b.bottom - bar.top + 6) + 'px';
      menuEl.style.minWidth = Math.round(b.width) + 'px';  // не уже кнопки, но и не шире своих пунктов
      menuEl.hidden = false;
      menuEl.style.left = Math.max(0, Math.min(b.left - bar.left, bar.width - menuEl.offsetWidth)) + 'px';
      btn.setAttribute('aria-expanded', 'true');
      menuHighlight(Math.max(0, vals.indexOf(state.city)));
      menuEl.focus({ preventScroll: true });
    }
    function closeMenu() {
      if (menuFor === null) return;
      menuEl.hidden = true;
      var b = tabsEl.querySelector('[aria-expanded="true"]');
      if (b) b.setAttribute('aria-expanded', 'false');
      menuFor = null;
    }
    function menuOpts() { return menuEl.querySelectorAll('.csel__opt'); }
    function menuHighlight(i) {
      var o = menuOpts(); menuActive = (i + o.length) % o.length;
      o.forEach(function (li, k) { li.classList.toggle('is-active', k === menuActive); });
    }
    var HOME = ['Екатеринбург', 'Арамиль'];
    function setFilter(region, city) {
      state.region = region; state.city = city || ''; state.all = false;
      var h = state.city || state.region;
      try { history.replaceState(null, '', h ? '#' + encodeURIComponent(h) : location.pathname + location.search); } catch (err) {}
      render();
    }

    tabsEl.addEventListener('click', function (e) {
      var b = e.target.closest('.cat-tab'); if (!b) return;
      var v = b.dataset.v;
      if (b.classList.contains('has-menu')) {
        if (menuFor === v) { closeMenu(); return; }
        closeMenu();
        if (state.region !== v) setFilter(v, '');
        openMenu(tabsEl.querySelector('.cat-tab[data-v="' + v.replace(/"/g, '\\"') + '"]'));
        return;
      }
      closeMenu();
      setFilter(v, '');
    });
    menuEl.addEventListener('click', function (e) {
      var li = e.target.closest('.csel__opt'); if (!li) return;
      var r = menuFor; if (r === null) return; closeMenu(); setFilter(r, li.dataset.c);
    });
    menuEl.addEventListener('mousemove', function (e) {
      var li = e.target.closest('.csel__opt'); if (li) menuHighlight(Array.prototype.indexOf.call(menuOpts(), li));
    });
    menuEl.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); menuHighlight(menuActive + 1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); menuHighlight(menuActive - 1); }
      else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); menuOpts()[menuActive].click(); }
      else if (e.key === 'Escape' || e.key === 'Tab') {
        var v = menuFor; closeMenu();
        if (e.key === 'Escape') { var b = tabsEl.querySelector('.cat-tab[data-v="' + v + '"]'); if (b) b.focus(); }
      }
    });
    // клик снаружи закрывает меню; кнопка, по которой кликнули, к этому моменту уже перерисована — её не считаем «снаружи»
    document.addEventListener('click', function (e) { if (menuFor !== null && e.target.isConnected && !menuEl.contains(e.target) && !tabsEl.contains(e.target)) closeMenu(); });
    tabsEl.addEventListener('scroll', closeMenu, { passive: true });
    window.addEventListener('resize', closeMenu);

    // «Как добраться» — маршрут до метки салона; карта — картинка (без рекламы), по клику открываются Яндекс Карты
    function latlon(s) { var p = s.ll.split(','); return p[1] + ',' + p[0]; }
    function routeUrl(s) { return s.ll ? 'https://yandex.ru/maps/?rtext=~' + latlon(s) + '&rtt=auto' : 'https://yandex.ru/maps/?text=' + encodeURIComponent(s.city + ', ' + s.address); }
    function mapUrl(s) { return 'https://yandex.ru/maps/?ll=' + s.ll + '&z=17&pt=' + s.ll + ',pm2rdl'; }

    function card(s, i) {
      var ph = s.photos || [];
      var thumbs = ph.slice(1, 5).map(function (p, j) {
        var more = j === 3 && ph.length > 5 ? '<span class="shop__more">+' + (ph.length - 5) + '</span>' : '';
        return '<button type="button" class="shop__thumb" data-shop="' + i + '" data-photo="' + (j + 1) + '" aria-label="Фото ' + (j + 2) + '"><img src="' + esc(p) + '" alt="" loading="lazy" decoding="async">' + more + '</button>';
      }).join('');
      var photos = ph.length
        ? '<div class="shop__photos' + (ph.length === 1 ? ' is-single' : '') + '"><button type="button" class="shop__main" data-shop="' + i + '" data-photo="0" aria-label="Смотреть фото салона"><img src="' + esc(ph[0]) + '" alt="' + esc(s.name + ', ' + s.city) + '" loading="lazy" decoding="async"></button>' +
          (thumbs ? '<div class="shop__thumbs">' + thumbs + '</div>' : '') + '</div>'
        : '';
      var phones = s.phones.map(function (p) { return '<a href="tel:' + esc(p.tel) + '">' + esc(p.text) + '</a>'; }).join('');
      var emails = s.emails.map(function (e) { return '<a href="mailto:' + esc(e) + '">' + esc(e) + '</a>'; }).join('');
      return '<article class="shop' + (ph.length ? '' : ' no-photos') + '">' +
        '<div class="shop__info">' +
          '<span class="tag tag--blue shop__city">' + esc(s.city) + '</span>' +
          '<h2 class="shop__name">' + esc(s.name) + '</h2>' +
          '<p class="shop__addr">' + esc(s.address) + (s.where ? '<span>' + esc(s.where) + '</span>' : '') + '</p>' +
          '<dl class="shop__rows">' +
            '<div><dt>Часы работы</dt><dd>' + s.hours.map(esc).join('<br>') + '</dd></div>' +
            '<div><dt>Телефон</dt><dd class="shop__links">' + phones + '</dd></div>' +
            (emails ? '<div><dt>Почта</dt><dd class="shop__links">' + emails + '</dd></div>' : '') +
          '</dl>' +
          (s.rating ? '<iframe class="shop__rating" src="https://yandex.ru/sprav/widget/rating-badge/' + esc(s.rating) + '?type=rating" width="150" height="50" frameborder="0" loading="lazy" title="Рейтинг на Яндекс Картах"></iframe>' : '') +
          '<a class="btn btn--outline btn--outline-soft shop__route" href="' + routeUrl(s) + '" target="_blank" rel="noopener">Как добраться <img src="../assets/icons/arrow-right-dark-3.svg" width="24" height="24" alt=""></a>' +
        '</div>' +
        photos +
        (s.mapImg ? '<div class="shop__map" data-shop-map="' + i + '">' +
          '<button type="button" class="shop__map-live" aria-label="Показать интерактивную карту: ' + esc(s.name) + '"><img src="' + esc(s.mapImg) + '" alt="" loading="lazy" decoding="async">' +
            '<span class="shop__map-hint"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 9l-3 3 3 3M9 5l3-3 3 3M15 19l-3 3-3-3M19 9l3 3-3 3M2 12h20M12 2v20"/></svg>Подвигать карту</span></button>' +
          '<a class="shop__map-open" href="' + mapUrl(s) + '" target="_blank" rel="noopener">Открыть в Яндекс Картах</a>' +
        '</div>' : '') +
      '</article>';
    }

    var shown = [];
    function render() {
      shown = all.filter(function (s) { return inRegion(s, state.region) && (!state.city || s.city === state.city); });
      // «Все города»: сначала только Екатеринбург и Арамиль, остальные салоны — по кнопке
      var rest = 0;
      if (!state.region && !state.all) {
        var full = shown.length;
        shown = shown.filter(function (s) { return HOME.indexOf(s.city) !== -1; });
        rest = full - shown.length;
      }
      listEl.innerHTML = shown.map(card).join('') + (rest
        ? '<button type="button" class="btn btn--outline btn--lg cat-more shops-more js-shops-more">Салоны в других городах<span>' + rest + '</span></button>'
        : '');
      tabs();
    }

    listEl.addEventListener('click', function (e) {
      if (!e.target.closest('.js-shops-more')) return;
      var n = shown.length;
      state.all = true; render();
      // переводим фокус на первый из открытых салонов
      var first = listEl.querySelectorAll('.shop')[n];
      if (first) first.setAttribute('tabindex', '-1'), first.focus({ preventScroll: true });
    });

    // Картинка карты → по нажатию живая карта Яндекса только этого салона (страница не грузит 21 виджет сразу)
    function widgetUrl(s) {
      if (s.map) return 'https://yandex.ru/map-widget/v1/?um=constructor%3A' + s.map + '&source=constructor';
      return 'https://yandex.ru/map-widget/v1/?ll=' + s.ll + '&z=16&pt=' + s.ll + ',pm2rdl';
    }
    listEl.addEventListener('click', function (e) {
      var b = e.target.closest('.shop__map-live'); if (!b) return;
      var box = b.parentNode, st = shown[+box.dataset.shopMap];
      box.innerHTML = '<iframe src="' + widgetUrl(st) + '" title="' + esc(st.name + ' на карте') + '" allowfullscreen></iframe>';
      box.classList.add('is-live');
    });

    // Просмотр фото салона
    var view = document.querySelector('.js-shop-view');
    var vImg = document.querySelector('.js-sv-img');
    var vCap = document.querySelector('.js-sv-cap');
    var cur = { s: null, i: 0 };
    function show(i) {
      var ph = cur.s.photos;
      cur.i = (i + ph.length) % ph.length;
      vImg.src = ph[cur.i];
      vImg.alt = cur.s.name + ', ' + cur.s.city;
      vCap.textContent = cur.s.name + ' · ' + cur.s.city + ' · ' + (cur.i + 1) + ' из ' + ph.length;
      view.classList.toggle('is-single', ph.length < 2);
    }
    listEl.addEventListener('click', function (e) {
      var b = e.target.closest('[data-photo]'); if (!b || !view) return;
      cur.s = shown[+b.dataset.shop];
      show(+b.dataset.photo);
      view.showModal();
    });
    if (view) {
      document.querySelector('.js-sv-close').addEventListener('click', function () { view.close(); });
      document.querySelector('.js-sv-prev').addEventListener('click', function () { show(cur.i - 1); });
      document.querySelector('.js-sv-next').addEventListener('click', function () { show(cur.i + 1); });
      view.addEventListener('click', function (e) { if (e.target === view) view.close(); });
      view.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') show(cur.i - 1);
        if (e.key === 'ArrowRight') show(cur.i + 1);
      });
      // свайп на телефоне
      var x0 = null;
      view.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
      view.addEventListener('touchend', function (e) {
        if (x0 === null) return;
        var dx = e.changedTouches[0].clientX - x0; x0 = null;
        if (Math.abs(dx) > 40) show(cur.i + (dx < 0 ? 1 : -1));
      });
    }

    render();
  }
})();
