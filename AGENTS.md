# Agent notes

## Preview the site when making changes

When making content, layout, or theme changes, start a Hugo preview server so
the organiser can review the result in the browser. Do this as soon as there
is something to look at, and leave the server running.

```bash
hugo server -D --bind 0.0.0.0 --port 1313
```

`--bind 0.0.0.0` is required so cloud-agent port forwarding can reach the
server. Future-dated content is already enabled in `hugo.toml`. Point the
organiser at the specific pages you changed (for example a news post or
publication page), not only the homepage.

If Hugo is missing, install the extended edition as described in the README.

## Posting CMS seminars to external listings

Use these procedures when posting CMS seminar events from `content/events/` to
external listing services:

- `docs/talks-cam-posting.md` for Talks.cam.
- `docs/faculty-music-event-posting.md` for the Faculty of Music website.

The expected workflow is manual browser authentication, agent-assisted form
filling, and organiser review before pressing `Save`, `Publish`, or any
equivalent submit button.

When creating or updating CMS seminar events, include the standard seminar Zoom
link by default unless the organiser gives a different instruction. Use the
`livestream_url` from the most recent CMS seminar as the source of truth; the
current standard link is
`https://zoom.us/j/99433440421?pwd=ZWxCQXFZclRtbjNXa0s2K1Q2REVPZz09`.

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

## Publication BibTeX encoding

- Use Unicode characters directly in publication `bibtex` fields.
  - Example: `Müllensiefen`, `Fouché`, `Pérez-Acosta`.
- Do not use LaTeX accent escapes like `{\"u}`, `{\c{C}}`, or `{\'e}` in
  newly added entries.

## Content title casing

- Use sentence case for content titles and event titles.
- Preserve proper nouns, acronyms, and established source titles as needed.

## Image format preference

- Prefer `.jpg` for new raster images referenced in content pages.
- Keep `.png` only when needed (for transparency, crisp UI/text graphics, or
  compatibility constraints such as favicons); prefer `.svg` for logos/icons
  when available.
- When converting existing assets, update all affected links in `content/`
  files in the same change.

## Topic page thumbnails

Topic pages use an optional `thumbnail` for brochure cards and the detail
header. Put raster assets in `static/images/topics/` and reference them
from front matter, for example:

```yaml
thumbnail: "/images/topics/example.jpg"
thumbnail_credit:
  author: "Example Author"
  license: "CC BY-SA 3.0"
  license_url: "https://creativecommons.org/licenses/by-sa/3.0/"
```

Notes:

- Prefer `.jpg`; resize long edge to about 1600px when importing large sources.
- For transparent sources that should sit on a light background, flatten onto
  white (and use Pillow `ImageOps.pad` when a fixed aspect ratio helps).
- `thumbnail_credit` is optional. When set, credit renders only under the
  detail-page thumbnail, not on brochure cards.
- Do not add smoke tests that hard-code particular topic image paths,
  authors, or license strings. Document the workflow here and in
  `docs/content-authoring.md` / `docs/research-content-architecture.md`
  instead.
