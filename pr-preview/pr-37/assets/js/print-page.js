(function () {
  var buttons = document.querySelectorAll('[data-print]');
  if (!buttons.length) return;

  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      window.print();
    });
  });
})();
