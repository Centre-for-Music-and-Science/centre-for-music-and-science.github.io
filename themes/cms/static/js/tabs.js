(function () {
  function initTabs() {
    document.querySelectorAll('.tabs').forEach(function (tabGroup) {
      if (tabGroup.getAttribute('data-tabs-ready') === 'true') return;
      tabGroup.setAttribute('data-tabs-ready', 'true');

      var buttons = Array.from(tabGroup.querySelectorAll('.tab-btn'));
      var panels = tabGroup.querySelectorAll('.tab-panel');
      var syncHash = tabGroup.hasAttribute('data-sync-hash');

      function activateTab(btn, options) {
        options = options || {};
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

        if (syncHash && options.updateHash !== false) {
          var nextHash = options.hash || ('#' + btn.getAttribute('data-tab'));
          if (window.location.hash !== nextHash) {
            history.replaceState(
              null,
              '',
              window.location.pathname + window.location.search + nextHash
            );
          }
        }
      }

      function activateFromHash(hash) {
        if (!hash || hash === '#') return false;
        var id = decodeURIComponent(hash.slice(1));
        var directBtn = null;
        var i;
        for (i = 0; i < buttons.length; i++) {
          if (buttons[i].getAttribute('data-tab') === id) {
            directBtn = buttons[i];
            break;
          }
        }
        if (directBtn) {
          activateTab(directBtn, { updateHash: false });
          return true;
        }

        var target = document.getElementById(id);
        if (!target || !tabGroup.contains(target)) return false;
        var panel = target.closest('.tab-panel');
        if (!panel || !panel.id || panel.id.indexOf('panel-') !== 0) return false;
        var tabName = panel.id.slice('panel-'.length);
        var panelBtn = null;
        for (i = 0; i < buttons.length; i++) {
          if (buttons[i].getAttribute('data-tab') === tabName) {
            panelBtn = buttons[i];
            break;
          }
        }
        if (!panelBtn) return false;
        activateTab(panelBtn, { updateHash: false });
        window.requestAnimationFrame(function () {
          target.scrollIntoView({ block: 'start' });
        });
        return true;
      }

      buttons.forEach(function (btn) {
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

      if (syncHash) {
        activateFromHash(window.location.hash);
        window.addEventListener('hashchange', function () {
          activateFromHash(window.location.hash);
        });
        window.addEventListener('load', function () {
          activateFromHash(window.location.hash);
        });
      }
    });

    // Show nav logo only after the hero section scrolls out of view.
    // On pages without a hero, the logo is always visible.
    var siteLogo = document.querySelector('.site-logo');
    var heroSection = document.querySelector('.hero');
    if (siteLogo && siteLogo.getAttribute('data-logo-ready') !== 'true') {
      siteLogo.setAttribute('data-logo-ready', 'true');
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
    if (toggle && navLinks && toggle.getAttribute('data-nav-ready') !== 'true') {
      toggle.setAttribute('data-nav-ready', 'true');
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
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTabs);
  } else {
    initTabs();
  }
})();
