(function () {
  var btns = document.querySelectorAll('[data-copy-trisagion]');
  if (!btns.length) return;

  function collectText(container, lang) {
    var out = [];
    var selector = lang ? '.prayer[lang="' + lang + '"]' : '.prayer';
    var prayers = container.querySelectorAll(selector);
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
    ta.style.position = 'fixed';
    ta.style.top = '0';
    ta.style.left = '0';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.focus();
    ta.setSelectionRange(0, text.length);
    var ok = false;
    try {
      ok = document.execCommand('copy');
    } catch (_err) {
      ok = false;
    }
    document.body.removeChild(ta);
    return ok;
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
        timer = null;
      }, 1800);
    }

    btn.addEventListener('click', function () {
      if (busy) return;
      busy = true;
      btn.disabled = true;

      var container = document.getElementById(btn.getAttribute('data-copy-trisagion'));
      if (!container) {
        btn.disabled = false;
        setStatus('Copy failed', true);
        return;
      }

      var lang = btn.getAttribute('data-copy-lang') || '';
      var text = collectText(container, lang).trim();
      if (!text) {
        btn.disabled = false;
        setStatus('Copy failed', true);
        return;
      }

      var finish = function (ok) {
        btn.disabled = false;
        setStatus(ok ? 'Copied ✓' : 'Copy failed', !ok);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          finish(true);
        }).catch(function () {
          finish(fallbackCopy(text));
        });
      } else {
        finish(fallbackCopy(text));
      }
    });
  });
})();
