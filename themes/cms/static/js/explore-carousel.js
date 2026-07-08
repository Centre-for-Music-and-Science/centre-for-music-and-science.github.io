document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-explore-carousel]').forEach(function (carousel) {
    var track = carousel.querySelector('[data-explore-carousel-track]');
    var prevButton = carousel.querySelector('[data-explore-carousel-prev]');
    var nextButton = carousel.querySelector('[data-explore-carousel-next]');

    if (!track || !prevButton || !nextButton) return;

    var frameRequested = false;

    function shuffleSlides() {
      var slides = Array.from(track.querySelectorAll('.explore-highlight-slide'));

      for (var index = slides.length - 1; index > 0; index -= 1) {
        var swapIndex = Math.floor(Math.random() * (index + 1));
        var slide = slides[index];

        slides[index] = slides[swapIndex];
        slides[swapIndex] = slide;
      }

      slides.forEach(function (slide) {
        track.appendChild(slide);
      });
      track.scrollLeft = 0;
    }

    function maxScrollLeft() {
      return Math.max(0, track.scrollWidth - track.clientWidth);
    }

    function updateButtons() {
      var maxScroll = maxScrollLeft();
      var edgeTolerance = 4;

      prevButton.disabled = track.scrollLeft <= edgeTolerance;
      nextButton.disabled = track.scrollLeft >= maxScroll - edgeTolerance;
    }

    function requestButtonUpdate() {
      if (frameRequested) return;

      frameRequested = true;
      window.requestAnimationFrame(function () {
        frameRequested = false;
        updateButtons();
      });
    }

    function scrollStep() {
      var firstSlide = track.querySelector('.explore-highlight-slide');
      var trackStyles = window.getComputedStyle(track);
      var gap = parseFloat(trackStyles.columnGap || trackStyles.gap || '0') || 0;

      if (!firstSlide) return track.clientWidth;

      return firstSlide.getBoundingClientRect().width + gap;
    }

    function scrollBySlide(direction) {
      track.scrollBy({
        left: direction * scrollStep(),
        behavior: 'smooth'
      });
    }

    prevButton.addEventListener('click', function () {
      scrollBySlide(-1);
    });

    nextButton.addEventListener('click', function () {
      scrollBySlide(1);
    });

    track.addEventListener('scroll', requestButtonUpdate, { passive: true });
    window.addEventListener('resize', requestButtonUpdate);
    shuffleSlides();
    updateButtons();
  });
});
