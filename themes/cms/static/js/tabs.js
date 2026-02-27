document.addEventListener('DOMContentLoaded', function () {
  const buttons = document.querySelectorAll('.tab-btn');
  const panels = document.querySelectorAll('.tab-panel');

  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var target = btn.getAttribute('data-tab');

      buttons.forEach(function (b) {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      panels.forEach(function (p) {
        p.classList.remove('active');
        p.setAttribute('aria-hidden', 'true');
      });

      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      var panel = document.getElementById('panel-' + target);
      if (panel) {
        panel.classList.add('active');
        panel.setAttribute('aria-hidden', 'false');
      }
    });
  });

  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var navLinks = document.querySelector('.nav-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
    });
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('open');
      });
    });
  }
});
