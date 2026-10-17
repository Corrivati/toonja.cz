/* Forms without Webflow: submit via FormSubmit (https://formsubmit.co) and
   show Webflow's own success / error boxes, exactly like the original site. */
document.querySelectorAll('form[data-ajax-form]').forEach(function (form) {
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    e.stopImmediatePropagation(); // keep webflow.js from posting to Webflow
    var wrap = form.closest('.w-form') || form.parentNode;
    var done = wrap.querySelector('.w-form-done');
    var fail = wrap.querySelector('.w-form-fail');
    var btn = form.querySelector('[type="submit"]');
    var label = btn && btn.value;
    if (btn) { btn.disabled = true; if (btn.dataset.wait) btn.value = btn.dataset.wait; }
    if (fail) fail.style.display = 'none';

    var data = new FormData(form);
    data.append('_subject', 'Nová zpráva z toonja.cz (' + document.title + ')');
    data.append('_template', 'table');
    data.append('_captcha', 'false');

    fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok || String(j.success) !== 'true') throw j; }); })
      .then(function () {
        form.style.display = 'none';
        if (done) done.style.display = 'block';
      })
      .catch(function () {
        if (fail) fail.style.display = 'block';
      })
      .then(function () {
        if (btn) { btn.disabled = false; btn.value = label; }
      });
  }, true);
});
