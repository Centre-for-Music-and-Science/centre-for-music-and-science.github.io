# Research content architecture

This document is the canonical source of truth for the research content model.

## Entity model

- Themes: top-level research areas.
- Projects: children of themes or other projects (research portfolio).
- Topics: applicant-facing research topics shown within pathway pages and on `/topics/` (optionally linked to a project).
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

## Topics contract

Projects are the research portfolio. **Topics** are a separate applicant-facing content type for research areas people can apply to work on.

- Section: `content/topics/`
- Open topics are surfaced in the Topics tab on each rendered
  `/applicants/<pathway>/` page.
- The complete topic index remains available at `/topics/`, but neither the
  pathway Topics tabs nor the `/applicants/` hub link to it; the tabs embed the
  topic cards directly instead.
- Detail pages live at `/topics/<slug>/`.
- Pathway pages currently show the same unfiltered set of open topics.
  The embedded Topics tab provides the extension point for pathway-specific
  filtering in the future.
- Graduate pathway pages may define tab bodies with top-level `##` headings (for
  example `Programme`, `Prerequisites`, `Finances`, `Applying`). Set `pathway_tabs` in
  front matter to control order, including where `topics` sits — e.g.
  `[programme, topics, prerequisites, finances, applying]`.
- Without `pathway_tabs`, markdown sections appear in heading order and Topics
  is inserted after the first section when enabled.
- Pathway pages without `##` sections keep a single About panel (plus Topics
  when enabled).
- Pathway pages may set `topics_intro` to customise the Topics tab blurb.
- Set `show_topics: false` on a pathway page to hide the Topics tab entirely
  (default is shown).

Front matter:

```yaml
open: true              # false = hide from topic listings (default true)
thumbnail: ""           # optional card / detail image path
thumbnail_credit:       # optional; shown on detail page only
  author: "ArtBrom"
  license: "CC BY-SA 2.0"
  license_url: "https://creativecommons.org/licenses/by-sa/2.0/"
supervisor: peter-harrison  # optional person slug
cosupervisors:          # optional person slugs for possible cosupervisors
  - harin-lee
projects:               # optional links to portfolio project slugs
  - memory
publications:           # optional links to publication slugs
  - lee-globalmood
weight: 0
```

Relationship rules:

- `thumbnail` is an optional image shown on topic cards and the detail header.
- `thumbnail_credit` is optional attribution for third-party thumbnails; when
  set, it renders under the detail-page thumbnail only (not on brochure cards).
- The Markdown body is the detailed description shown only on the topic page.
- `supervisor` is an optional people slug shown on the detail page as Supervisor.
- `cosupervisors` is an optional list of people slugs shown on the detail page
  as Possible cosupervisors. External collaborators can use people records with
  `positions[].kind: collaborator` (these are omitted from People listings).
- Every slug in `projects` must resolve to an existing `content/projects` record.
- Every slug in `publications` must resolve to an existing `content/publications` record.
- Topic detail pages show linked projects as Related projects.
- Related publications combine any explicit `publications` list with reverse
  lookup of publications tagged to the linked projects (including descendant
  projects).
- Portfolio projects with no topic are not advertised for applications.
- Hypothetical topics use a topic with no `projects` (until research exists in the portfolio).

Build-time rules:

- `supervisor`, when set, must be an existing people slug
- `cosupervisors`, when set, must be a list of existing people slugs
- every slug in `projects` must match an existing project slug
- every slug in `publications` must match an existing publication slug
- legacy `collaborators` fields are rejected
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

Publication detail pages also surface:

- Related projects from `publications.projects`
- Related apps from explore records that list the publication in `publications`
- Related datasets from `publications.datasets`

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
- `volume`, `number`, `pages` (when present in BibTeX)
- `doi` (derived from BibTeX when available)

Hand-maintained `date` should be the online publication day (`YYYY-MM-DD`) when
known, because lists sort on it. Display still uses the year only.

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
