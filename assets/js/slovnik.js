// Slovník pojmů: hledání a filtr podle oblasti. Bez knihoven.
(function () {
  var input = document.getElementById('slovnik-hledat');
  if (!input) return;
  var cards = Array.prototype.slice.call(document.querySelectorAll('.slovnik-card'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.slovnik-group'));
  var buttons = Array.prototype.slice.call(document.querySelectorAll('.slovnik-filter'));
  var count = document.getElementById('slovnik-pocet');
  var empty = document.querySelector('.slovnik-empty');
  var cat = 'vse';

  function fold(s) {
    return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  function update() {
    var q = fold(input.value.trim());
    var visible = 0;
    cards.forEach(function (c) {
      var ok = (cat === 'vse' || c.dataset.cat === cat) && (!q || c.dataset.search.indexOf(q) !== -1);
      c.hidden = !ok;
      if (ok) visible++;
    });
    groups.forEach(function (g) {
      g.hidden = !g.querySelector('.slovnik-card:not([hidden])');
    });
    document.querySelectorAll('.slovnik-az__link[href]').forEach(function (a) {
      var g = document.querySelector(a.getAttribute('href'));
      a.classList.toggle('is-empty', !g || g.hidden);
    });
    count.textContent = visible;
    empty.hidden = visible > 0;
  }

  input.addEventListener('input', update);
  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      cat = b.dataset.cat;
      buttons.forEach(function (x) { x.classList.toggle('is-active', x === b); });
      update();
    });
  });
  var q = new URLSearchParams(location.search).get('q');
  if (q) { input.value = q; update(); }
})();
