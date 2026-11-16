/* «Хаски» — логика посадочной страницы */
(function () {
  'use strict';

  // ?shot — режим скриншотов: hero фиксированной высоты, всё видно сразу
  if (new URLSearchParams(location.search).has('shot')) document.body.classList.add('shot-mode');

  /* ---------- Шапка: тёмная поверх фото → светлая при прокрутке ---------- */
  var hd = document.getElementById('hd');
  function onScrollHd() { hd.classList.toggle('is-solid', window.scrollY > 40); }
  window.addEventListener('scroll', onScrollHd, { passive: true });
  onScrollHd();

  /* ---------- Появление блоков при прокрутке ---------- */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    document.querySelectorAll('.rv').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('.rv').forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- Анатомия: точки-подсказки (тексты — из инфографики «Хаски PRO») ---------- */
  var HOTS = {
    1: {
      t: '4-камерный стеклопакет',
      p: 'С дистанционной рамкой и дополнительной герметизацией — стекло не становится самым холодным участком двери.',
      s: '4-камерный стеклопакет'
    },
    2: {
      t: 'Коробка 91 мм',
      p: 'Усилена клееным брусом, который обеспечивает жёсткость конструкции.',
      s: 'Коробка — 91 мм'
    },
    3: {
      t: 'Оцинкованная сталь',
      p: 'Полотно и коробка из оцинкованной стали. Атмосферостойкое покрытие с повышенной устойчивостью к влаге и перепадам температур.',
      s: 'Атмосферостойкое покрытие'
    },
    4: {
      t: 'Петли с 3D-регулировкой',
      p: 'Петли (Италия) испытаны на 500 000 циклов открывания. Регулировка в трёх плоскостях — полотно не провисает со временем.',
      s: '500 000 циклов открывания'
    },
    5: {
      t: 'Утепление 84 мм',
      p: 'Пенополистирол: не впитывает влагу и не оседает со временем.',
      s: 'Утеплитель — 84 мм'
    },
    6: {
      t: 'Усиленное полотно',
      p: 'Полотно усилено клееным брусом. Заготовка изготавливается на немецком оборудовании и проходит обработку, которая обеспечивает защиту от влаги.',
      s: 'Клееный брус в полотне'
    },
    7: {
      t: '3 терморазрыва',
      p: 'Два в полотне и один в коробке защищают дверь от наледи и промерзания. Применяются термовставки из композитного материала.',
      s: '2 в полотне + 1 в коробке'
    },
    8: {
      t: '3 контура уплотнителя Cyclone D',
      p: 'Два в полотне и один в коробке обеспечивают плотное прилегание и защиту от продувания.',
      s: 'Уплотнитель Cyclone D'
    },
    9: {
      t: 'Износостойкий порог',
      p: 'С накладкой из нержавеющей стали — не царапается и не боится влаги.',
      s: 'Накладка из нержавеющей стали'
    },
    10: {
      t: 'Термовставка в пороге',
      p: 'Из композитного материала — порог не промерзает и не собирает конденсат.',
      s: 'Композитная термовставка'
    }
  };
  var anatTitle = document.getElementById('anat-title');
  var anatText = document.getElementById('anat-text');
  var anatSpec = document.getElementById('anat-spec');
  var anatNav = document.getElementById('anat-nav');
  var hotEls = document.querySelectorAll('.hot, .pin');

  function setHot(n) {
    var d = HOTS[n];
    if (!d) return;
    anatTitle.textContent = d.t;
    anatText.textContent = d.p;
    anatSpec.textContent = d.s;
    hotEls.forEach(function (h) { h.classList.toggle('is-active', h.dataset.hot === String(n)); });
    anatNav.querySelectorAll('button').forEach(function (b) {
      b.classList.toggle('is-active', b.dataset.hot === String(n));
    });
  }
  Object.keys(HOTS).forEach(function (n) {
    var b = document.createElement('button');
    b.type = 'button';
    b.dataset.hot = n;
    b.textContent = n;
    b.setAttribute('aria-label', HOTS[n].t);
    b.addEventListener('click', function () { setHot(n); });
    anatNav.appendChild(b);
  });
  hotEls.forEach(function (h) {
    h.addEventListener('click', function () { setHot(h.dataset.hot); });
  });
  setHot(7);

  /* ---------- Квиз: подбор под условия дома ---------- */
  var QUESTIONS = [
    { q: 'Вход в дом — сразу с улицы или через тамбур?', opts: ['Сразу с улицы', 'Через тамбур или веранду', 'Пока строимся — не знаю'] },
    { q: 'Как отапливается дом?', opts: ['Постоянно, живём круглый год', 'Периодически — дача, приезжаем', 'Дом ещё без отопления'] },
    { q: 'Какой стиль входной двери вам ближе?', opts: ['Минимализм, гладкое полотно', 'Рейки, фрезеровка, фактура', 'Со стеклом или витражом', 'Пока выбираю — нужен совет'] }
  ];
  var quizBody = document.getElementById('quiz-body');
  var quizQ = document.getElementById('quiz-q');
  var quizOpts = document.getElementById('quiz-opts');
  var quizProgress = document.getElementById('quiz-progress');
  var answers = [];
  var step = 0;

  function renderStep() {
    quizProgress.querySelectorAll('i').forEach(function (el, i) {
      el.classList.toggle('is-done', i <= step);
    });
    if (step >= QUESTIONS.length) {
      quizBody.innerHTML =
        '<div class="quiz__done">' +
        '<p class="quiz__q">Спасибо, этого достаточно для начала.</p>' +
        '<p>Оставьте телефон — подготовим персональный подбор с учётом ваших ответов и рассчитаем стоимость под ваш проём.</p>' +
        '<a class="btn btn--accent" href="#form">Получить персональный подбор</a>' +
        '</div>';
      return;
    }
    quizQ.textContent = QUESTIONS[step].q;
    quizOpts.innerHTML = '';
    QUESTIONS[step].opts.forEach(function (o) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'quiz__opt';
      b.textContent = o;
      b.addEventListener('click', function () {
        answers[step] = o;
        step += 1;
        renderStep();
      });
      quizOpts.appendChild(b);
    });
  }
  renderStep();

  /* ---------- Закреплённая кнопка на телефоне ---------- */
  var sticky = document.getElementById('sticky-cta');
  var formSec = document.getElementById('form');
  function onScrollSticky() {
    var past = window.scrollY > window.innerHeight * 0.8;
    var fr = formSec.getBoundingClientRect();
    var formVisible = fr.top < window.innerHeight && fr.bottom > 0;
    sticky.classList.toggle('is-visible', past && !formVisible);
  }
  window.addEventListener('scroll', onScrollSticky, { passive: true });
  onScrollSticky();

  /* ---------- Форма ---------- */
  var form = document.getElementById('husky-form');
  var fields = document.getElementById('form-fields');
  var done = document.getElementById('form-done');
  var nameIn = document.getElementById('f-name');
  var phoneIn = document.getElementById('f-phone');
  var consentIn = document.getElementById('f-consent');

  function phoneDigits(v) {
    var d = v.replace(/\D/g, '');
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
  phoneIn.addEventListener('input', function () { phoneIn.value = formatPhone(phoneDigits(phoneIn.value)); });
  phoneIn.addEventListener('focus', function () { if (!phoneIn.value) phoneIn.value = '+7 ('; });
  phoneIn.addEventListener('blur', function () { if (phoneDigits(phoneIn.value).length <= 1) phoneIn.value = ''; });

  function setErr(input, errEl, msg) {
    document.getElementById(errEl).textContent = msg || '';
    if (input) input.classList.toggle('is-err', !!msg);
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var ok = true;
    if (nameIn.value.trim().length < 2) { setErr(nameIn, 'err-name', 'Укажите имя.'); ok = false; } else setErr(nameIn, 'err-name');
    if (phoneDigits(phoneIn.value).length !== 11) { setErr(phoneIn, 'err-phone', 'Укажите телефон полностью.'); ok = false; } else setErr(phoneIn, 'err-phone');
    if (!consentIn.checked) { setErr(null, 'err-consent', 'Нужно согласие на обработку данных.'); ok = false; } else setErr(null, 'err-consent');
    if (!ok) return;

    var finish = function () { fields.hidden = true; done.hidden = false; };

    // Локальный предпросмотр (нет PHP): показываем демо-успех без отправки
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') { finish(); return; }

    var fd = new FormData(form);
    fetch('/send.php', { method: 'POST', body: fd })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (res.ok) { finish(); }
        else { setErr(null, 'err-consent', res.error || 'Не получилось отправить. Позвоните нам, пожалуйста.'); }
      })
      .catch(function () { setErr(null, 'err-consent', 'Нет соединения. Позвоните нам, пожалуйста.'); });
  });
})();
