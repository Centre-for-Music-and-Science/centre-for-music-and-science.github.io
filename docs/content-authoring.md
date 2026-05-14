# Content authoring guide

This guide describes how to create and maintain records in the refactored research model.

## Create a new record

Use Hugo archetypes:

- `hugo new projects/<slug>.md`
- `hugo new methods/<slug>.md`
- `hugo new groups/<slug>.md`
- `hugo new publications/<slug>.md`
- `hugo new datasets/<slug>.md`
- `hugo new events/<slug>.md`

Research record archetypes include a `stub_only` field comment.

- `stub_only: false` visible and linkable
- `stub_only: true` visible but non-clickable

## Relationship workflow

Set project hierarchy on parent records:

- theme: set `projects`
- project: set `projects` for child projects

Set reverse-lookup tags on publications/datasets so pages can build related lists automatically:

- `projects`, `methods`

Person-project links are project-owned:

- set `people: [person-slug, ...]` on project records
- do not set `projects` on people records

Group membership is person-owned:

- set `group` (or `groups`) on people records
- group pages derive projects from member-linked projects and derive publications from member-linked publications

Build-time guards:

- every project must be listed in `themes.*.projects` or `projects.*.projects`
- parent `projects` lists must only reference existing project slugs

## Publications workflow

1. Add `bibtex` to the publication record (**required**).
2. Run the citation generation script (to be wired into build workflow).
3. Commit generated `citation_apa`, `authors`, `journal`, and `doi`.
4. Set publication ownership links on the publication record itself:
   - `projects: [project-slug, ...]`
   - `methods: [method-slug, ...]`

Build-time guard:

- publication templates fail the build if `bibtex` is missing.
- project/method/group records fail the build if they define a `publications` field.

Do not manually edit:

- `citation_apa`
- `authors` (when generated from BibTeX)
- `journal` (when generated from BibTeX)
- `doi` (when generated from BibTeX)
- These fields are written with inline comments in front matter to indicate
  that they are auto-generated.

Author matching for profile links and bolding:

- Add canonical BibTeX-style author strings to person records via `publication_names`.
- Example:
  - `publication_names: ["Cross, I."]`
- Use these canonical strings exactly as they appear in generated publication `authors` lines.

## Featured publications

Add featured publication slugs on the parent record:

- `featured_publications`

Featured publications render first as cards; the remaining related publications render as an APA citation list.

Do not add `publications` arrays to project/method/group records. Publication pages are the sole source of relation ownership.
Do not add `groups` arrays to publication records for group-page linking; group publication lists are inherited from group members.

## Dataset linkage

Link publications to datasets via publication front matter:

- `datasets: [dataset-slug, ...]`

Dataset pages automatically gather related publications from this field.

## Events workflow

Create upcoming event records in `content/events/`. The homepage shows the next three current/future events, ordered by event date.

Recommended front matter:

```yaml
---
title: "CMS Seminar Title"
date: 2026-03-25T17:00:00
end_date: 2026-03-25T18:30:00
date_label: "25 March 2026, 5pm"
location: "Centre for Music and Science"
speakers:
  - name: "Presenter Name"
    image: "/images/events/presenter-name.jpg"
    affiliations:
      - "Presenter Affiliation"
event_type: "CMS seminar"
image: ""
livestream_url: ""
abstract: ""
biography: ""
---
```

Use `date` for sorting. Use `date_label` when the public display text needs to differ from the default formatted date or date range. Add one or more `speakers`, each with one or more `affiliations` and an optional speaker `image`. Event-level `abstract`, `biography`, `image`, and `livestream_url` are optional and render only on the event detail page.

## Troubleshooting checklist

- Card not linkable: check `stub_only` is not `true`.
- Missing relation list: verify reverse tags include the current entity slug.
- Missing person on a project page: verify the project has the person slug in `people`.
- Missing publication on a group page: verify a group member has a matching `publication_names` value present in the publication `authors` line.
- Missing featured card: verify the featured slug exists and matches publication slug.
- Wrong citation: verify `bibtex` and rerun citation generation.
- Build fails with hierarchy error: check `themes.*.projects` and `projects.*.projects` for missing or orphaned slugs.
