/* ---------- Яндекс Метрика и пиксель VK Ads: подключаются только после «Принять» в уведомлении о cookie ---------- */
(function () {
  var ID = 113661573;      // Яндекс Метрика
  var VK_ID = '3805477';   // пиксель VK Ads (Top.Mail.Ru)
  var loaded = false;
  var vkLoaded = false;

  // Цели: window.siteGoal('lead_success') — безопасно вызывать всегда; без согласия ничего не отправляется
  window.siteGoal = function (name, params) {
    if (loaded && typeof window.ym === 'function') window.ym(ID, 'reachGoal', name, params || {});
    if (vkLoaded) window._tmr.push({ type: 'reachGoal', id: VK_ID, goal: name });
  };

  function loadVk() {
    if (vkLoaded) return;
    vkLoaded = true;
    var _tmr = window._tmr || (window._tmr = []);
    _tmr.push({ id: VK_ID, type: 'pageView', start: Date.now() });
    if (document.getElementById('tmr-code')) return;
    var ts = document.createElement('script');
    ts.async = true; ts.id = 'tmr-code'; ts.src = 'https://top-fwz1.mail.ru/js/code.js';
    var first = document.getElementsByTagName('script')[0];
    first.parentNode.insertBefore(ts, first);
  }

  function load() {
    if (loaded) return;
    loaded = true;
    (function (m, e, t, r, i, k, a) {
      m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
      m[i].l = 1 * new Date();
      k = e.createElement(t); a = e.getElementsByTagName(t)[0];
      k.async = 1; k.src = r; a.parentNode.insertBefore(k, a);
    })(window, document, 'script', 'https://mc.yandex.ru/metrika/tag.js?id=' + ID, 'ym');
    window.ym(ID, 'init', { webvisor: true, clickmap: true, accurateTrackBounce: true, trackLinks: true });
  }

  var saved = null;
  try { saved = localStorage.getItem('cookie-consent'); } catch (e) {}

  // Сайт открыт внутри инструментов самой Метрики (карта кликов, аналитика форм, Вебвизор) —
  // это смотрит владелец сайта, а не посетитель: подключаем счётчик и не показываем уведомление о cookie
  var inMetrika = false;
  try {
    var anc = location.ancestorOrigins;
    inMetrika = window.self !== window.top && (
      /metrika\.yandex|webvisor\.com|metrica\.yandex/.test(document.referrer) ||
      (anc && anc.length && /metrika\.yandex|webvisor\.com|metrica\.yandex/.test(anc[anc.length - 1]))
    );
  } catch (e) {}
  if (inMetrika) {
    document.documentElement.classList.add('in-metrika');
    load();
  } else if (saved === 'all') {
    load();
    loadVk();
  }
  document.addEventListener('cookie-consent', function (e) { if (e.detail === 'all') { load(); loadVk(); } });

  // Клики-цели по всему сайту
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href');
    if (href.indexOf('tel:') === 0) window.siteGoal('phone_click');
    else if (href.indexOf('mailto:') === 0) window.siteGoal('email_click');
    else if (href.indexOf('yandex.ru/maps') !== -1) window.siteGoal('route_click');
    else if (href.indexOf('steelline.store/catalog') !== -1) window.siteGoal('catalog_click');
  });
})();

