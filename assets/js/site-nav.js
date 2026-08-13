(function () {
  var wrap = document.getElementById('site-header-wrap');
  var toggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('site-nav');
  if (!wrap || !toggle || !nav) return;

  function setOpen(open) {
    wrap.classList.toggle('is-nav-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.textContent = open ? 'Close' : 'Menu';
  }

  toggle.addEventListener('click', function () {
    setOpen(!wrap.classList.contains('is-nav-open'));
  });

  nav.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () { setOpen(false); });
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setOpen(false);
  });
})();
