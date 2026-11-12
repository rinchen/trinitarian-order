(function () {
  var rows = document.querySelectorAll('.feast-table tr[data-month][data-day]');
  var note = document.getElementById('today-note');
  if (!rows.length) return;

  var now = new Date();
  var month = String(now.getMonth() + 1);
  var day = String(now.getDate());
  var found = null;

  rows.forEach(function (row) {
    row.classList.remove('is-today');
    if (row.getAttribute('data-month') === month && row.getAttribute('data-day') === day) {
      found = row;
    }
  });

  if (found) {
    found.classList.add('is-today');
    var feast = found.getAttribute('data-feast') || 'a Trinitarian feast';
    if (note) {
      note.textContent = 'Today, ' + now.toLocaleDateString(undefined, {
        month: 'long',
        day: 'numeric'
      }) + ': ' + feast + '.';
    }
  } else if (note) {
    note.textContent = 'No proper Trinitarian feast is listed for today, ' + now.toLocaleDateString(undefined, {
      month: 'long',
      day: 'numeric'
    }) + '.';
  }
})();
