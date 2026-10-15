(function () {
  var btns = document.querySelectorAll('[data-copy-trisagion]');
  if (!btns.length) return;

  var ALLOWED_LANG = { en: true, it: true };
  var COPY_TIMEOUT_MS = 8000;

  function collectText(container, lang) {
    var out = [];
    var prayers;
    if (lang && ALLOWED_LANG[lang]) {
      prayers = container.querySelectorAll('.prayer[lang="' + lang + '"]');
    } else {
      prayers = container.querySelectorAll('.prayer');
    }
    prayers.forEach(function (prayer) {
      var lines = [];
      var label = prayer.getAttribute('data-lang');
      if (label) lines.push(label);
      prayer.querySelectorAll('p, .line, .stanza .line').forEach(function (node) {
        var t = (node.innerText || node.textContent || '').replace(/\s+/g, ' ').trim();
        if (t) lines.push(t);
      });
      if (lines.length) out.push(lines.join('\n'));
    });
    return out.join('\n\n');
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.className = 'copy-fallback';
    document.body.appendChild(ta);
    try {
      ta.focus();
      ta.setSelectionRange(0, text.length);
      return document.execCommand('copy');
    } catch (_err) {
      return false;
    } finally {
      if (ta.parentNode) document.body.removeChild(ta);
    }
  }

  function canUseAsyncClipboard() {
    return Boolean(
      window.isSecureContext &&
      navigator.clipboard &&
      typeof navigator.clipboard.writeText === 'function'
    );
  }

  btns.forEach(function (btn) {
    var original = btn.textContent;
    var timer = null;
    var busy = false;

    function setStatus(msg, isError) {
      if (timer) {
        clearTimeout(timer);
        timer = null;
      }
      btn.setAttribute('aria-live', 'polite');
      btn.textContent = msg;
      if (isError) btn.classList.add('is-error');
      else btn.classList.remove('is-error');
      timer = setTimeout(function () {
        btn.textContent = original;
        btn.classList.remove('is-error');
        busy = false;
        btn.disabled = false;
        timer = null;
      }, 1800);
    }

    function finish(ok) {
      // Keep disabled until status timer clears busy (avoids silent no-ops).
      setStatus(ok ? 'Copied ✓' : 'Copy failed', !ok);
    }

    btn.addEventListener('click', function () {
      if (busy) return;
      busy = true;
      btn.disabled = true;

      var container = document.getElementById(btn.getAttribute('data-copy-trisagion'));
      if (!container) {
        finish(false);
        return;
      }

      var lang = btn.getAttribute('data-copy-lang') || '';
      if (lang && !ALLOWED_LANG[lang]) lang = '';
      var text = collectText(container, lang).trim();
      if (!text) {
        finish(false);
        return;
      }

      if (!canUseAsyncClipboard()) {
        finish(fallbackCopy(text));
        return;
      }

      var settled = false;
      var watchdog = setTimeout(function () {
        if (settled) return;
        settled = true;
        finish(fallbackCopy(text));
      }, COPY_TIMEOUT_MS);

      var done = function (ok) {
        if (settled) return;
        settled = true;
        clearTimeout(watchdog);
        finish(ok);
      };

      try {
        navigator.clipboard.writeText(text).then(function () {
          done(true);
        }).catch(function () {
          done(fallbackCopy(text));
        });
      } catch (_err) {
        done(fallbackCopy(text));
      }
    });
  });
})();
