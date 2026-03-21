(function () {
  'use strict';

  var canvas = document.getElementById('spectral-canvas');
  if (!canvas) return;

  var SPECTRAL_BASE = (document.querySelector('meta[name="spectral-base-url"]') || {}).content || 'data/';
  var AUDIO_BASE = (document.querySelector('meta[name="audio-base-url"]') || {}).content || 'audio/';
  var queryParams = new URLSearchParams(window.location.search);
  var spectralOverride = queryParams.get('spectral');
  var debug2D = queryParams.get('debug2d') === '1';
  var height3D = queryParams.get('height3d') !== '0';
  var freqTopHigh = queryParams.get('freqTopHigh') !== '0';
  var vividMode = queryParams.get('vivid') === '1';

  var TRACKS = [
    {
      title: 'Berghain',
      artist: 'ROSAL\u00cdA',
      audioFile: 'berghain.mp3',
      dataFile: 'spectral_data.json',
      ringColor: '#87ceeb',
      theme: 'blue',
      colors: {
        deep: [0.05, 0.08, 0.18],
        mid:  [0.1, 0.5, 0.7],
        bright: [0.85, 0.95, 1.0]
      },
      vividColors: {
        deep: [0.01, 0.02, 0.08],
        mid: [0.05, 0.55, 0.95],
        bright: [1.0, 0.85, 0.2]
      }
    },
    {
      title: 'Fever',
      artist: 'Dua Lipa',
      audioFile: 'fever.mp3',
      dataFile: 'spectral_fever.json',
      ringColor: '#ff4455',
      theme: 'red',
      colors: {
        deep: [0.18, 0.04, 0.06],
        mid:  [0.7, 0.12, 0.15],
        bright: [1.0, 0.75, 0.7]
      },
      vividColors: {
        deep: [0.03, 0.0, 0.06],
        mid: [0.85, 0.1, 0.2],
        bright: [1.0, 0.88, 0.25]
      }
    }
  ];

  var currentTrackIdx = 0;
  var scene, camera, renderer, mesh, clock;
  var ORTHO_FRUSTUM_SIZE = 12;
  var DEBUG_2D_FRUSTUM_SIZE = 14;
  var DEBUG_2D_CAMERA_POS = new THREE.Vector3(0, 16, 0);
  var DEBUG_2D_LOOK_AT = new THREE.Vector3(0, 0, 0);
  var DEBUG_3D_CAMERA_POS = new THREE.Vector3(0, 12, 4);
  var DEBUG_3D_LOOK_AT = new THREE.Vector3(0, 0.4, -2);
  var spectralData = null;
  var currentPositionMs = 0;
  var isPlaying = false;

  var VISIBLE_SECONDS = 10;
  var TERRAIN_WIDTH = 20;
  var TERRAIN_DEPTH = 10;
  var HEIGHT_SCALE = 3.0;
  var LERP_SPEED = 6.0;

  var freqSegs, timeSegs;
  var targetHeights = null;
  var currentHeights = null;

  var audio = document.getElementById('hero-audio');
  var playBtn = document.getElementById('hero-play-btn');
  var nextBtn = document.getElementById('hero-next-btn');
  var timeDisplay = document.getElementById('hero-time');
  var btnRing = document.getElementById('hero-btn-ring');
  var trackTitle = document.getElementById('hero-track-title');
  var trackArtist = document.getElementById('hero-track-artist');
  var playerEl = document.getElementById('hero-player');

  var spectralCache = {};

  function init() {
    clock = new THREE.Clock();

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a2332);
    scene.fog = debug2D ? null : new THREE.FogExp2(0x1a2332, 0.035);

    var aspect = canvas.clientWidth / canvas.clientHeight;
    var frustumSize = debug2D ? DEBUG_2D_FRUSTUM_SIZE : ORTHO_FRUSTUM_SIZE;
    camera = new THREE.OrthographicCamera(
      -frustumSize * aspect / 2,
      frustumSize * aspect / 2,
      frustumSize / 2,
      -frustumSize / 2,
      0.1,
      100
    );
    if (debug2D && !height3D) {
      camera.position.copy(DEBUG_2D_CAMERA_POS);
      camera.lookAt(DEBUG_2D_LOOK_AT);
    } else if (debug2D && height3D) {
      camera.position.copy(DEBUG_3D_CAMERA_POS);
      camera.lookAt(DEBUG_3D_LOOK_AT);
    } else {
      camera.position.set(0, 14, 0.5);
      camera.lookAt(0, 0.2, -2);
    }

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
    animate();
  }

  function bindHeroInfoPanel() {
    var infoBtn = document.getElementById('hero-info-btn');
    var infoPanel = document.getElementById('hero-info-panel');
    var watermark = document.querySelector('.hero-lab-logo-watermark');
    if (!infoBtn || !infoPanel) return;

    function setOpen(open) {
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
    var frustumSize = debug2D ? DEBUG_2D_FRUSTUM_SIZE : ORTHO_FRUSTUM_SIZE;
    camera.left = -frustumSize * aspect / 2;
    camera.right = frustumSize * aspect / 2;
    camera.top = frustumSize / 2;
    camera.bottom = -frustumSize / 2;
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

    var dataUrl = spectralOverride ? (spectralOverride.match(/^https?:\/\//) ? spectralOverride : SPECTRAL_BASE + spectralOverride) : SPECTRAL_BASE + track.dataFile;
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

  function makeFragmentShader(colors, vivid) {
    var d = colors.deep, m = colors.mid, b = colors.bright;
    var floor = vivid ? 0.10 : 0.00;
    var ceil = vivid ? 0.92 : 1.00;
    var gamma = vivid ? 0.75 : 1.00;
    var edgeBase = vivid ? 0.75 : 0.40;
    var edgeGain = vivid ? 0.25 : 0.60;
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
      '  float edge = smoothstep(0.0, 0.08, vUv.x) * smoothstep(0.0, 0.08, 1.0 - vUv.x);',
      '  gl_FragColor = vec4(color * (' + edgeBase.toFixed(2) + ' + ' + edgeGain.toFixed(2) + ' * edge), 1.0);',
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

    var track = TRACKS[currentTrackIdx];
    var palette = vividMode && track.vividColors ? track.vividColors : track.colors;
    var fragShader = makeFragmentShader(palette, vividMode);

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

  function computeTargetHeights(positionMs) {
    if (!spectralData) return;

    var fps = spectralData.fps;
    var totalFrames = spectralData.nFrames;
    var exactFrame = (positionMs / 1000) * fps;
    var nearestFrame = Math.round(exactFrame);

    var cols = timeSegs + 1;
    var rows = freqSegs + 1;
    var start = nearestFrame;

    for (var col = 0; col < cols; col++) {
      var f = start + col;
      for (var row = 0; row < rows; row++) {
        var idx = row * cols + col;
        var srcRow = freqTopHigh ? (spectralData.nMels - 1 - row) : row;
        var freqIdx = Math.min(Math.max(srcRow, 0), spectralData.nMels - 1);
        var amp = sampleAmplitude(f, freqIdx, totalFrames);
        targetHeights[idx] = amp * HEIGHT_SCALE;
      }
    }
  }

  function applyHeights(heights) {
    var positions = mesh.geometry.attributes.position.array;
    var count = heights.length;
    for (var i = 0; i < count; i++) {
      positions[i * 3 + 1] = heights[i];
    }
    mesh.geometry.attributes.position.needsUpdate = true;
  }

  function lerpHeights(dt) {
    var factor = 1 - Math.exp(-LERP_SPEED * dt);
    var count = currentHeights.length;
    var changed = false;
    for (var i = 0; i < count; i++) {
      var cur = currentHeights[i];
      var tgt = targetHeights[i];
      if (cur !== tgt) {
        currentHeights[i] = cur + (tgt - cur) * factor;
        changed = true;
      }
    }
    return changed;
  }

  var normalTimer = 0;
  var NORMAL_INTERVAL = 0.1;
  var zoomFactor = 0;
  var ZOOM_SPEED = 2.5;

  function animate() {
    requestAnimationFrame(animate);
    if (!renderer || !scene || !camera || !spectralData || !mesh) {
      if (renderer && scene && camera) renderer.render(scene, camera);
      return;
    }

    var dt = Math.min(clock.getDelta(), 0.05);
    var elapsed = clock.getElapsedTime();

    var zoomTarget = 0;
    if (debug2D) {
      zoomFactor = 0;
    } else {
      zoomFactor += (zoomTarget - zoomFactor) * (1 - Math.exp(-ZOOM_SPEED * dt));
    }

    if (audio) {
      currentPositionMs = audio.currentTime * 1000;
    }
    computeTargetHeights(currentPositionMs);

    var changed = lerpHeights(dt);
    if (changed) {
      applyHeights(currentHeights);
      normalTimer += dt;
      if (normalTimer >= NORMAL_INTERVAL) {
        mesh.geometry.computeVertexNormals();
        normalTimer = 0;
      }
    }


    if (debug2D && !height3D) {
      camera.position.copy(DEBUG_2D_CAMERA_POS);
      camera.lookAt(DEBUG_2D_LOOK_AT);
    } else if (debug2D && height3D) {
      camera.position.copy(DEBUG_3D_CAMERA_POS);
      camera.lookAt(DEBUG_3D_LOOK_AT);
    } else {
      var idleX = Math.sin(elapsed * 0.08) * 1.6;
      var idleY = 13.8 + Math.sin(elapsed * 0.05) * 0.6;
      var idleZ = 1.0 + Math.cos(elapsed * 0.06) * 0.4;

      var playX = Math.sin(elapsed * 0.06) * 0.5;
      var playY = 12.0 + Math.sin(elapsed * 0.09) * 0.2;
      var playZ = -0.2;

      camera.position.x = idleX + (playX - idleX) * zoomFactor;
      camera.position.y = idleY + (playY - idleY) * zoomFactor;
      camera.position.z = idleZ + (playZ - idleZ) * zoomFactor;
      camera.lookAt(0, 0.2, -2);
    }

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
    } else {
      playIcon.style.display = '';
      pauseIcon.style.display = 'none';
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

    loadTrack(0);

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
