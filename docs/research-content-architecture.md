# Research content architecture

This document is the canonical source of truth for the research content model.

## Entity model

- Themes: top-level research areas.
- Projects: children of themes or other projects.
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

## Reverse aggregation model

People/publications/datasets are aggregated by reverse lookup tags.

People:

- `people.projects`
- `people.methods`
- `people.groups`

Publications:

- `publications.projects`
- `publications.methods`
- `publications.groups`

Publication ownership rules:

- Publication links are publication-owned only.
- Parent entity records (`projects`, `methods`, `groups`) must not define `publications`.
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
