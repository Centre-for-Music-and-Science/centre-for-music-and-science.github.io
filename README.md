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

No other dependencies are required. The theme is included in the repository under `themes/cms/`.

## Local development

Clone the repository and start the dev server:

```bash
git clone https://github.com/centre-for-music-and-science/website.git
cd website
hugo server -D
```

The site will be available at **http://localhost:1313/**. The server watches for file changes and reloads automatically.

Useful flags:

| Flag | Description |
|------|-------------|
| `-D` | Include draft content |
| `--buildFuture` | Include future-dated content (enabled by default in `hugo.toml`) |
| `--disableFastRender` | Full rebuild on every change (slower but avoids stale state) |
| `--port 1414` | Use a different port |

## Project structure

```
.
├── content/             # Markdown content
│   ├── people/          # Lab members
│   ├── projects/        # Research projects
│   ├── themes/          # Research theme groupings
│   ├── publications/    # Publication entries
│   ├── events/          # Events
│   ├── datasets/        # Dataset pages
│   ├── facilities/      # Facilities info
│   └── applicants/      # Applicant info (PhD, MPhil, etc.)
├── data/                # YAML data files (lab authors, past members, videos)
├── static/              # Static assets (images, audio, JSON)
├── themes/cms/          # Custom Hugo theme
│   ├── layouts/         # HTML templates
│   └── static/          # Theme CSS and JS
├── hugo.toml            # Site configuration
└── .github/workflows/   # GitHub Actions deployment
```

## Adding content

### New publication

Create a file in `content/publications/`:

```yaml
---
title: "Paper Title"
date: 2026-01-15
authors: "Author, A., Author, B., & Author, C."
journal: "Journal Name, 12(3), 100–115."
doi: "https://doi.org/10.xxxx/xxxxx"
---
```

### New person

To add a new person, complete these steps:

1. Create a new Markdown file in `content/people/` using the person's slug, for example `content/people/jane-doe.md`.
2. Add front matter for the person's name, role, category, ordering, and contact details.
3. Add an optional short bio below the front matter.
4. Place the profile photo in `static/images/people/`.
5. Run `hugo server -D` and check both the homepage people cards and the person's detail page.

Recommended front matter:

```yaml
---
title: "Full Name"
role: "PhD Student"
category: "phd"          # director | phd | postdoc | technical | emeritus | affiliate
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
- `weight` controls sorting within a category. Lower numbers appear first.
- The photo does not need to be perfectly square, but it will be cropped into a circular frame on the site. A centered head-and-shoulders image with roughly square dimensions works best.
- Use an image path under `static/images/people/`, for example `"/images/people/jane-doe.jpg"`.

### New project

Create a file in `content/projects/` and add its slug to the relevant theme file in `content/themes/`:

```yaml
---
title: "Project Title"
theme: "music-cognition"   # must match a theme filename
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

## Production build

```bash
hugo --gc --minify --cleanDestinationDir
```

Output goes to `public/`. Deployment to GitHub Pages happens automatically on push to `main` via GitHub Actions.
