# Content authoring guide

This guide describes how to create and maintain records in the refactored research model.

## Create a new record

Use Hugo archetypes:

- `hugo new topics/<slug>.md`
- `hugo new projects/<slug>.md`
- `hugo new methods/<slug>.md`
- `hugo new groups/<slug>.md`
- `hugo new publications/<slug>.md`
- `hugo new datasets/<slug>.md`

Each archetype includes a `stub_only` field comment.

- `stub_only: false` visible and linkable
- `stub_only: true` visible but non-clickable

## Relationship workflow

Set parent references on child records:

- topic: set `theme`
- project: set `topic`

Set reverse-lookup tags on people/publications/datasets so pages can build related lists automatically:

- `topics`, `projects`, `methods`, `groups`

## Publications workflow

1. Add `bibtex` to the publication record.
2. Run the citation generation script (to be wired into build workflow).
3. Commit generated `citation_apa` and `doi`.

Do not manually edit:

- `citation_apa`
- `doi` (when generated from BibTeX)

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
