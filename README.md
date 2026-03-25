# Centre for Music and Science — Website

The website for the [Centre for Music and Science](https://centre-for-music-and-science.github.io) at the University of Cambridge, built with [Hugo](https://gohugo.io/).

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
- If `positions` is present, listing category/status and subtitle are derived from it.
- `positions[].title` is optional; when omitted, title defaults are derived from `kind`.
- Current role is derived from `end_date` (empty/null = current role).
- Use `YYYY` or `YYYY-MM` for `start_date` and `end_date`.
- Keep legacy fields (`category`, `status`, `degree_type`, `graduation_year`, `position_title`) only for older profiles pending migration.
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
