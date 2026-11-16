/* Прототип «Гид по продукту»: видео Rutube по нажатию, окно технологии. Вертикальные ролики открывает общий плеер из script.js */
(function () {
  // Видео о фабрике: обложка → плеер Rutube (страница не грузит четыре плеера сразу)
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-rutube]'); if (!b) return;
    window.siteGoal && window.siteGoal('video_open');
    var box = document.createElement('div');
    box.className = 'rt-card__media is-live';
    box.innerHTML = '<iframe src="https://rutube.ru/play/embed/' + b.dataset.rutube + '?autoplay=1" title="' + b.getAttribute('aria-label').replace(/"/g, '&quot;') + '" allow="autoplay; clipboard-write; fullscreen; picture-in-picture" allowfullscreen></iframe>';
    b.parentNode.replaceChild(box, b);
  });

  // Ленты роликов: стрелки по краям при наведении (полоса прокрутки скрыта), листают на ширину ленты
  document.querySelectorAll('.gid-track-wrap').forEach(function (wrap) {
    var track = wrap.querySelector('.gid-reels--track');
    var prev = wrap.querySelector('.gid-arrow--prev'), next = wrap.querySelector('.gid-arrow--next');
    function sync() {
      var thumb = track.querySelector('.video-card__thumb');
      if (thumb) prev.style.top = next.style.top = (thumb.offsetHeight / 2) + 'px'; // середина ролика
      var max = track.scrollWidth - track.clientWidth;
      prev.hidden = next.hidden = max <= 2;
      prev.disabled = track.scrollLeft <= 2;
      next.disabled = track.scrollLeft >= max - 2;
    }
    function step(dir) { track.scrollBy({ left: dir * (track.clientWidth - 40), behavior: 'smooth' }); }
    prev.addEventListener('click', function () { step(-1); });
    next.addEventListener('click', function () { step(1); });
    track.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', sync);
    window.addEventListener('load', sync);
    sync();
  });

  // Технологии: карточка → окно с фото, описанием и пунктами; листаются стрелками
  var view = document.querySelector('.js-tech-view');
  var dataEl = document.getElementById('tech-data');
  if (!view || !dataEl) return;
  var tech = JSON.parse(dataEl.textContent);
  var img = view.querySelector('.js-tv-img');
  var title = view.querySelector('.js-tv-title');
  var lead = view.querySelector('.js-tv-lead');
  var points = view.querySelector('.js-tv-points');
  var cur = 0, opener = null;
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function show(i) {
    cur = (i + tech.length) % tech.length;
    var t = tech[cur];
    img.src = t.img; img.alt = t.title;
    title.textContent = t.title;
    lead.textContent = t.lead;
    points.innerHTML = t.points.map(function (p) { return '<div><dt>' + esc(p.t) + '</dt><dd>' + esc(p.d) + '</dd></div>'; }).join('');
    view.querySelector('.tech-view__body').scrollTop = 0;
  }
  document.addEventListener('click', function (e) {
    var c = e.target.closest('[data-tech]'); if (!c) return;
    opener = c;
    show(+c.dataset.tech);
    document.body.classList.add('has-modal');
    view.showModal();
  });
  view.querySelector('.js-tv-close').addEventListener('click', function () { view.close(); });
  view.querySelector('.js-tv-prev').addEventListener('click', function () { show(cur - 1); });
  view.querySelector('.js-tv-next').addEventListener('click', function () { show(cur + 1); });
  view.addEventListener('click', function (e) { if (e.target === view) view.close(); });
  view.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') show(cur - 1);
    if (e.key === 'ArrowRight') show(cur + 1);
  });
  view.addEventListener('close', function () {
    document.body.classList.remove('has-modal');
    if (opener) opener.focus();
  });
})();