(function () {
  // Мобильное меню
  var header = document.querySelector('.header');
  var burger = document.querySelector('.header__burger');
  var nav = document.getElementById('site-nav');

  function setMenu(open) {
    header.classList.toggle('is-open', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
  }

  burger.addEventListener('click', function () {
    setMenu(!header.classList.contains('is-open'));
  });
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) setMenu(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setMenu(false);
  });

  // Бегущая строка: копий списка столько, чтобы лента без пробелов перекрывала любой экран,
  // а сдвиг за цикл — ровно на ширину одного списка (иначе на широких экранах в конце пустота)
  var track = document.querySelector('.ticker__track');
  var list = track && track.querySelector('.ticker__list');
  if (list) {
    var SPEED = 40; // пикселей в секунду
    var fillTicker = function () {
      var w = list.getBoundingClientRect().width;
      if (!w) return;
      var need = Math.ceil(window.innerWidth / w) + 1;
      while (track.children.length < need + 1) {
        var clone = list.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        track.appendChild(clone);
      }
      track.style.setProperty('--ticker-shift', w + 'px');
      track.style.setProperty('--ticker-dur', (w / SPEED) + 's');
    };
    fillTicker();
    window.addEventListener('resize', fillTicker);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fillTicker);
  }

  // Перетаскивание горизонтальных каруселей мышью
  document.querySelectorAll('[data-drag]').forEach(function (el) {
    var startX = 0;
    var startScroll = 0;
    var moved = false;
    var down = false;

    el.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      down = true;
      moved = false;
      startX = e.clientX;
      startScroll = el.scrollLeft;
    });

    window.addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - startX;
      if (!moved && Math.abs(dx) > 4) {
        moved = true;
        el.classList.add('is-dragging');
      }
      if (moved) el.scrollLeft = startScroll - dx;
    });

    window.addEventListener('pointerup', function () {
      if (!down) return;
      down = false;
      el.classList.remove('is-dragging');
    });

    el.addEventListener('dragstart', function (e) { e.preventDefault(); });
  });

  // «Дверь под вашу идею» на телефоне: лента из всех карточек одного размера (из тех же данных, что и слайдер)
  document.querySelectorAll('.idea2__mobile').forEach(function (track) {
    var dataEl = document.getElementById(track.dataset.items);
    if (!dataEl) return;
    JSON.parse(dataEl.textContent).forEach(function (it) {
      var card = document.createElement('article');
      card.className = 'idea2-mcard';
      card.innerHTML =
        '<div class="idea2-mcard__media"><img loading="lazy" width="1399" height="1514"></div>' +
        '<div class="idea2-card__desc"><h3 class="idea2-card__title"></h3><p class="idea2-card__text"></p></div>';
      var img = card.querySelector('img');
      img.src = it.src;
      img.alt = it.alt;
      card.querySelector('.idea2-card__title').innerHTML = it.title;
      card.querySelector('.idea2-card__text').innerHTML = it.text;
      track.appendChild(card);
    });
  });

  // «Дверь под вашу идею», вариант 2: три карточки стоят на месте, а фото внутри них «перетекают».
  // По стрелке в каждой карточке новое фото открывается шторкой поверх старого (старое уходит в сторону),
  // волной от большой карточки к маленьким. Подписи плавно сменяются.
  document.querySelectorAll('.idea2__stage').forEach(function (stage) {
    var dataEl = document.getElementById(stage.dataset.items);
    var items = dataEl ? JSON.parse(dataEl.textContent) : [];
    var cards = Array.prototype.slice.call(stage.querySelectorAll('.idea2-card'));
    var n = items.length;
    if (n < 2) return;
    var offset = 0; // какое фото сейчас в большой карточке
    var busy = false;
    var DURATION = 900;
    var STAGGER = 90;
    var EASE = 'cubic-bezier(0.65, 0, 0.35, 1)';
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function itemFor(pos) { return items[(offset + pos) % n]; }
    function plain(html) { return html.replace(/<br[^>]*>/g, ' ').replace(/\s+/g, ' ').trim(); }

    // фото подгружаем заранее, чтобы смена шла без мигания, — но только когда блок рядом с экраном
    // (а на телефоне, где этот слайдер скрыт, не подгружаем вовсе)
    function preload(src) {
      var img = new Image();
      img.src = src;
      return img.decode ? img.decode().catch(function () {}) : Promise.resolve();
    }
    var startPreload;
    var ready = new Promise(function (resolve) {
      startPreload = function () { resolve(Promise.all(items.map(function (it) { return preload(it.src); }))); };
    });
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting && stage.offsetParent !== null) { io.disconnect(); startPreload(); }
      }, { rootMargin: '600px 0px' });
      io.observe(stage);
    } else {
      startPreload();
    }

    function setText(card, it) {
      card.querySelector('.idea2-card__title').innerHTML = it.title;
      card.querySelector('.idea2-card__text').innerHTML = it.text;
      card.querySelector('.idea2-card__media').setAttribute('aria-label', 'Показать крупно: ' + plain(it.title));
    }

    function swapCard(card, it, dir, delay) {
      var holder = card.querySelector('.zoom');
      // если прошлый переход не успел убрать старые слои — убираем, оставляя только текущее фото
      var layers = holder.querySelectorAll('.idea2-card__img');
      for (var l = 0; l < layers.length - 1; l++) layers[l].remove();
      var oldImg = layers[layers.length - 1];
      if (oldImg) oldImg.getAnimations().forEach(function (an) { an.cancel(); });
      var newImg = document.createElement('img');
      newImg.className = 'idea2-card__img';
      newImg.src = it.src;
      newImg.alt = it.alt;
      holder.appendChild(newImg);

      var desc = card.querySelector('.idea2-card__desc');
      if (reduced) {
        if (oldImg) oldImg.remove();
        setText(card, it);
        return Promise.resolve();
      }
      // вперёд — новое фото натекает справа, назад — слева
      var from = dir > 0 ? 'inset(0 0 0 100%)' : 'inset(0 100% 0 0)';
      var shift = dir > 0 ? '-12%' : '12%';
      var timing = { duration: DURATION, easing: EASE, delay: delay, fill: 'both' };
      var anims = [
        newImg.animate([
          { clipPath: from, transform: 'scale(1.08)' },
          { clipPath: 'inset(0 0 0 0)', transform: 'scale(1)' }
        ], timing)
      ];
      if (oldImg) {
        anims.push(oldImg.animate([
          { transform: 'translateX(0)', filter: 'brightness(1)' },
          { transform: 'translateX(' + shift + ')', filter: 'brightness(0.6)' }
        ], timing));
      }
      // подпись: гаснет и проявляется с новым текстом посередине перехода
      desc.animate([{ opacity: 1 }, { opacity: 0 }], { duration: DURATION * 0.35, delay: delay, easing: 'ease', fill: 'forwards' })
        .finished.then(function () {
          setText(card, it);
          return desc.animate([{ opacity: 0 }, { opacity: 1 }], { duration: DURATION * 0.45, easing: 'ease', fill: 'forwards' }).finished;
        }).catch(function () {});

      return Promise.all(anims.map(function (an) { return an.finished.catch(function () {}); })).then(function () {
        if (oldImg) oldImg.remove();
        newImg.getAnimations().forEach(function (an) { an.cancel(); });
      });
    }

    function go(step) {
      if (busy || !step) return;
      busy = true;
      offset = ((offset + step) % n + n) % n;
      var dir = step > 0 ? 1 : -1;
      ready.then(function () {
        // волна: при «вперёд» от большой к маленьким, при «назад» — наоборот
        var order = dir > 0 ? cards : cards.slice().reverse();
        var jobs = order.map(function (card, k) {
          return swapCard(card, itemFor(parseInt(card.dataset.pos, 10)), dir, k * STAGGER);
        });
        var done = false;
        var finish = function () { if (!done) { done = true; busy = false; } };
        Promise.all(jobs).then(finish);
        // страховка, если браузер приостановил анимацию (фоновая вкладка)
        setTimeout(finish, DURATION + STAGGER * cards.length + 200);
      });
    }

    stage.querySelectorAll('[data-idea2-dir]').forEach(function (btn) {
      btn.addEventListener('click', function () { go(parseInt(btn.dataset.idea2Dir, 10)); });
    });
    // клик по маленькой карточке — её фото переходит в большую
    cards.forEach(function (card) {
      card.querySelector('.idea2-card__media').addEventListener('click', function () {
        go(parseInt(card.dataset.pos, 10));
      });
    });
  });

  // Центрированная карусель («За рамками…»): масштаб карточек под ширину экрана,
  // отступы, чтобы первая и последняя карточки вставали по центру, и ширина белого fade по бокам
  document.querySelectorAll('[data-center]').forEach(function (track) {
    if (track.closest('[hidden]')) return; // блок скрыт — не клонируем карточки и не грузим их фото
    var PEEK = 80; // сколько видно соседних карточек с каждой стороны на десктопе
    var DESIGN_W = 1475;

    // Бесконечная прокрутка (data-loop): копии карточек слева и справа от настоящих.
    // Когда лента останавливается на копии, незаметно перескакиваем на такую же настоящую карточку.
    var loop = track.hasAttribute('data-loop');
    var count = track.children.length;
    if (loop) {
      var originals = Array.prototype.slice.call(track.children);
      var makeClone = function (card) {
        var c = card.cloneNode(true);
        c.setAttribute('aria-hidden', 'true');
        c.setAttribute('inert', '');
        c.classList.add('is-clone');
        return c;
      };
      originals.slice().reverse().forEach(function (card) { track.insertBefore(makeClone(card), track.firstChild); });
      originals.forEach(function (card) { track.appendChild(makeClone(card)); });
    }
    function layout() {
      var tw = track.clientWidth;
      if (!tw) return; // блок скрыт — считать нечего
      var desktop = window.innerWidth >= 768;
      var s = desktop ? Math.min(1, (tw - 2 * PEEK) / DESIGN_W) : 1;
      track.style.setProperty('--s', s.toFixed(4));
      var cards = track.children;
      var first = cards[0].getBoundingClientRect().width;
      var last = cards[cards.length - 1].getBoundingClientRect().width;
      var widest = 0;
      Array.prototype.forEach.call(cards, function (c) { widest = Math.max(widest, c.getBoundingClientRect().width); });
      track.style.setProperty('--pad-l', Math.max(0, (tw - first) / 2) + 'px');
      track.style.setProperty('--pad-r', Math.max(0, (tw - last) / 2) + 'px');
      // ширина fade: 60% от видимой части соседних карточек
      track.style.setProperty('--fade', Math.max(10, Math.min(96, (tw - widest) / 2 * 0.6)) + 'px');
    }
    // Номер карточки, ближайшей к центру
    function centeredIndex() {
      var mid = track.getBoundingClientRect().left + track.clientWidth / 2;
      var best = 0;
      var dist = Infinity;
      Array.prototype.forEach.call(track.children, function (c, i) {
        var r = c.getBoundingClientRect();
        var d = Math.abs(r.left + r.width / 2 - mid);
        if (d < dist) { dist = d; best = i; }
      });
      return best;
    }
    function centerOn(i) {
      var c = track.children[i];
      var r = c.getBoundingClientRect();
      var left = r.left - track.getBoundingClientRect().left + track.scrollLeft + r.width / 2 - track.clientWidth / 2;
      track.scrollTo({ left: left, behavior: 'instant' });
    }
    // Если по центру копия — перескакиваем на настоящую карточку (без анимации, содержимое то же)
    function normalize() {
      if (!loop || track.classList.contains('is-dragging')) return;
      var i = centeredIndex();
      if (i >= count && i < 2 * count) return;
      var clone = track.children[i];
      var real = track.children[count + (i % count)];
      var delta = real.getBoundingClientRect().left - clone.getBoundingClientRect().left;
      track.scrollTo({ left: track.scrollLeft + delta, behavior: 'instant' });
    }
    if (loop) {
      var idle;
      track.addEventListener('scroll', function () {
        clearTimeout(idle);
        idle = setTimeout(normalize, 150);
      }, { passive: true });
      track.addEventListener('scrollend', normalize);
      window.addEventListener('pointerup', function () { setTimeout(normalize, 200); });
    }

    layout();
    // При загрузке по центру стоит карточка из data-center (номер с 1)
    var startIndex = Math.max(0, Math.min(count - 1, (parseInt(track.dataset.center, 10) || 1) - 1));
    centerOn(loop ? count + startIndex : startIndex);
    // При изменении размера окна держим по центру ту же карточку
    window.addEventListener('resize', function () {
      var i = centeredIndex();
      layout();
      centerOn(i);
    });
  });

  // Стрелки каруселей: листаем на одну карточку, у края стрелка выключается
  document.querySelectorAll('.slider-nav').forEach(function (nav) {
    var track = document.getElementById(nav.dataset.target);
    if (!track) return;
    var prev = nav.querySelector('[data-dir="-1"]');
    var next = nav.querySelector('[data-dir="1"]');
    var cards = Array.prototype.slice.call(track.children);

    function start() {
      return parseFloat(getComputedStyle(track).scrollPaddingLeft) || 0;
    }
    // Позиция карточки внутри ленты (в координатах прокрутки)
    function pos(c) {
      return c.getBoundingClientRect().left - track.getBoundingClientRect().left + track.scrollLeft;
    }
    var looped = track.hasAttribute('data-loop');
    function update() {
      if (looped) { prev.disabled = false; next.disabled = false; return; }
      var max = track.scrollWidth - track.clientWidth;
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= max - 2;
    }
    var centered = track.hasAttribute('data-center');

    // Центрированная карусель: ищем карточку, ближайшую к центру, и ставим в центр соседнюю
    function stepCenter(dir) {
      var mid = track.scrollLeft + track.clientWidth / 2;
      var current = 0;
      var best = Infinity;
      cards.forEach(function (c, i) {
        var d = Math.abs(pos(c) + c.getBoundingClientRect().width / 2 - mid);
        if (d < best) { best = d; current = i; }
      });
      var target = cards[Math.max(0, Math.min(cards.length - 1, current + dir))];
      var left = pos(target) + target.getBoundingClientRect().width / 2 - track.clientWidth / 2;
      track.scrollTo({ left: left, behavior: 'smooth' });
      setTimeout(update, 600);
    }

    function step(dir) {
      if (centered) return stepCenter(dir);
      var edge = track.scrollLeft + start();
      var target = null;
      if (dir > 0) {
        target = cards.filter(function (c) { return pos(c) > edge + 4; })[0];
      } else {
        var before = cards.filter(function (c) { return pos(c) < edge - 4; });
        target = before[before.length - 1];
      }
      var left = target ? pos(target) - start() : (dir > 0 ? track.scrollWidth : 0);
      track.scrollTo({ left: left, behavior: 'smooth' });
      setTimeout(update, 600);
    }

    prev.addEventListener('click', function () { step(-1); });
    next.addEventListener('click', function () { step(1); });
    track.addEventListener('scroll', update, { passive: true });
    track.addEventListener('scrollend', update);
    window.addEventListener('resize', update);
    update();
  });

  // Слайдер первого экрана: точки и автопрокрутка включаются, когда слайдов больше одного
  (function () {
    var slides = document.querySelectorAll('.hero__slide');
    var dots = document.querySelector('.hero__steps');
    if (!dots || slides.length < 2) {
      if (dots) dots.hidden = true;
      return;
    }
    var SLIDE_MS = 6000;
    var current = 0;
    var timer = null;
    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    dots.style.setProperty('--slide-ms', SLIDE_MS + 'ms');

    slides.forEach(function (_, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-label', 'Слайд ' + (i + 1));
      b.addEventListener('click', function () { go(i); restart(); });
      dots.appendChild(b);
    });

    // Фото слайдов грузятся по мере надобности: текущее и следующее
    function load(i) {
      var slide = slides[(i + slides.length) % slides.length];
      // мобильный вариант фото (<source> внутри <picture>) — подставляем до картинки
      var source = slide.querySelector('source[data-srcset]');
      if (source) {
        source.srcset = source.dataset.srcset;
        source.removeAttribute('data-srcset');
      }
      var img = slide.querySelector('img[data-src]');
      if (img) {
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
      }
    }

    function go(i) {
      current = (i + slides.length) % slides.length;
      load(current);
      load(current + 1);
      load(current - 1); // для свайпа назад
      slides.forEach(function (s, k) { s.classList.toggle('is-active', k === current); });
      // Сбрасываем и заново запускаем заполнение активной полоски
      var buttons = dots.querySelectorAll('button');
      buttons.forEach(function (b) { b.setAttribute('aria-selected', 'false'); });
      void dots.offsetWidth;
      buttons[current].setAttribute('aria-selected', 'true');
    }
    function restart() {
      if (reduced) return;
      clearInterval(timer);
      timer = setInterval(function () { go(current + 1); }, SLIDE_MS);
    }
    // Пока вкладка скрыта, слайды не листаем
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) clearInterval(timer);
      else { go(current); restart(); }
    });

    // Свайп на телефоне и перетаскивание мышью на компьютере: влево — следующий слайд, вправо — предыдущий.
    // С кнопок и ссылок жест не начинается; вертикальная прокрутка страницы работает как обычно.
    var hero = document.querySelector('.hero');
    var THRESHOLD = 50;
    var startX = null;
    var startY = 0;
    var pointerId = null;
    var dragged = false;

    hero.addEventListener('pointerdown', function (e) {
      dragged = false;
      if (e.button !== 0 || e.target.closest('a, button, input, textarea')) return;
      startX = e.clientX;
      startY = e.clientY;
      pointerId = e.pointerId;
      dragged = false;
      if (e.pointerType === 'mouse') {
        hero.classList.add('is-grabbing');
        e.preventDefault(); // не выделяем текст и не тащим картинку
      }
    });
    hero.addEventListener('pointermove', function (e) {
      if (startX === null || e.pointerId !== pointerId) return;
      if (Math.abs(e.clientX - startX) > 8) dragged = true;
    });
    function finish(e) {
      if (startX === null || e.pointerId !== pointerId) return;
      var dx = e.clientX - startX;
      var dy = e.clientY - startY;
      startX = null;
      hero.classList.remove('is-grabbing');
      // клик, который браузер шлёт сразу после перетаскивания, гасим; дальше клики работают как обычно
      setTimeout(function () { dragged = false; }, 0);
      // листаем только явный горизонтальный жест
      if (Math.abs(dx) > THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
        go(current + (dx < 0 ? 1 : -1));
        restart();
      }
    }
    hero.addEventListener('pointerup', finish);
    hero.addEventListener('pointercancel', function () { startX = null; hero.classList.remove('is-grabbing'); });
    hero.addEventListener('lostpointercapture', function () { hero.classList.remove('is-grabbing'); });
    // после перетаскивания мышью не срабатывает случайный клик
    hero.addEventListener('click', function (e) {
      if (dragged) { e.preventDefault(); e.stopPropagation(); dragged = false; }
    }, true);
    hero.addEventListener('dragstart', function (e) { e.preventDefault(); });

    go(0);
    restart();
  })();

  // Видеообзоры: по клику ролик открывается в большом плеере поверх страницы.
  // Листать можно стрелками на экране, клавишами ← → и свайпом; список — карточки того же блока
  (function () {
    var player = document.getElementById('player');
    if (!player) return;
    var video = player.querySelector('.player__video');
    var title = player.querySelector('.player__title');
    var count = player.querySelector('.player__count');
    var prevBtn = player.querySelector('[data-player-dir="-1"]');
    var nextBtn = player.querySelector('[data-player-dir="1"]');
    var list = [];
    var index = 0;
    var opener = null;

    function cardData(thumb) {
      var card = thumb.closest('.video-card');
      var img = thumb.querySelector('img');
      var h = card && card.querySelector('.video-card__title');
      return {
        src: thumb.dataset.video,
        poster: img ? img.currentSrc || img.src : '',
        title: h ? h.textContent.replace(/\s+/g, ' ').trim() : ''
      };
    }

    function show(i) {
      index = (i + list.length) % list.length;
      var item = cardData(list[index]);
      video.pause();
      video.poster = item.poster;
      video.src = item.src;
      title.textContent = item.title;
      count.textContent = list.length > 1 ? (index + 1) + ' / ' + list.length : '';
      prevBtn.hidden = nextBtn.hidden = list.length < 2;
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
    }

    document.addEventListener('click', function (e) {
      var thumb = e.target.closest('.video-card__thumb[data-video]');
      if (!thumb) return;
      e.preventDefault();
      window.siteGoal('video_open');
      // список роликов — карточки из того же блока (страница или модалка с обзорами)
      var scope = thumb.closest('.reels__body, .reviews__grid') || document;
      list = Array.prototype.slice.call(scope.querySelectorAll('.video-card__thumb[data-video]'));
      opener = thumb;
      document.body.classList.add('has-modal');
      if (!player.open) player.showModal();
      show(list.indexOf(thumb));
    });

    prevBtn.addEventListener('click', function () { show(index - 1); });
    nextBtn.addEventListener('click', function () { show(index + 1); });
    player.addEventListener('click', function (e) {
      if (e.target === player || e.target.closest('[data-close-player]')) player.close();
    });
    player.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); show(index + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); show(index - 1); }
    });

    // Свайп влево/вправо на телефоне
    var startX = null;
    player.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
    player.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      startX = null;
      if (Math.abs(dx) > 60 && list.length > 1) show(index + (dx < 0 ? 1 : -1));
    });

    player.addEventListener('close', function () {
      video.pause();
      video.removeAttribute('src');
      video.load();
      // фон страницы остаётся заблокированным, если под плеером открыта модалка с обзорами
      var reels = document.getElementById('reels');
      if (!(reels && reels.open)) document.body.classList.remove('has-modal');
      if (opener) opener.focus();
    });
  })();

  // ---------- Галерея салона: просмотр фото крупно ----------
  (function () {
    var view = document.getElementById('gallery-view');
    var items = Array.prototype.slice.call(document.querySelectorAll('.salon-gallery__item'));
    if (!view || !items.length) return;
    var img = view.querySelector('.gallery-view__img');
    var title = view.querySelector('.gallery-view__title');
    var count = view.querySelector('.gallery-view__count');
    var index = 0;
    var opener = null;

    function show(i) {
      index = (i + items.length) % items.length;
      var src = items[index].querySelector('img');
      img.src = src.currentSrc || src.src;
      img.alt = src.alt;
      title.textContent = src.alt;
      count.textContent = (index + 1) + ' / ' + items.length;
    }

    items.forEach(function (item, i) {
      item.addEventListener('click', function () {
        opener = item;
        document.body.classList.add('has-modal');
        view.showModal();
        show(i);
      });
    });
    view.querySelectorAll('[data-gallery-dir]').forEach(function (b) {
      b.addEventListener('click', function () { show(index + parseInt(b.dataset.galleryDir, 10)); });
    });
    view.addEventListener('click', function (e) {
      if (e.target === view || e.target.closest('[data-close-gallery]')) view.close();
    });
    view.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); show(index + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); show(index - 1); }
    });
    var startX = null;
    view.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
    view.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      startX = null;
      if (Math.abs(dx) > 60) show(index + (dx < 0 ? 1 : -1));
    });
    view.addEventListener('close', function () {
      document.body.classList.remove('has-modal');
      if (opener) opener.focus();
    });
  })();

  // ---------- Все видеообзоры (модальное окно) ----------
  // Кнопка «Смотреть обзоры» открывает модалку; без JS ссылка ведёт на steelline.store
  (function () {
    var reels = document.getElementById('reels');
    if (!reels) return;
    var opener = null;

    function stopAll() {
      reels.querySelectorAll('video').forEach(function (v) { v.pause(); });
    }

    document.addEventListener('click', function (e) {
      var trigger = e.target.closest('[data-open-reels]');
      if (trigger) {
        e.preventDefault();
        opener = trigger;
        document.body.classList.add('has-modal');
        reels.showModal();
        reels.scrollTop = 0;
        return;
      }
      if (e.target.closest('[data-close-reels]')) reels.close();
    });

    // Клик по фону закрывает окно
    reels.addEventListener('click', function (e) {
      if (e.target === reels) reels.close();
    });

    reels.addEventListener('close', function () {
      stopAll();
      document.body.classList.remove('has-modal');
      if (opener) opener.focus();
    });
  })();

  // ---------- Форма заявки ----------
  var dialog = document.getElementById('lead');
  var form = document.getElementById('lead-form');
  if (!dialog || !form) return;

  var MAX_FILES = 5;
  var MAX_SIZE = 10 * 1024 * 1024; // 10 МБ на файл до сжатия
  var MAX_SIDE = 2000; // фото сжимаем до 2000px по длинной стороне

  var done = dialog.querySelector('.lead__done');
  var title = form.querySelector('.lead__title');
  var lead = form.querySelector('.lead__lead');
  var fileInput = document.getElementById('lead-photos');
  var dropzone = form.querySelector('.dropzone');
  var previews = document.getElementById('lead-previews');
  var photosError = document.getElementById('photos-error');
  var phone = document.getElementById('lead-phone');
  var submit = form.querySelector('.lead__submit');
  var submitText = form.querySelector('.lead__submit-text');
  var status = form.querySelector('.lead__status');
  var files = [];
  var lastTrigger = null;
  var openedAt = 0;

  // Метки рекламы и источник визита: запоминаем при первом заходе в этой вкладке, отправляем с заявкой
  var TRACK_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'yclid', 'gclid'];
  var track = {};
  try { track = JSON.parse(sessionStorage.getItem('lead-track') || '{}') || {}; } catch (e) { track = {}; }
  (function () {
    var params = new URLSearchParams(location.search);
    var fresh = {};
    TRACK_KEYS.forEach(function (k) { var v = params.get(k); if (v) fresh[k] = v.slice(0, 300); });
    if (Object.keys(fresh).length) track = fresh; // новый переход по рекламе важнее старого
    if (!track.landing) track.landing = location.href.slice(0, 300);
    if (!track.referrer && document.referrer && document.referrer.indexOf(location.host) === -1) {
      track.referrer = document.referrer.slice(0, 300);
    }
    try { sessionStorage.setItem('lead-track', JSON.stringify(track)); } catch (e) {}
  })();

  function openForm(source) {
    var contact = source === 'contact';
    title.textContent = contact ? title.dataset.titleContact : title.dataset.titlePhoto;
    lead.textContent = contact ? lead.dataset.leadContact : lead.dataset.leadPhoto;
    form.elements.source.value = source || '';
    openedAt = Date.now();
    window.siteGoal('form_open', { source: source || '' });
    form.hidden = false;
    done.hidden = true;
    status.textContent = '';
    setMenu(false);
    document.body.classList.add('has-modal');
    dialog.showModal();
  }

  function closeForm() {
    dialog.close();
  }

  dialog.addEventListener('close', function () {
    document.body.classList.remove('has-modal');
    if (!done.hidden) resetForm();
    if (lastTrigger) lastTrigger.focus();
  });

  // Клик по фону закрывает окно
  dialog.addEventListener('click', function (e) {
    if (e.target === dialog) closeForm();
  });

  document.addEventListener('click', function (e) {
    var trigger = e.target.closest('[data-open-form]');
    if (trigger) {
      e.preventDefault();
      lastTrigger = trigger;
      openForm(trigger.dataset.openForm);
      return;
    }
    if (e.target.closest('[data-close-form]')) closeForm();
  });

  // Маска телефона: +7 (XXX) XXX-XX-XX
  function phoneDigits(value) {
    var d = value.replace(/\D/g, '');
    if (d[0] === '8') d = '7' + d.slice(1);
    if (d && d[0] !== '7') d = '7' + d;
    return d.slice(0, 11);
  }
  function formatPhone(d) {
    if (!d) return '';
    var r = '+7';
    if (d.length > 1) r += ' (' + d.slice(1, 4);
    if (d.length >= 4) r += ')';
    if (d.length > 4) r += ' ' + d.slice(4, 7);
    if (d.length > 7) r += '-' + d.slice(7, 9);
    if (d.length > 9) r += '-' + d.slice(9, 11);
    return r;
  }
  phone.addEventListener('input', function () {
    phone.value = formatPhone(phoneDigits(phone.value));
  });
  phone.addEventListener('focus', function () {
    if (!phone.value) phone.value = '+7 (';
  });
  phone.addEventListener('blur', function () {
    if (phoneDigits(phone.value).length <= 1) phone.value = '';
  });

  // Фото проёма
  function isImage(file) {
    return /^image\//.test(file.type) || /\.(heic|heif)$/i.test(file.name);
  }

  function addFiles(list) {
    photosError.textContent = '';
    Array.prototype.forEach.call(list, function (file) {
      if (!isImage(file)) {
        photosError.textContent = 'Можно загрузить только фотографии.';
        return;
      }
      if (file.size > MAX_SIZE) {
        photosError.textContent = 'Файл «' + file.name + '» больше 10 МБ.';
        return;
      }
      if (files.length >= MAX_FILES) {
        photosError.textContent = 'Можно приложить до ' + MAX_FILES + ' фото.';
        return;
      }
      files.push(file);
    });
    renderPreviews();
  }

  function renderPreviews() {
    previews.querySelectorAll('img').forEach(function (img) { URL.revokeObjectURL(img.src); });
    previews.innerHTML = '';
    files.forEach(function (file, i) {
      var li = document.createElement('li');
      li.className = 'preview';
      var img = document.createElement('img');
      img.alt = file.name;
      img.src = URL.createObjectURL(file);
      // HEIC большинство браузеров не показывает — выводим имя файла
      img.addEventListener('error', function () {
        var name = document.createElement('span');
        name.className = 'preview__name';
        name.textContent = file.name;
        img.replaceWith(name);
      });
      var remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'preview__remove';
      remove.setAttribute('aria-label', 'Удалить ' + file.name);
      remove.innerHTML = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M3 3l6 6M9 3l-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>';
      remove.addEventListener('click', function () {
        files.splice(i, 1);
        photosError.textContent = '';
        renderPreviews();
      });
      li.appendChild(img);
      li.appendChild(remove);
      previews.appendChild(li);
    });
  }

  fileInput.addEventListener('change', function () {
    addFiles(fileInput.files);
    fileInput.value = '';
  });

  ['dragenter', 'dragover'].forEach(function (type) {
    dropzone.addEventListener(type, function (e) {
      e.preventDefault();
      dropzone.classList.add('is-over');
    });
  });
  ['dragleave', 'drop'].forEach(function (type) {
    dropzone.addEventListener(type, function (e) {
      e.preventDefault();
      dropzone.classList.remove('is-over');
    });
  });
  dropzone.addEventListener('drop', function (e) {
    if (e.dataTransfer && e.dataTransfer.files) addFiles(e.dataTransfer.files);
  });

  // Сжимаем JPEG/PNG/WebP перед отправкой; HEIC и всё, что браузер не открыл, уходит как есть
  function compress(file) {
    if (!/^image\/(jpeg|png|webp)$/.test(file.type) || !window.createImageBitmap) {
      return Promise.resolve(file);
    }
    return createImageBitmap(file).then(function (bmp) {
      var scale = Math.min(1, MAX_SIDE / Math.max(bmp.width, bmp.height));
      var canvas = document.createElement('canvas');
      canvas.width = Math.round(bmp.width * scale);
      canvas.height = Math.round(bmp.height * scale);
      canvas.getContext('2d').drawImage(bmp, 0, 0, canvas.width, canvas.height);
      return new Promise(function (resolve) {
        canvas.toBlob(function (blob) {
          if (!blob || blob.size >= file.size) return resolve(file);
          var name = file.name.replace(/\.\w+$/, '') + '.jpg';
          resolve(new File([blob], name, { type: 'image/jpeg' }));
        }, 'image/jpeg', 0.85);
      });
    }).catch(function () { return file; });
  }

  // Проверка полей
  function setError(input, message) {
    var field = input.closest('.field');
    field.classList.toggle('is-invalid', !!message);
    field.querySelector('.field__error').textContent = message || '';
    input.setAttribute('aria-invalid', message ? 'true' : 'false');
  }

  function validate() {
    var ok = true;
    var name = form.elements.name;
    var email = form.elements.email;
    var consent = form.elements.consent;

    if (name.value.trim().length < 2) { setError(name, 'Укажите имя'); ok = false; } else setError(name, '');
    if (phoneDigits(phone.value).length !== 11) { setError(phone, 'Укажите телефон полностью'); ok = false; } else setError(phone, '');
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.value.trim())) { setError(email, 'Проверьте адрес почты'); ok = false; } else setError(email, '');
    if (!consent.checked) { setError(consent, 'Нужно ваше согласие, чтобы отправить заявку'); ok = false; } else setError(consent, '');

    if (!ok) {
      var first = form.querySelector('[aria-invalid="true"]');
      if (first) first.focus();
    }
    return ok;
  }

  form.addEventListener('input', function (e) {
    if (e.target.getAttribute('aria-invalid') === 'true') setError(e.target, '');
  });

  function setLoading(on) {
    submit.disabled = on;
    submitText.textContent = on ? 'Отправляем…' : 'Получить подбор двери';
  }

  function resetForm() {
    form.reset();
    files = [];
    renderPreviews();
    form.querySelectorAll('.field.is-invalid').forEach(function (f) { f.classList.remove('is-invalid'); });
    form.querySelectorAll('.field__error').forEach(function (p) { p.textContent = ''; });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    status.textContent = '';
    if (!validate()) return;

    // Тестовый режим (GitHub Pages): заявку никуда не отправляем и честно говорим об этом
    if (form.hasAttribute('data-test-mode')) {
      status.innerHTML = '';
      status.classList.add('is-info');
      status.appendChild(document.createTextNode('Сайт работает в тестовом режиме — заявка не отправлена. Чтобы подобрать дверь, позвоните нам: '));
      var tel = document.createElement('a');
      tel.href = 'tel:+79222077552';
      tel.textContent = '+7 (922) 207-75-52';
      status.appendChild(tel);
      return;
    }
    status.classList.remove('is-info');
    window.siteGoal('form_submit');

    setLoading(true);
    Promise.all(files.map(compress)).then(function (ready) {
      var data = new FormData(form);
      data.set('phone', formatPhone(phoneDigits(phone.value)));
      data.set('ts', String(openedAt));
      Object.keys(track).forEach(function (k) { data.set(k, track[k]); });
      ready.forEach(function (file) { data.append('photos[]', file, file.name); });
      return fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (json) {
        if (!res.ok || !json.ok) throw new Error(json.error || 'send_failed');
      });
    }).then(function () {
      form.hidden = true;
      done.hidden = false;
      done.querySelector('.btn').focus();
      window.siteGoal('lead_success', { source: form.elements.source.value });
    }).catch(function (err) {
      var msg = err && err.message && err.message !== 'send_failed' && err.message !== 'Failed to fetch'
        ? err.message + ' '
        : 'Не получилось отправить заявку. ';
      window.siteGoal('form_error');
      status.innerHTML = '';
      status.appendChild(document.createTextNode(msg + 'Позвоните нам: '));
      var a = document.createElement('a');
      a.href = 'tel:+79222077552';
      a.textContent = '+7 (922) 207-75-52';
      status.appendChild(a);
    }).then(function () {
      setLoading(false);
    });
  });
})();

