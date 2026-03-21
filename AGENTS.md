# Agent notes

## Adding a new track to the hero banner spectrogram

The hero banner on the homepage displays a 3D terrain visualisation driven by
spectral data. Each track needs three things: a trimmed audio file, a spectral
JSON file, and a JS track definition.

### Steps

1. **Trim the audio** to ~30 seconds using ffmpeg and place it in `static/audio/`.
   Re-encode (don't use `-c copy`) for frame-accurate start/end times:

   ```bash
   ffmpeg -i source.mp3 -ss <start_seconds> -t 30 \
     -codec:a libmp3lame -b:a 320k static/audio/<name>.mp3
   ```

2. **Generate spectral data** using the same parameters as the other tracks.
   Activate the venv first, then run:

   ```bash
   source .venv/bin/activate
   python scripts/generate_spectrogram.py static/audio/<name>.mp3 \
     --profile buap_fft --fps 60 --n-fft 8192 --sample-rate 44100 \
     --window BH7 --scale Mel --f-min 50 --f-max 5000 \
     --target-bins 384 --db-mapping range \
     --display-min-db -40 --display-max-db 20 --decimals 3 \
     --output static/data/<name>-spectral.json
   ```

   This also produces a `.json.gz` alongside the JSON.

3. **Add a track entry** to the `TRACKS` array in
   `themes/cms/static/js/spectral-viz.js`. Each entry has:
   - `title`, `artist` — displayed in the player UI.
   - `audioFile`, `dataFile` — filenames (not paths) in `static/audio/` and
     `static/data/` respectively.
   - `ringColor` — CSS color for the play-button progress ring.
   - `theme` — a label set as `data-theme` on the player element (not
     currently used by CSS, but kept for potential future styling).
   - `colors.deep` — should be `[0.102, 0.137, 0.196]` (i.e. `#1a2332`, the
     scene background) so the terrain blends seamlessly into the background.
   - `colors.mid`, `colors.bright` — mid and highlight colours for the
     terrain gradient.

4. **Update `scripts/generate_spectral_data.sh`** so the track is included
   when bulk-regenerating all spectral data.
