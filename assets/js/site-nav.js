(function () {
  var wrap = document.getElementById('site-header-wrap');
  var toggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('site-nav');
  if (!wrap || !toggle || !nav) return;

  function isOpen() {
    return wrap.classList.contains('is-nav-open');
  }

  function setOpen(open) {
    wrap.classList.toggle('is-nav-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.textContent = open ? 'Close' : 'Menu';
    if (!open && nav.contains(document.activeElement)) {
      toggle.focus();
    }
  }

  toggle.addEventListener('click', function () {
    setOpen(!isOpen());
  });

  nav.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () { setOpen(false); });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && isOpen()) setOpen(false);
  });

  document.addEventListener('pointerdown', function (e) {
    if (!isOpen()) return;
    var t = e.target;
    if (t && wrap.contains(t)) return;
    setOpen(false);
  });
})();