/* ---------- Превью видеообзоров: без звука по наведению ---------- */
(function () {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  function thumbOf(el) {
    var card = el && el.closest && el.closest('.video-card');
    return card && card.querySelector('.video-card__thumb[data-video]');
  }

  function start(thumb) {
    var v = thumb.querySelector('.video-card__preview');
    if (!v) {
      v = document.createElement('video');
      v.className = 'video-card__preview';
      v.muted = true;
      v.loop = true;
      v.playsInline = true;
      v.preload = 'auto';
      v.setAttribute('aria-hidden', 'true');
      v.addEventListener('playing', function () {
        if (thumb.dataset.hover) v.classList.add('is-playing');
      });
      v.src = thumb.dataset.video;
      thumb.insertBefore(v, thumb.querySelector('.video-card__badge'));
    }
    thumb.dataset.hover = '1';
    var p = v.play();
    if (p && p.catch) p.catch(function () {});
  }

  function stop(thumb) {
    var v = thumb.querySelector('.video-card__preview');
    delete thumb.dataset.hover;
    if (!v) return;
    v.classList.remove('is-playing');
    v.pause();
  }

  document.addEventListener('mouseover', function (e) {
    var t = thumbOf(e.target);
    if (t && !t.dataset.hover) start(t);
  });
  document.addEventListener('mouseout', function (e) {
    var t = thumbOf(e.target);
    if (!t) return;
    var card = t.closest('.video-card');
    if (e.relatedTarget && card.contains(e.relatedTarget)) return;
    stop(t);
  });
  // при открытии большого плеера превью останавливаем
  document.addEventListener('click', function (e) {
    var t = thumbOf(e.target);
    if (t) stop(t);
  });
})();

