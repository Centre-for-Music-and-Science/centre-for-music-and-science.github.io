# Content authoring guide

This guide describes how to create and maintain records in the refactored research model.

## Create a new record

Use Hugo archetypes:

- `hugo new projects/<slug>.md`
- `hugo new methods/<slug>.md`
- `hugo new groups/<slug>.md`
- `hugo new publications/<slug>.md`
- `hugo new datasets/<slug>.md`

Each archetype includes a `stub_only` field comment.

- `stub_only: false` visible and linkable
- `stub_only: true` visible but non-clickable

## Relationship workflow

Set project hierarchy on parent records:

- theme: set `projects`
- project: set `projects` for child projects

Set reverse-lookup tags on people/publications/datasets so pages can build related lists automatically:

- `projects`, `methods`, `groups`

Build-time guards:

- every project must be listed in `themes.*.projects` or `projects.*.projects`
- parent `projects` lists must only reference existing project slugs

## Publications workflow

1. Add `bibtex` to the publication record (**required**).
2. Run the citation generation script (to be wired into build workflow).
3. Commit generated `citation_apa`, `authors`, `journal`, and `doi`.

Build-time guard:

- publication templates fail the build if `bibtex` is missing.

Do not manually edit:

- `citation_apa`
- `authors` (when generated from BibTeX)
- `journal` (when generated from BibTeX)
- `doi` (when generated from BibTeX)
- These fields are written with inline comments in front matter to indicate
  that they are auto-generated.

## Featured publications

Add featured publication slugs on the parent record:

- `featured_publications`

Featured publications render first as cards; the remaining related publications render as an APA citation list.

## Dataset linkage

Link publications to datasets via publication front matter:

- `datasets: [dataset-slug, ...]`

Dataset pages automatically gather related publications from this field.

## Troubleshooting checklist

- Card not linkable: check `stub_only` is not `true`.
- Missing relation list: verify reverse tags include the current entity slug.
- Missing featured card: verify the featured slug exists and matches publication slug.
- Wrong citation: verify `bibtex` and rerun citation generation.
- Build fails with hierarchy error: check `themes.*.projects` and `projects.*.projects` for missing or orphaned slugs.
