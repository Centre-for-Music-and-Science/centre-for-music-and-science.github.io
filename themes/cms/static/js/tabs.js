document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.tabs').forEach(function (tabGroup) {
    var buttons = Array.from(tabGroup.querySelectorAll('.tab-btn'));
    var panels = tabGroup.querySelectorAll('.tab-panel');

    function activateTab(btn) {
      buttons.forEach(function (b) {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
        b.setAttribute('tabindex', '-1');
      });
      panels.forEach(function (p) {
        p.classList.remove('active');
        p.setAttribute('aria-hidden', 'true');
      });

      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      btn.setAttribute('tabindex', '0');

      var panel = document.getElementById('panel-' + btn.getAttribute('data-tab'));
      if (panel) {
        panel.classList.add('active');
        panel.setAttribute('aria-hidden', 'false');
      }
    }

    buttons.forEach(function (btn, index) {
      // Initialise tabindex: only the active tab is in the tab sequence.
      btn.setAttribute('tabindex', btn.classList.contains('active') ? '0' : '-1');

      btn.addEventListener('click', function () {
        activateTab(btn);
      });

      btn.addEventListener('keydown', function (e) {
        var currentIndex = buttons.indexOf(document.activeElement);
        var newIndex;

        if (e.key === 'ArrowRight') {
          newIndex = (currentIndex + 1) % buttons.length;
        } else if (e.key === 'ArrowLeft') {
          newIndex = (currentIndex - 1 + buttons.length) % buttons.length;
        } else if (e.key === 'Home') {
          newIndex = 0;
        } else if (e.key === 'End') {
          newIndex = buttons.length - 1;
        } else {
          return;
        }

        e.preventDefault();
        activateTab(buttons[newIndex]);
        buttons[newIndex].focus();
      });
    });
  });

  // Show nav logo only after the hero section scrolls out of view.
  // On pages without a hero, the logo is always visible.
  var siteLogo = document.querySelector('.site-logo');
  var heroSection = document.querySelector('.hero');
  if (siteLogo) {
    if (heroSection && typeof IntersectionObserver !== 'undefined') {
      new IntersectionObserver(function (entries) {
        siteLogo.classList.toggle('site-logo--visible', !entries[0].isIntersecting);
      }, { threshold: 0.1 }).observe(heroSection);
    } else {
      siteLogo.classList.add('site-logo--visible');
    }
  }

  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var navLinks = document.querySelector('.nav-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      var isOpen = navLinks.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }
});
