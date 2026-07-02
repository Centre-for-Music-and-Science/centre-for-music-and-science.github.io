(function () {
  var SVG_NS = 'http://www.w3.org/2000/svg';
  var MAP_WIDTH = 960;
  var MAP_HEIGHT = 520;
  var MAP_VISIBLE_HEIGHT = 430;
  var DEFAULT_COUNTRY_ISO = 'GB';
  var DEFAULT_SONG_TITLE = 'Bentayga';
  var DEFAULT_RATING_GROUP = 'US';
  var GROUP_LABELS = {
    AR: 'Spanish speakers',
    EG: 'Arabic speakers',
    EN: 'English speakers',
    ES: 'Spanish speakers',
    FR: 'French speakers',
    GB: 'English speakers',
    KR: 'Korean speakers',
    MX: 'Spanish speakers',
    US: 'English speakers'
  };
  var GROUP_COLORS = {
    EG: '#c99700',
    FR: '#c0392b',
    KR: '#1f6fbf',
    MX: '#1f8a4c',
    US: '#7b1e3a'
  };
  var TAG_TRANSLATIONS = {
    EG: {
      'احتفالي': 'celebratory',
      'الألم': 'pain',
      'الاثاره': 'excitement',
      'الاستمتاع': 'enjoyment',
      'الحب': 'love',
      'الحزن': 'sadness',
      'الحماس': 'enthusiasm',
      'الدفئ': 'warmth',
      'الرومانسية': 'romance',
      'السعادة': 'happiness',
      'المرح': 'fun',
      'الهدوء': 'calmness',
      'بهجة': 'delight',
      'رقص': 'dance',
      'شباب': 'youth',
      'صاخب': 'loud',
      'عشق': 'passion',
      'فرح': 'joy',
      'قوة': 'strength',
      'نشاط': 'active'
    },
    FR: {
      'rythmé': 'rhythmic',
      'rythme': 'rhythmic',
      'dansant': 'dancing',
      'entrainant': 'catchy',
      'entraînant': 'catchy',
      'joie': 'joy',
      'festif': 'festive',
      'étranger': 'foreign',
      'etranger': 'foreign',
      'nostalgie': 'nostalgia',
      'joyeux': 'happy',
      'amour': 'love',
      'cool': 'cool',
      'moderne': 'modern',
      'latino': 'latino',
      'calme': 'calm',
      'agréable': 'pleasant',
      'agreable': 'pleasant',
      'doux': 'soft',
      'triste': 'sad',
      'ensoleillé': 'sunny',
      'ensoleille': 'sunny',
      'amusant': 'fun',
      'bonheur': 'happiness',
      'mélancolie': 'melancholy',
      'melancolie': 'melancholy'
    },
    KR: {
      '리듬감있는': 'rhythmic',
      '신나는': 'exciting',
      '애절한': 'sorrowful',
      '흥겨운': 'cheerful',
      '즐거운': 'pleasant',
      '호소하는': 'appealing',
      '경쾌한': 'lively',
      '그리움': 'longing',
      '그리운': 'longing',
      '슬픈': 'sad',
      '감미로운': 'sweet',
      '강렬한': 'intense',
      '이국적인': 'exotic',
      '감정적인': 'emotional',
      '잔잔한': 'calm',
      '부드러운': 'soft',
      '자유로운': 'free',
      '활기찬': 'energetic',
      '기분좋은': 'feel-good',
      '사랑스러운': 'lovely',
      '평화로운': 'peaceful',
      '평화롭다': 'peaceful'
    },
    MX: {
      'alegría': 'joy',
      'alegria': 'joy',
      'baile': 'dance',
      'amor': 'love',
      'felicidad': 'happiness',
      'fiesta': 'party',
      'ritmo': 'rhythm',
      'relajacion': 'relaxation',
      'relajación': 'relaxation',
      'tranquilidad': 'tranquility',
      'nostalgia': 'nostalgia',
      'emocion': 'emotion',
      'emoción': 'emotion',
      'tristeza': 'sadness',
      'pasión': 'passion',
      'pasion': 'passion',
      'romance': 'romance',
      'movida': 'lively',
      'sensualidad': 'sensuality',
      'raro': 'strange',
      'esperanza': 'hope',
      'melancolia': 'melancholy',
      'melancolía': 'melancholy',
      'diversion': 'fun',
      'diversión': 'fun',
      'paz': 'peace'
    }
  };

  function initGlobalMoodExplorer() {
    var root = document.querySelector('.globalmood-explorer');
    if (!root) return;

    var state = {
      countries: [],
      countryByIso: new Map(),
      countryByName: new Map(),
      ratingsByVideo: new Map(),
      selectedCountryKey: '',
      selectedSongId: '',
      selectedGroup: ''
    };

    var els = {
      app: root.querySelector('.globalmood-app'),
      button: root.querySelector('.globalmood-load-btn'),
      status: root.querySelector('.globalmood-status'),
      map: root.querySelector('.globalmood-map'),
      countryHeading: root.querySelector('#globalmood-country-heading'),
      countrySummary: root.querySelector('.globalmood-country-summary'),
      songList: root.querySelector('.globalmood-song-list'),
      songEmpty: root.querySelector('.globalmood-song-empty'),
      songDetail: root.querySelector('.globalmood-song-detail'),
      songTitle: root.querySelector('.globalmood-song-title'),
      songArtist: root.querySelector('.globalmood-song-artist'),
      video: root.querySelector('.globalmood-video'),
      ratingsNote: root.querySelector('.globalmood-ratings-note'),
      languageTabs: root.querySelector('.globalmood-language-tabs'),
      ratingBars: root.querySelector('.globalmood-rating-bars')
    };

    els.button.addEventListener('click', function () {
      loadExplorer(root, els, state);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGlobalMoodExplorer);
  } else {
    initGlobalMoodExplorer();
  }

  function loadExplorer(root, els, state) {
    els.button.disabled = true;
    setStatus(els, 'Loading metadata, ratings, and map data...', false);

    Promise.all([
      fetchText(root.dataset.songUrl),
      fetchText(root.dataset.ratingsUrl),
      fetchJson(root.dataset.mapUrl)
    ])
      .then(function (results) {
        buildSongIndex(parseCsv(results[0]), state);
        buildRatingIndex(parseCsv(results[1]), state);
        renderMap(results[2], els, state);
        els.app.hidden = false;

        if (state.countries.length > 0) {
          selectDefaultCountryAndSong(els, state);
          setStatus(
            els,
            'Loaded ' + countSongs(state.countries) + ' songs from ' + state.countries.length + ' countries.',
            false
          );
        } else {
          setStatus(els, 'The public metadata file loaded, but no songs were found.', true);
        }
      })
      .catch(function (error) {
        els.button.disabled = false;
        setStatus(els, 'Unable to load the explorer data: ' + error.message, true);
      });
  }

  function fetchText(url) {
    return fetch(url).then(function (response) {
      if (!response.ok) throw new Error('Failed to fetch ' + url);
      return response.text();
    });
  }

  function fetchJson(url) {
    return fetch(url).then(function (response) {
      if (!response.ok) throw new Error('Failed to fetch ' + url);
      return response.json();
    });
  }

  function setStatus(els, message, isError) {
    els.status.textContent = message;
    els.status.classList.toggle('is-error', isError);
  }

  function parseCsv(text) {
    var rows = [];
    var row = [];
    var field = '';
    var inQuotes = false;
    var i;

    text = text.replace(/^\uFEFF/, '');

    for (i = 0; i < text.length; i += 1) {
      var char = text[i];
      var next = text[i + 1];

      if (inQuotes) {
        if (char === '"' && next === '"') {
          field += '"';
          i += 1;
        } else if (char === '"') {
          inQuotes = false;
        } else {
          field += char;
        }
      } else if (char === '"') {
        inQuotes = true;
      } else if (char === ',') {
        row.push(field);
        field = '';
      } else if (char === '\n') {
        row.push(field);
        rows.push(row);
        row = [];
        field = '';
      } else if (char !== '\r') {
        field += char;
      }
    }

    if (field || row.length) {
      row.push(field);
      rows.push(row);
    }

    if (!rows.length) return [];

    var headers = rows.shift().map(function (header) {
      return header.trim();
    });

    return rows
      .filter(function (values) {
        return values.some(function (value) {
          return value.trim() !== '';
        });
      })
      .map(function (values) {
        var item = {};
        headers.forEach(function (header, index) {
          item[header] = values[index] || '';
        });
        return item;
      });
  }

  function buildSongIndex(rows, state) {
    var byIso = new Map();

    rows.forEach(function (row) {
      var iso = clean(row.iso2).toUpperCase();
      var countryName = clean(row.country);
      var videoId = clean(row.videoID);

      if (!countryName || !videoId) return;

      var key = iso || normalizeName(countryName);
      if (!byIso.has(key)) {
        byIso.set(key, {
          key: key,
          iso2: iso,
          name: countryName,
          songs: []
        });
      }

      byIso.get(key).songs.push({
        videoId: videoId,
        country: countryName,
        iso2: iso,
        title: clean(row.song) || 'Untitled song',
        artist: clean(row.artist) || 'Unknown artist'
      });
    });

    state.countries = Array.from(byIso.values())
      .map(function (country) {
        country.songs.sort(function (a, b) {
          return a.title.localeCompare(b.title);
        });
        return country;
      })
      .sort(function (a, b) {
        return a.name.localeCompare(b.name);
      });

    state.countries.forEach(function (country) {
      if (country.iso2) state.countryByIso.set(country.iso2, country);
      state.countryByName.set(normalizeName(country.name), country);
    });
  }

  function buildRatingIndex(rows, state) {
    rows.forEach(function (row) {
      var videoId = clean(row.videoID);
      var group = clean(row.country).toUpperCase();
      var tag = clean(row.tag);
      var mean = parseFloat(row.mean_rating);

      if (!videoId || !group || !tag || Number.isNaN(mean)) return;

      if (!state.ratingsByVideo.has(videoId)) {
        state.ratingsByVideo.set(videoId, new Map());
      }

      var byGroup = state.ratingsByVideo.get(videoId);
      if (!byGroup.has(group)) byGroup.set(group, []);

      byGroup.get(group).push({
        tag: tag,
        mean: mean,
        sd: parseFloat(row.sd_rating),
        n: parseInt(row.n_ratings, 10)
      });
    });

    state.ratingsByVideo.forEach(function (byGroup) {
      byGroup.forEach(function (ratings) {
        ratings.sort(function (a, b) {
          return b.mean - a.mean || a.tag.localeCompare(b.tag);
        });
      });
    });
  }

  function renderMap(geojson, els, state) {
    var svg = document.createElementNS(SVG_NS, 'svg');
    var tooltip = document.createElement('div');

    svg.setAttribute('viewBox', '0 0 ' + MAP_WIDTH + ' ' + MAP_VISIBLE_HEIGHT);
    svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', 'World map with GlobalMood countries highlighted');

    tooltip.className = 'globalmood-map-tooltip';
    tooltip.hidden = true;

    geojson.features.forEach(function (feature) {
      var props = feature.properties || {};
      var iso = clean(props.ISO_A2 || props.ISO_A2_EH).toUpperCase();
      var name = clean(props.NAME || props.NAME_LONG || props.ADMIN);
      var country = state.countryByIso.get(iso) || state.countryByName.get(normalizeName(name));
      var pathData = geometryToPath(feature.geometry);

      if (iso === 'AQ' || normalizeName(name) === 'antarctica') return;
      if (!pathData) return;

      var path = document.createElementNS(SVG_NS, 'path');
      path.setAttribute('d', pathData);
      path.setAttribute('class', 'globalmood-country' + (country ? ' is-available' : ''));
      path.setAttribute('aria-label', country ? country.name + ', ' + country.songs.length + ' songs' : name);

      var title = document.createElementNS(SVG_NS, 'title');
      title.textContent = country ? country.name + ' (' + country.songs.length + ' songs)' : name;
      path.appendChild(title);

      if (country) {
        path.dataset.countryKey = country.key;
        path.setAttribute('role', 'button');
        path.setAttribute('tabindex', '0');
        path.addEventListener('mousedown', function (event) {
          event.preventDefault();
        });
        path.addEventListener('click', function () {
          selectCountry(country.key, els, state);
          path.blur();
        });
        path.addEventListener('keydown', function (event) {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            selectCountry(country.key, els, state);
          }
        });
      }

      path.addEventListener('mouseenter', function (event) {
        showMapTooltip(tooltip, event, country ? country.name : name);
      });
      path.addEventListener('mousemove', function (event) {
        positionMapTooltip(tooltip, event);
      });
      path.addEventListener('mouseleave', function () {
        tooltip.hidden = true;
      });

      svg.appendChild(path);
    });

    els.map.replaceChildren(svg, tooltip);
  }

  function showMapTooltip(tooltip, event, label) {
    tooltip.textContent = label;
    tooltip.hidden = false;
    positionMapTooltip(tooltip, event);
  }

  function positionMapTooltip(tooltip, event) {
    var container = tooltip.parentElement.getBoundingClientRect();
    tooltip.style.left = (event.clientX - container.left + 12) + 'px';
    tooltip.style.top = (event.clientY - container.top + 12) + 'px';
  }

  function geometryToPath(geometry) {
    if (!geometry) return '';
    if (geometry.type === 'Polygon') {
      return polygonToPath(geometry.coordinates);
    }
    if (geometry.type === 'MultiPolygon') {
      return geometry.coordinates.map(polygonToPath).join(' ');
    }
    return '';
  }

  function polygonToPath(polygon) {
    return polygon
      .map(function (ring) {
        return ring
          .map(function (coord, index) {
            var point = project(coord);
            return (index === 0 ? 'M' : 'L') + point[0].toFixed(2) + ' ' + point[1].toFixed(2);
          })
          .join(' ') + ' Z';
      })
      .join(' ');
  }

  function project(coord) {
    var lon = coord[0];
    var lat = coord[1];
    return [
      ((lon + 180) / 360) * MAP_WIDTH,
      ((90 - lat) / 180) * MAP_HEIGHT
    ];
  }

  function selectCountry(countryKey, els, state) {
    var country = state.countries.find(function (item) {
      return item.key === countryKey;
    });
    if (!country) return;

    state.selectedCountryKey = country.key;
    state.selectedSongId = '';
    state.selectedGroup = '';

    els.map.querySelectorAll('.globalmood-country').forEach(function (path) {
      path.classList.toggle('is-selected', path.dataset.countryKey === country.key);
    });

    els.countryHeading.textContent = 'Songs uniquely popular in ' + country.name;
    els.countrySummary.textContent = 'These are 20 songs that were not popular elsewhere other than ' + country.name + '.';
    renderSongList(country, els, state);

    if (country.songs.length) {
      selectSong(country.songs[0].videoId, els, state);
    }
  }

  function selectDefaultCountryAndSong(els, state) {
    var country = state.countryByIso.get(DEFAULT_COUNTRY_ISO) || state.countries[0];
    var defaultSong;

    selectCountry(country.key, els, state);

    defaultSong = country.songs.find(function (song) {
      return normalizeName(song.title) === normalizeName(DEFAULT_SONG_TITLE);
    });

    if (defaultSong) {
      selectSong(defaultSong.videoId, els, state);
    }
  }

  function renderSongList(country, els, state) {
    els.songList.replaceChildren();

    country.songs.forEach(function (song) {
      var button = document.createElement('button');
      var title = document.createElement('span');
      var meta = document.createElement('span');

      button.type = 'button';
      button.className = 'globalmood-song-btn';
      button.dataset.videoId = song.videoId;
      button.setAttribute('role', 'listitem');

      title.className = 'globalmood-song-name';
      title.textContent = song.title;
      meta.className = 'globalmood-song-meta';
      meta.textContent = song.artist;

      button.append(title, meta);
      button.addEventListener('click', function () {
        selectSong(song.videoId, els, state);
      });

      els.songList.appendChild(button);
    });
  }

  function selectSong(videoId, els, state) {
    var country = state.countries.find(function (item) {
      return item.key === state.selectedCountryKey;
    });
    if (!country) return;

    var song = country.songs.find(function (item) {
      return item.videoId === videoId;
    });
    if (!song) return;

    state.selectedSongId = videoId;
    state.selectedGroup = '';

    els.songList.querySelectorAll('.globalmood-song-btn').forEach(function (button) {
      button.classList.toggle('is-selected', button.dataset.videoId === videoId);
    });

    els.songEmpty.hidden = true;
    els.songDetail.hidden = false;
    els.songTitle.textContent = song.title;
    els.songArtist.textContent = song.artist + ' · ' + song.country;
    renderVideo(song, els);
    renderRatingGroups(song.videoId, els, state);
  }

  function renderVideo(song, els) {
    els.video.replaceChildren();

    if (!/^[A-Za-z0-9_-]{6,}$/.test(song.videoId)) {
      var message = document.createElement('p');
      message.className = 'globalmood-song-empty';
      message.textContent = 'This song does not have a valid YouTube video ID.';
      els.video.appendChild(message);
      return;
    }

    var iframe = document.createElement('iframe');
    iframe.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(song.videoId);
    iframe.title = 'YouTube preview for ' + song.title;
    iframe.loading = 'lazy';
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    iframe.allowFullscreen = true;
    els.video.appendChild(iframe);
  }

  function renderRatingGroups(videoId, els, state) {
    var byGroup = state.ratingsByVideo.get(videoId);
    var groups = byGroup ? Array.from(byGroup.keys()).sort() : [];

    els.languageTabs.replaceChildren();
    els.ratingBars.replaceChildren();

    if (!groups.length) {
      els.ratingsNote.textContent = 'No aggregated ratings are currently available for this song in the public ratings file.';
      return;
    }

    state.selectedGroup = state.selectedGroup && groups.indexOf(state.selectedGroup) !== -1
      ? state.selectedGroup
      : (groups.indexOf(DEFAULT_RATING_GROUP) !== -1 ? DEFAULT_RATING_GROUP : groups[0]);

    els.ratingBars.style.setProperty('--globalmood-rating-color', groupColor(state.selectedGroup));

    groups.forEach(function (group) {
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'globalmood-language-btn';
      button.textContent = groupLabel(group);
      button.style.setProperty('--globalmood-group-color', groupColor(group));
      button.setAttribute('role', 'tab');
      button.setAttribute('aria-selected', group === state.selectedGroup ? 'true' : 'false');
      button.classList.toggle('is-selected', group === state.selectedGroup);
      button.addEventListener('click', function () {
        state.selectedGroup = group;
        renderRatingGroups(videoId, els, state);
      });
      els.languageTabs.appendChild(button);
    });

    els.ratingsNote.textContent = 'Showing ' + groupLabel(state.selectedGroup) + '. ' +
      groups.length + ' rating group' + (groups.length === 1 ? ' is' : 's are') +
      ' available in the public file for this song.';

    renderRatingBars(byGroup.get(state.selectedGroup), els, state.selectedGroup);
  }

  function renderRatingBars(ratings, els, group) {
    els.ratingBars.replaceChildren();

    ratings.forEach(function (rating) {
      var row = document.createElement('div');
      var label = document.createElement('div');
      var tag = document.createElement('span');
      var value = document.createElement('span');
      var track = document.createElement('div');
      var fill = document.createElement('div');
      var width = Math.max(0, Math.min(100, (rating.mean / 5) * 100));
      var details = rating.mean.toFixed(2) + ' / 5';

      if (!Number.isNaN(rating.n)) details += ' · n=' + rating.n;
      if (!Number.isNaN(rating.sd)) details += ' · SD=' + rating.sd.toFixed(2);

      row.className = 'globalmood-rating-row';
      label.className = 'globalmood-rating-label';
      tag.className = 'globalmood-rating-tag';
      value.className = 'globalmood-rating-value';
      track.className = 'globalmood-rating-track';
      fill.className = 'globalmood-rating-fill';

      tag.textContent = translatedTagLabel(group, rating.tag);
      value.textContent = details;
      fill.style.width = width + '%';

      label.append(tag, value);
      track.appendChild(fill);
      row.append(label, track);
      els.ratingBars.appendChild(row);
    });
  }

  function countSongs(countries) {
    return countries.reduce(function (total, country) {
      return total + country.songs.length;
    }, 0);
  }

  function groupLabel(group) {
    return (GROUP_LABELS[group] || 'Rating group') + ' (' + group + ')';
  }

  function groupColor(group) {
    return GROUP_COLORS[group] || '#2a73b2';
  }

  function translatedTagLabel(group, tag) {
    var translations = TAG_TRANSLATIONS[group];
    var translation = translations && (translations[tag] || translations[clean(tag).toLowerCase()]);

    if (!translation) return tag;
    return tag + ' (' + translation + ')';
  }

  function clean(value) {
    return String(value || '').trim();
  }

  function normalizeName(value) {
    return clean(value)
      .toLowerCase()
      .replace(/&/g, 'and')
      .replace(/[^a-z0-9]+/g, ' ')
      .trim();
  }
}());