/* ---------- Закреплённая кнопка заявки (телефон): появляется после первого экрана ---------- */
(function () {
  var cta = document.querySelector('.sticky-cta');
  var edge = document.querySelector('.ticker') || document.querySelector('.hero');
  if (!cta || !edge || !('IntersectionObserver' in window)) {
    if (cta) cta.classList.add('is-visible');
    return;
  }
  new IntersectionObserver(function (entries) {
    var e = entries[0];
    // показываем, когда бегущая строка целиком ушла под шапку (64px)
    cta.classList.toggle('is-visible', !e.isIntersecting && e.boundingClientRect.top < 64);
  }, { rootMargin: '-64px 0px 0px 0px' }).observe(edge);
})();

/* ---------- Уведомление о cookie ----------
   Выбор: 'all' — все cookie (можно подключать Яндекс.Метрику), 'necessary' — только необходимые.
   Текущий выбор: window.cookieConsent; при выборе — событие 'cookie-consent' на document. */
(function () {
  var KEY = 'cookie-consent';
  var box = document.getElementById('cookie');
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  window.cookieConsent = saved;
  if (!box || saved) return;

  var root = document.documentElement;
  function syncHeight() { root.style.setProperty('--cookie-h', box.hidden ? '0px' : (box.offsetHeight + 12) + 'px'); }

  box.hidden = false;
  syncHeight();
  window.addEventListener('resize', syncHeight);

  box.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-cookie]');
    if (!btn) return;
    var value = btn.getAttribute('data-cookie');
    try { localStorage.setItem(KEY, value); } catch (err) {}
    window.cookieConsent = value;
    box.hidden = true;
    syncHeight();
    window.removeEventListener('resize', syncHeight);
    document.dispatchEvent(new CustomEvent('cookie-consent', { detail: value }));
  });
})();

/* ---------- Фото в горизонтальных лентах: начинаем грузить заранее, когда лента подъезжает к экрану ----------
   Браузер грузит lazy-фото в горизонтальной ленте только при прокрутке до них — карточки «проявлялись» с задержкой */
(function () {
  if (!('IntersectionObserver' in window)) return;
  document.querySelectorAll('#eng-track').forEach(function (track) {
    var io = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      io.disconnect();
      track.querySelectorAll('img[loading="lazy"]').forEach(function (img) { img.loading = 'eager'; });
    }, { rootMargin: '800px 0px' });
    io.observe(track);
  });
})();

