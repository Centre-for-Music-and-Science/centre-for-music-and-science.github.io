# Centre for Music and Science — Website

The website for the [Centre for Music and Science](https://centre-for-music-and-science.github.io) at the University of Cambridge, built with [Hugo](https://gohugo.io/).

For now, the old website is still visible at https://old-cms.mus.cam.ac.uk/, just in case people need to retrieve old content.

## Prerequisites

Install Hugo **extended** edition (v0.157.0 or later):

```bash
# macOS
brew install hugo

# Linux (Debian/Ubuntu) — download from GitHub releases
wget -O hugo.deb https://github.com/gohugoio/hugo/releases/download/v0.157.0/hugo_extended_0.157.0_linux-amd64.deb
sudo dpkg -i hugo.deb

# Verify
hugo version
```

For site development only, no other dependencies are required. The theme is included in the repository under `themes/cms/`.

Optional for maintenance scripts and tests:

- Python 3.10+
- `venv` module (usually bundled with Python)

## Local development

Clone the repository and start the dev server:

```bash
git clone https://github.com/Centre-for-Music-and-Science/centre-for-music-and-science.github.io.git
cd centre-for-music-and-science.github.io
hugo server -D
```

The site will be available at **<http://localhost:1313/>**. The server watches for file changes and reloads automatically.

Useful flags:

| Flag | Description |
| ---- | ----------- |
| `-D` | Include draft content |
| `--buildFuture` | Include future-dated content (enabled by default in `hugo.toml`) |
| `--disableFastRender` | Full rebuild on every change (slower but avoids stale state) |
| `--port 1414` | Use a different port |

## Project structure

```text
.
├── content/             # Markdown content
│   ├── people/          # Lab members
│   ├── projects/        # Research projects
│   ├── themes/          # Research theme groupings
│   ├── publications/    # Publication entries
│   ├── groups/          # Research groups
│   ├── methods/         # Methods pages
│   ├── news/            # News posts
│   ├── datasets/        # Dataset pages
│   ├── facilities/      # Facilities info
│   └── applicants/      # Applicant info (PhD, MPhil, etc.)
├── data/                # YAML data files (lab authors, past members, videos)
├── static/              # Static assets (images, audio, JSON)
├── scripts/             # Publication + spectrogram maintenance scripts
├── tests/               # Python tests for maintenance tooling
├── themes/cms/          # Custom Hugo theme
│   ├── layouts/         # HTML templates
│   └── static/          # Theme CSS and JS
├── hugo.toml            # Site configuration
└── .github/workflows/   # GitHub Actions deployment
```

## Adding content

### New publication

Create a file in `content/publications/` with a `bibtex` entry:

```yaml
---
title: "Paper Title"
date: 2026-01-15
stub_only: false
projects:
  - "project-slug"
bibtex: |-
  @article{paperkey2026,
    author = {Author, A. and Author, B. and Author, C.},
    title = {Paper title},
    journal = {Journal Name},
    year = {2026},
    doi = {10.xxxx/xxxxx}
  }
---
```

Then run:

```bash
python scripts/generate_publication_citations.py
python scripts/fetch_publication_abstracts.py
```

These scripts populate generated citation fields (`citation_apa`, `citation_mla`, etc.), `authors`, `journal`, `doi`, and (where available) `abstract`.

### New person

To add a new person, complete these steps:

1. Create a new Markdown file in `content/people/` using the person's slug, for example `content/people/jane-doe.md`.
2. Add front matter for the person's name, status, title fields, category, ordering, and contact details.
3. Add an optional short bio below the front matter.
4. Place the profile photo in `static/images/people/`.
5. Run `hugo server -D` and check both the homepage people cards and the person's detail page.

Recommended front matter:

```yaml
---
title: "Full Name"
positions:
  - kind: "phd"          # director | phd | mphil | postdoc | technical | emeritus | affiliate
    start_date: "2022"
    end_date: "2026"     # null/empty means current role
  - kind: "postdoc"
    start_date: "2026"
    end_date: null
weight: 10               # controls sort order within category
email: "abc1@cam.ac.uk"
image: "/images/people/full-name.jpg"
group: "mcc"             # optional: mcc | mls
website: "https://example.com"
---

Optional bio text here.
```

Notes:

- `group` is optional. If set, use `mcc` for Music Cognition & Culture or `mls` for Music, Language & Society.
- Listing category/status and subtitle are derived from `positions`.
- `positions[].title` is optional; when omitted, title defaults are derived from `kind`.
- Current role is derived from `end_date` (empty/null = current role).
- `start_date` and `end_date` are optional; include them when known.
- Use `YYYY` or `YYYY-MM` for any provided date values.
- `weight` controls sorting within a category. Lower numbers appear first.
- The photo does not need to be perfectly square, but it will be cropped into a circular frame on the site. A centered head-and-shoulders image with roughly square dimensions works best.
- Use an image path under `static/images/people/`, for example `"/images/people/jane-doe.jpg"`.

### New project

Create a file in `content/projects/` and add its slug to the relevant theme file in `content/themes/`:

```yaml
---
title: "Project Title"
people:
  - "person-slug"
publications:
  - "publication-slug"
media:
  - type: "image"
    src: "/images/projects/filename.png"
    caption: "Description"
---

Project body text.
```

After creating the project file, add its slug to the `projects` list in either `content/themes/cognition.md` or `content/themes/culture.md` so it appears under the right theme.

## Python tooling and tests

To run repository maintenance scripts and tests:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r scripts/requirements.txt
pytest tests
```

## Production build

```bash
hugo --gc --minify --cleanDestinationDir
```

Output goes to `public/`. Deployment to GitHub Pages happens automatically on push to `main` via GitHub Actions.

## Pull request preview build

Every pull request to `main` runs the same Hugo production build in GitHub Actions and uploads the generated `public/` directory as an artifact named `pr-preview-site-<PR number>`.

### Option 1 — Artifact preview from GitHub Actions (current CI flow)

To preview the built result before merge:

1. Open the pull request's latest **Deploy Hugo site to GitHub Pages** workflow run.
2. Download the `pr-preview-site-<PR number>` artifact.
3. Extract it and open `index.html` in a browser.

Best for: checking exactly what CI produced.

### Option 2 — Preview on your phone over local network

If you want to test on your phone quickly while editing:

1. Run `hugo server -D --bind 0.0.0.0 --baseURL http://<your-computer-ip>:1313`.
2. Ensure phone and computer are on the same Wi-Fi network.
3. Open `http://<your-computer-ip>:1313` on your phone browser.

Best for: fast visual checks on mobile while iterating locally.

### Option 3 — Keep artifact build, add hosted PR previews later

If the team wants one-click phone previews from any PR in future, you can add an external preview host (for example Netlify/Vercel/Cloudflare Pages) that posts a public URL per PR.

Best for: easiest reviewer experience, but requires extra service setup.

### Option 4 — GitHub Pages subpath previews (possible, but with caveats)

Yes — you can publish branch/PR previews under paths like `/previews/pr-123/` on GitHub Pages by deploying preview builds into subfolders on a dedicated Pages branch and setting Hugo `--baseURL` to that subpath.

Important tradeoffs:

1. GitHub Pages exposes one published site per repo, so preview content and production content must be managed together on the Pages branch.
2. You need cleanup logic for closed PRs to remove stale `/previews/...` folders.
3. Concurrent PR deploys can conflict unless the workflow serializes writes and preserves existing preview folders.
4. The current artifact-based preview is simpler and avoids touching the live Pages deployment path.

Best for: teams that want GitHub-only hosted preview URLs and are comfortable maintaining extra deployment logic.
