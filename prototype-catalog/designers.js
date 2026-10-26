/* Прототип «Дизайнерам и архитекторам»: переключатель схем проёмов «Однопольные / Двупольные» */
(function () {
  var tabs = document.querySelectorAll('[data-sch]');
  tabs.forEach(function (b) {
    b.addEventListener('click', function () {
      tabs.forEach(function (t) { var on = t === b; t.classList.toggle('is-active', on); t.setAttribute('aria-selected', on); });
      document.querySelectorAll('[data-sch-list]').forEach(function (l) { l.hidden = l.dataset.schList !== b.dataset.sch; });
    });
  });
})();
