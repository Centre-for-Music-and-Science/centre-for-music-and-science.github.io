(function () {
  'use strict';

  var canvas = document.getElementById('spectral-canvas');
  if (!canvas) return;

  var SPECTRAL_BASE = (document.querySelector('meta[name="spectral-base-url"]') || {}).content || 'data/';
  var AUDIO_BASE = (document.querySelector('meta[name="audio-base-url"]') || {}).content || 'audio/';

  var TRACKS = [
    {
      title: 'Cello Suite No. 1',
      artist: 'Fournier (1961) \u2022 Bach',
      audioFile: 'bach-cello-suite-1.mp3',
      dataFile: 'bach-cello-suite-1-spectral.json',
      ringColor: '#87ceeb',
      theme: 'blue',
      colors: {
        deep: [0.102, 0.137, 0.196],
        mid: [0.05, 0.55, 0.95],
        bright: [1.0, 0.85, 0.2]
      }
    }
  ];

  var currentTrackIdx = Math.floor(Math.random() * TRACKS.length);
  var scene, camera, renderer, mesh, clock;
  var ORTHO_FRUSTUM_SIZE = 12;
  var spectralData = null;
  var currentPositionMs = 0;
  var isPlaying = false;

  var VISIBLE_SECONDS = 10;
  var TERRAIN_WIDTH = 20;
  var TERRAIN_DEPTH = 10;
  var HEIGHT_SCALE = 3.0;
  var HEIGHT_GAMMA = 2.0;
  var SMOOTH_PASSES = 1; // 0 = no smoothing, 1 = 3x3 box blur, 2 = 5x5 box blur, etc.

  var freqSegs, timeSegs;
  var targetHeights = null;
  var currentHeights = null;
  var smoothTemp = null;
  var lastStartFrame = null;
  var frameFraction = 0;

  var audio = document.getElementById('hero-audio');
  var playBtn = document.getElementById('hero-play-btn');
  var nextBtn = document.getElementById('hero-next-btn');
  var timeDisplay = document.getElementById('hero-time');
  var btnRing = document.getElementById('hero-btn-ring');
  var trackTitle = document.getElementById('hero-track-title');
  var trackArtist = document.getElementById('hero-track-artist');
  var playerEl = document.getElementById('hero-player');

  var spectralCache = {};
  var infoPanelOpen = false;
  var heroInfoPanelSetOpen = null;
  var postEndedResetTimeout = null;
  var cameraBlend = 0;
  var CAMERA_BLEND_SPEED = 3.0;

  function init() {
    clock = new THREE.Clock();

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a2332);
    scene.fog = new THREE.FogExp2(0x1a2332, 0.035);

    var aspect = canvas.clientWidth / canvas.clientHeight;
    camera = new THREE.OrthographicCamera(
      -ORTHO_FRUSTUM_SIZE * aspect / 2,
      ORTHO_FRUSTUM_SIZE * aspect / 2,
      ORTHO_FRUSTUM_SIZE / 2,
      -ORTHO_FRUSTUM_SIZE / 2,
      0.1,
      100
    );
    camera.position.set(0, 6, 8);
    camera.lookAt(0, 0.5, -2);

    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    scene.add(new THREE.AmbientLight(0x334466, 0.6));
    var dirLight = new THREE.DirectionalLight(0xaaccff, 0.8);
    dirLight.position.set(5, 10, 5);
    scene.add(dirLight);

    window.addEventListener('resize', onResize);

    loadTrack(currentTrackIdx);
    initAudioPlayer();
    bindHeroInfoPanel();

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      renderer.render(scene, camera);
    } else {
      animate();
    }
  }

  function bindHeroInfoPanel() {
    var infoBtn = document.getElementById('hero-info-btn');
    var infoPanel = document.getElementById('hero-info-panel');
    var watermark = document.querySelector('.hero-lab-logo-watermark');
    if (!infoBtn || !infoPanel) return;

    function setOpen(open) {
      infoPanelOpen = open;
      infoBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (watermark) {
        watermark.style.display = open ? 'none' : '';
      }
      if (open) {
        infoPanel.removeAttribute('hidden');
      } else {
        infoPanel.setAttribute('hidden', '');
      }
    }

    heroInfoPanelSetOpen = setOpen;

    infoBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      setOpen(infoPanel.hasAttribute('hidden'));
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !infoPanel.hasAttribute('hidden')) {
        setOpen(false);
        infoBtn.focus();
      }
    });

    document.addEventListener('click', function (e) {
      if (infoPanel.hasAttribute('hidden')) return;
      if (infoPanel.contains(e.target) || infoBtn.contains(e.target)) return;
      setOpen(false);
    });
  }

  function onResize() {
    var w = canvas.parentElement.clientWidth;
    var h = canvas.parentElement.clientHeight;
    var aspect = w / h;
    camera.left = -ORTHO_FRUSTUM_SIZE * aspect / 2;
    camera.right = ORTHO_FRUSTUM_SIZE * aspect / 2;
    camera.top = ORTHO_FRUSTUM_SIZE / 2;
    camera.bottom = -ORTHO_FRUSTUM_SIZE / 2;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }

  function loadTrack(idx) {
    var track = TRACKS[idx];
    currentTrackIdx = idx;

    if (trackTitle) trackTitle.textContent = track.title;
    if (trackArtist) trackArtist.textContent = track.artist;
    if (btnRing) {
      btnRing.style.setProperty('--ring-color', track.ringColor);
      btnRing.style.setProperty('--progress', 0);
    }
    if (timeDisplay) timeDisplay.textContent = '0:00';
    if (playerEl) playerEl.setAttribute('data-theme', track.theme);

    audio.src = AUDIO_BASE + track.audioFile;
    audio.load();

    var dataUrl = SPECTRAL_BASE + track.dataFile;
    if (spectralCache[dataUrl]) {
      spectralData = spectralCache[dataUrl];
      rebuildTerrain();
    } else {
      fetch(dataUrl)
        .then(function (r) { return r.json(); })
        .then(function (data) {
          spectralCache[dataUrl] = data;
          spectralData = data;
          rebuildTerrain();
        })
        .catch(function (err) {
          console.error('Failed to load spectral data:', err);
        });
    }
  }

  function makeFragmentShader(colors) {
    var d = colors.deep, m = colors.mid, b = colors.bright;
    var floor = 0.10;
    var ceil = 0.92;
    var gamma = 0.75;
    return [
      'varying float vHeight;',
      'varying vec2 vUv;',
      'void main() {',
      '  float h = clamp(vHeight / ' + HEIGHT_SCALE.toFixed(1) + ', 0.0, 1.0);',
      '  h = clamp((h - ' + floor.toFixed(2) + ') / (' + ceil.toFixed(2) + ' - ' + floor.toFixed(2) + '), 0.0, 1.0);',
      '  h = pow(h, ' + gamma.toFixed(2) + ');',
      '  vec3 deepC = vec3(' + d[0].toFixed(3) + ', ' + d[1].toFixed(3) + ', ' + d[2].toFixed(3) + ');',
      '  vec3 midC  = vec3(' + m[0].toFixed(3) + ', ' + m[1].toFixed(3) + ', ' + m[2].toFixed(3) + ');',
      '  vec3 brightC = vec3(' + b[0].toFixed(3) + ', ' + b[1].toFixed(3) + ', ' + b[2].toFixed(3) + ');',
      '  vec3 color = h < 0.5',
      '    ? mix(deepC, midC, h * 2.0)',
      '    : mix(midC, brightC, (h - 0.5) * 2.0);',
      '  gl_FragColor = vec4(color, 1.0);',
      '}'
    ].join('\n');
  }

  var vertexShader = [
    'varying float vHeight;',
    'varying vec2 vUv;',
    'void main() {',
    '  vHeight = position.y;',
    '  vUv = uv;',
    '  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);',
    '}'
  ].join('\n');

  function rebuildTerrain() {
    if (mesh) {
      scene.remove(mesh);
      mesh.geometry.dispose();
      mesh.material.dispose();
    }

    freqSegs = spectralData.nMels - 1;
    timeSegs = Math.min(Math.floor(VISIBLE_SECONDS * spectralData.fps), 240);

    var geometry = new THREE.PlaneGeometry(TERRAIN_WIDTH, TERRAIN_DEPTH, timeSegs, freqSegs);
    geometry.rotateX(-Math.PI / 2);

    var vertCount = (timeSegs + 1) * (freqSegs + 1);
    targetHeights = new Float32Array(vertCount);
    currentHeights = new Float32Array(vertCount);
    smoothTemp = new Float32Array(vertCount);
    lastStartFrame = null;
    frameFraction = 0;

    var track = TRACKS[currentTrackIdx];
    var fragShader = makeFragmentShader(track.colors);

    mesh = new THREE.Mesh(geometry, new THREE.ShaderMaterial({
      vertexShader: vertexShader,
      fragmentShader: fragShader,
      side: THREE.DoubleSide
    }));
    scene.add(mesh);

    currentPositionMs = audio ? (audio.currentTime * 1000) : 0;
    computeTargetHeights(currentPositionMs);
    for (var i = 0; i < vertCount; i++) {
      currentHeights[i] = targetHeights[i];
    }
    applyHeights(currentHeights);
    mesh.geometry.computeVertexNormals();
  }

  function sampleAmplitude(frameIdx, freqIdx, totalFrames) {
    if (frameIdx < 0 || frameIdx >= totalFrames) return 0;
    var frame = spectralData.frames[frameIdx];
    if (!frame) return 0;
    return frame[Math.min(freqIdx, spectralData.nMels - 1)] || 0;
  }

  function smoothHeights(heights, cols, rows, passes) {
    for (var p = 0; p < passes; p++) {
      for (var row = 0; row < rows; row++) {
        for (var col = 0; col < cols; col++) {
          var sum = 0;
          var count = 0;
          for (var dr = -1; dr <= 1; dr++) {
            var r = row + dr;
            if (r < 0 || r >= rows) continue;
            for (var dc = -1; dc <= 1; dc++) {
              var c = col + dc;
              if (c < 0 || c >= cols) continue;
              sum += heights[r * cols + c];
              count++;
            }
          }
          smoothTemp[row * cols + col] = sum / count;
        }
      }
      for (var i = 0; i < heights.length; i++) {
        heights[i] = smoothTemp[i];
      }
    }
  }

  function computeTargetHeights(positionMs) {
    if (!spectralData) return;

    var fps = spectralData.fps;
    var totalFrames = spectralData.nFrames;
    var exactFrame = (positionMs / 1000) * fps;
    var startFrame = Math.floor(exactFrame);
    frameFraction = exactFrame - startFrame;

    var cols = timeSegs + 1;
    var rows = freqSegs + 1;
    var start = startFrame;

    for (var col = 0; col < cols; col++) {
      var f = start + col;
      for (var row = 0; row < rows; row++) {
        var idx = row * cols + col;
        var srcRow = spectralData.nMels - 1 - row;
        var freqIdx = Math.min(Math.max(srcRow, 0), spectralData.nMels - 1);
        var amp = sampleAmplitude(f, freqIdx, totalFrames);
        targetHeights[idx] = Math.pow(amp, HEIGHT_GAMMA) * HEIGHT_SCALE;
      }
    }

    if (SMOOTH_PASSES > 0) {
      smoothHeights(targetHeights, cols, rows, SMOOTH_PASSES);
    }

    lastStartFrame = startFrame;
  }

  function applyHeights(heights) {
    var positions = mesh.geometry.attributes.position.array;
    var count = heights.length;
    for (var i = 0; i < count; i++) {
      positions[i * 3 + 1] = heights[i];
    }
    mesh.geometry.attributes.position.needsUpdate = true;
  }

  var normalTimer = 0;
  var NORMAL_INTERVAL = 0.1;

  function animate() {
    requestAnimationFrame(animate);
    if (!renderer || !scene || !camera || !spectralData || !mesh) {
      if (renderer && scene && camera) renderer.render(scene, camera);
      return;
    }

    var dt = Math.min(clock.getDelta(), 0.05);
    var elapsed = clock.getElapsedTime();

    if (audio) {
      currentPositionMs = audio.currentTime * 1000;
    }
    var prevStartFrame = lastStartFrame;
    computeTargetHeights(currentPositionMs);
    if (lastStartFrame !== prevStartFrame) {
      for (var i = 0; i < currentHeights.length; i++) {
        currentHeights[i] = targetHeights[i];
      }
      applyHeights(currentHeights);
      normalTimer += dt;
      if (normalTimer >= NORMAL_INTERVAL) {
        mesh.geometry.computeVertexNormals();
        normalTimer = 0;
      }
    }
    mesh.position.x = -(frameFraction * TERRAIN_WIDTH) / timeSegs;

    var blendTarget = infoPanelOpen ? 1 : 0;
    cameraBlend += (blendTarget - cameraBlend) * (1 - Math.exp(-CAMERA_BLEND_SPEED * dt));

    var phase0 = 0.175 * 4;
    var idleX = Math.sin(-elapsed * 0.08 + phase0) * 3.5;
    var idleY = 9.0 + Math.sin(-elapsed * 0.05 + phase0) * 1.5;
    var idleZ = 8.0 + Math.cos(-elapsed * 0.06 + phase0) * 2.0;

    var detailX = 0;
    var detailY = 8;
    var detailZ = 4.5;

    camera.position.x = idleX + (detailX - idleX) * cameraBlend;
    camera.position.y = idleY + (detailY - idleY) * cameraBlend;
    camera.position.z = idleZ + (detailZ - idleZ) * cameraBlend;

    var lookX = 0 + 0.25 * cameraBlend;
    var lookY = -0.5 + (0.2 - (-0.5)) * cameraBlend;
    camera.lookAt(lookX, lookY, -2);

    renderer.render(scene, camera);
  }

  function formatTime(sec) {
    var m = Math.floor(sec / 60);
    var s = Math.floor(sec % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  function updatePlayerUI() {
    var playIcon = playBtn.querySelector('.play-icon');
    var pauseIcon = playBtn.querySelector('.pause-icon');
    if (isPlaying) {
      playIcon.style.display = 'none';
      pauseIcon.style.display = '';
      playBtn.setAttribute('aria-label', 'Pause');
    } else {
      playIcon.style.display = '';
      pauseIcon.style.display = 'none';
      playBtn.setAttribute('aria-label', 'Play');
    }
  }

  function switchTrack(idx) {
    var wasPlaying = isPlaying;
    audio.pause();
    isPlaying = false;
    loadTrack(idx);
    if (wasPlaying) {
      audio.addEventListener('canplay', function onCanPlay() {
        audio.removeEventListener('canplay', onCanPlay);
        audio.play();
      });
    }
  }

  function initAudioPlayer() {
    if (!audio || !playBtn) return;

    loadTrack(currentTrackIdx);

    playBtn.addEventListener('click', function () {
      if (isPlaying) {
        audio.pause();
      } else {
        audio.play();
      }
    });

    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        var next = (currentTrackIdx + 1) % TRACKS.length;
        switchTrack(next);
      });
    }

    audio.addEventListener('play', function () {
      if (postEndedResetTimeout) {
        clearTimeout(postEndedResetTimeout);
        postEndedResetTimeout = null;
      }
      isPlaying = true;
      updatePlayerUI();
    });

    audio.addEventListener('pause', function () {
      isPlaying = false;
      updatePlayerUI();
    });

    audio.addEventListener('ended', function () {
      isPlaying = false;
      if (btnRing) btnRing.style.setProperty('--progress', 0);
      updatePlayerUI();
      if (postEndedResetTimeout) {
        clearTimeout(postEndedResetTimeout);
      }
      postEndedResetTimeout = setTimeout(function () {
        postEndedResetTimeout = null;
        if (heroInfoPanelSetOpen) {
          heroInfoPanelSetOpen(false);
        }
      }, 1000);
    });

    audio.addEventListener('timeupdate', function () {
      if (timeDisplay) {
        timeDisplay.textContent = formatTime(audio.currentTime);
      }
      if (btnRing && audio.duration) {
        var progress = audio.currentTime / audio.duration;
        btnRing.style.setProperty('--progress', progress);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
