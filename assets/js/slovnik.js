// Slovník pojmů: filtr podle oblasti. Bez knihoven.
(function () {
  var buttons = Array.prototype.slice.call(document.querySelectorAll('.slovnik-filter'));
  if (!buttons.length) return;
  var cards = Array.prototype.slice.call(document.querySelectorAll('.slovnik-card'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.slovnik-group'));
  var count = document.getElementById('slovnik-pocet');

  function update(cat) {
    var visible = 0;
    cards.forEach(function (c) {
      var ok = cat === 'vse' || c.dataset.cat === cat;
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
    if (count) count.textContent = visible;
  }

  buttons.forEach(function (b) {
    b.addEventListener('click', function () {
      buttons.forEach(function (x) { x.classList.toggle('is-active', x === b); });
      update(b.dataset.cat);
    });
  });
})();
