document.addEventListener('DOMContentLoaded', function () {
  var modal = document.getElementById('explore-video-modal');
  var trigger = document.querySelector('.explore-video-trigger');

  if (!modal || !trigger) return;

  var frame = modal.querySelector('[data-explore-video-frame]');
  var closeControls = modal.querySelectorAll('[data-explore-video-close]');
  var previousFocus = null;
  var focusableSelector = 'a[href], button:not([disabled]), iframe, [tabindex]:not([tabindex="-1"])';

  function videoEmbedUrl(videoId) {
    return 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(videoId) + '?autoplay=1&rel=0';
  }

  function clearFrame() {
    if (frame) {
      frame.replaceChildren();
    }
  }

  function closeModal() {
    clearFrame();
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('explore-video-is-open');

    if (previousFocus && typeof previousFocus.focus === 'function') {
      previousFocus.focus();
    }
  }

  function openModal() {
    var videoId = trigger.getAttribute('data-video-id') || '';
    var videoTitle = trigger.getAttribute('data-video-title') || 'Video';

    if (!/^[A-Za-z0-9_-]{6,}$/.test(videoId) || !frame) return;

    previousFocus = document.activeElement;
    clearFrame();

    var iframe = document.createElement('iframe');
    iframe.src = videoEmbedUrl(videoId);
    iframe.title = 'YouTube video: ' + videoTitle;
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    iframe.allowFullscreen = true;
    frame.appendChild(iframe);

    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('explore-video-is-open');

    var firstFocusable = modal.querySelector(focusableSelector);
    if (firstFocusable) {
      firstFocusable.focus();
    }
  }

  trigger.addEventListener('click', openModal);

  closeControls.forEach(function (control) {
    control.addEventListener('click', closeModal);
  });

  document.addEventListener('keydown', function (event) {
    if (modal.hidden) return;

    if (event.key === 'Escape') {
      event.preventDefault();
      closeModal();
      return;
    }

    if (event.key !== 'Tab') return;

    var focusable = Array.from(modal.querySelectorAll(focusableSelector));
    if (!focusable.length) return;

    var first = focusable[0];
    var last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
});
