# Research content architecture

This document is the canonical source of truth for the research content model.

## Entity model

- Themes: top-level research areas.
- Projects: children of themes or other projects (research portfolio).
- Opportunities: applicant-facing topics for Join us (optionally linked to a project).
- Methods: standalone method records.
- Groups: organisational group records.
- Publications: bibliographic records with optional detail pages.
- Datasets: dataset records that can be linked from publications and other entities.

## Hierarchy ownership

Hierarchy is parent-owned:

- `theme.projects` lists child project slugs.
- `project.projects` lists child project slugs.

Templates should derive hierarchy from these parent lists.

Build-time rules:

- every slug in `theme.projects` and `project.projects` must resolve to a project record
- every project must be referenced by either a theme or another project

## Stub state contract

The `stub_only` field is mandatory on:

- projects
- methods
- groups
- publications

Boolean semantics:

- `stub_only: false`: record is shown and linkable.
- `stub_only: true`: record is shown in cards/lists but rendered as non-clickable.

Default for new records is `stub_only: false`.

## Opportunities contract

Projects are the research portfolio. **Opportunities** are a separate applicant-facing content type for topics people can apply to work on.

- Section: `content/opportunities/`
- Surfaced on `/applicants/` (brochure) and optional detail pages at `/opportunities/<slug>/`

Front matter:

```yaml
open: true              # false = hide from brochure (default true)
levels:                 # required when open is true
  - phd
  - mphil
collaborators:          # optional display names (not yet linked to people)
  - "Alex Smith"
projects:               # optional links to portfolio project slugs
  - memory
publications:           # optional links to publication slugs
  - lee-globalmood
note: ""                # optional caveat shown in the brochure
summary: ""             # short text shown only on the brochure card
weight: 0
```

Known `levels` values:

- `undergraduate`, `mphil`, `phd`, `postdoc`, `internship`, `visitor`

Relationship rules:

- `summary` is the short applicant-facing pitch shown on the brochure.
- The Markdown body is the detailed description shown only on the opportunity page.
- `collaborators` is an optional list of quoted names displayed directly on the brochure card and detail page.
- Every slug in `projects` must resolve to an existing `content/projects` record.
- Every slug in `publications` must resolve to an existing `content/publications` record.
- Portfolio projects with no opportunity are not advertised for applications.
- Hypothetical topics use an opportunity with no `projects` (until research exists in the portfolio).

Build-time rules:

- if `open` is `true` (or omitted), `levels` must be a non-empty list of known levels
- `collaborators`, when set, must be a list of non-empty strings
- every slug in `projects` must match an existing project slug
- every slug in `publications` must match an existing publication slug

## Reverse aggregation model

People/publications/datasets are aggregated by reverse lookup tags.

People:

- `projects.people` (project ownership; single source of truth for person-project links)
- `people.methods`
- `people.group` / `people.groups`

Publications:

- `publications.projects`
- `publications.methods`

Group publication relation model:

- Groups do not directly own publication links.
- Group publication lists are inherited from group members.
- Publication records should not use `publications.groups` for group-page linking.

Publication ownership rules:

- Publication links are publication-owned only.
- Parent entity records (`projects`, `methods`) must not define `publications`.
- Build fails if parent-side `publications` fields are present.

Datasets:

- `datasets.projects`
- `datasets.methods`
- `datasets.groups`

Publication-to-dataset linking source of truth:

- `publications.datasets` (dataset slug list)

Dataset pages should reverse-query publication records by `datasets`.

## Featured publication rules

Featured publications are parent-owned:

- `projects.featured_publications`
- `methods.featured_publications`
- `groups.featured_publications`

Rendering rules:

1. Render all featured publications first as cards.
2. Build the normal related publication list.
3. Remove duplicates already shown in featured cards.

## Publication metadata ownership

Publication metadata source of truth:

- `bibtex` is authoritative for citation metadata and required for publication records.

Generated fields (do not edit manually):

- `citation_apa`
- `authors` (display line for list formatting)
- `journal` (display venue for list formatting)
- `doi` (derived from BibTeX when available)

Publication pages are optional and controlled by content readiness.

## Missing-data policy

Sections are omitted when data is absent:

- no related people => omit people section
- no related publications => omit publications section
- no featured publications => omit featured block
- no leader image => omit that block

No empty placeholder headings should be rendered.

## Author matching source of truth

Author-name decoration and person-profile mapping are derived from people records:

- `content/people/*.md` may define `publication_names` as canonical BibTeX-style author strings.
- Publication-to-person inference links authors when a `publication_names` value appears in a publication's `authors` string.
- Author bolding and profile-avatar linking both use the same `publication_names` source.
