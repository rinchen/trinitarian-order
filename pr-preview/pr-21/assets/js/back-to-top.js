(function () {
  var btn = document.getElementById('back-to-top');
  if (!btn) return;

  var mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  var prefersReduced = mq ? mq.matches : false;
  if (mq) {
    var onChange = function (e) { prefersReduced = e.matches; };
    if (typeof mq.addEventListener === 'function') mq.addEventListener('change', onChange);
    else if (typeof mq.addListener === 'function') mq.addListener(onChange);
  }

  var ticking = false;
  var supportsPreventScroll = false;
  try {
    var opts = Object.defineProperty({}, 'preventScroll', {
      get: function () { supportsPreventScroll = true; return false; }
    });
    document.createElement('div').focus(opts);
  } catch (_err) {
    supportsPreventScroll = false;
  }

  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      try {
        if (window.scrollY > 480) {
          btn.classList.add('is-visible');
          btn.removeAttribute('hidden');
        } else {
          btn.classList.remove('is-visible');
          btn.setAttribute('hidden', '');
        }
      } finally {
        ticking = false;
      }
    });
  }

  btn.setAttribute('hidden', '');
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  btn.addEventListener('click', function () {
    window.scrollTo({
      top: 0,
      behavior: prefersReduced ? 'auto' : 'smooth'
    });
    var main = document.getElementById('main-content');
    if (!main) return;
    if (supportsPreventScroll) {
      main.focus({ preventScroll: true });
    } else if (typeof main.focus === 'function') {
      // Avoid focus() without preventScroll — it can fight smooth scrollTo.
      try { main.setAttribute('tabindex', main.getAttribute('tabindex') || '-1'); } catch (_e) { /* ignore */ }
    }
  });
})();
