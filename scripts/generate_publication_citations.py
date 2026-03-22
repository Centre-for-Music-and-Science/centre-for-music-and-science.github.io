#!/usr/bin/env python3
"""Generate publication citation fields from BibTeX front matter."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
from pathlib import Path
from typing import Dict
from typing import Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover - import guard for CLI usage.
    raise ImportError(
        "PyYAML is required. Install it with: pip install pyyaml"
    ) from exc

try:
    from citeproc import Citation
    from citeproc import CitationItem
    from citeproc import CitationStylesBibliography
    from citeproc import CitationStylesStyle
    from citeproc import formatter
    from citeproc.source.json import CiteProcJSON
except ImportError as exc:  # pragma: no cover - import guard for CLI usage.
    raise ImportError(
        "citeproc-py and citeproc-py-styles are required. "
        "Install them with: pip install citeproc-py citeproc-py-styles"
    ) from exc

try:
    from pybtex.database import parse_string
except ImportError as exc:  # pragma: no cover - import guard for CLI usage.
    raise ImportError(
        "pybtex is required. Install it with: pip install pybtex"
    ) from exc


FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
FIELD_RE = re.compile(r"(\w+)\s*=\s*\{([^{}]*)\}|(\w+)\s*=\s*\"([^\"]*)\"")
AUTOGEN_COMMENT = "# generated from bibtex; do not edit manually"
AUTOGEN_FIELDS = (
    "citation_apa",
    "citation_mla",
    "citation_chicago",
    "citation_ieee",
    "authors",
    "journal",
    "doi",
)
CSL_STYLE_MAP = {
    "citation_apa": "apa",
    "citation_mla": "modern-language-association",
    "citation_chicago": "chicago-author-date",
    "citation_ieee": "ieee",
}
ENTRY_TYPE_MAP = {
    "article": "article-journal",
    "book": "book",
    "inbook": "chapter",
    "incollection": "chapter",
    "inproceedings": "paper-conference",
    "conference": "paper-conference",
    "proceedings": "book",
    "mastersthesis": "thesis",
    "phdthesis": "thesis",
    "techreport": "report",
    "misc": "article",
}


class PublicationDumper(yaml.SafeDumper):
    """YAML dumper with readable multiline string formatting."""


def str_presenter(dumper, data):
    """Render multiline strings as YAML block scalars."""
    if "\n" in data:
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str",
            data,
            style="|",
        )
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


PublicationDumper.add_representer(str, str_presenter)


def split_front_matter(content: str) -> Tuple[Dict, str]:
    """Split a markdown document into YAML front matter and body."""
    match = FRONT_MATTER_RE.match(content)
    if not match:
        raise ValueError("File does not contain YAML front matter.")
    front_matter = yaml.safe_load(match.group(1)) or {}
    body = content[match.end():]
    return front_matter, body


def parse_bibtex_fields(bibtex: str) -> Dict[str, str]:
    """Parse simple BibTeX key-value fields from a BibTeX entry string."""
    fields: Dict[str, str] = {}
    for match in FIELD_RE.finditer(bibtex):
        if match.group(1):
            fields[match.group(1).lower()] = match.group(2).strip()
        else:
            fields[match.group(3).lower()] = match.group(4).strip()
    return fields


def normalize_doi(doi_value: str) -> str:
    """Normalize a DOI to https://doi.org/... format."""
    if not doi_value:
        return ""
    doi_value = doi_value.strip()
    doi_value = doi_value.replace("https://doi.org/", "")
    doi_value = doi_value.replace("http://doi.org/", "")
    doi_value = doi_value.replace("doi:", "")
    doi_value = doi_value.strip().strip("{}")
    return f"https://doi.org/{doi_value}" if doi_value else ""


def publication_link(fields: Dict[str, str]) -> str:
    """Resolve publication link, preferring DOI over explicit URL."""
    doi_raw = fields.get("doi", "").strip().strip("{}")
    url_raw = fields.get("url", "").strip().strip("{}")
    if doi_raw.startswith("10."):
        return normalize_doi(doi_raw)
    if doi_raw.startswith(("http://", "https://")):
        return doi_raw
    if url_raw.startswith(("http://", "https://")):
        return url_raw
    return normalize_doi(doi_raw)


def normalize_terminal_title_punctuation(citation_html: str) -> str:
    """Drop redundant periods after terminal ?/! punctuation."""
    return re.sub(
        r"([?!])((?:[\"'”]|</em>|</i>)*)\.(?=\s|$)",
        r"\1\2",
        citation_html,
    )


def normalize_citeproc_html(citation_html: str) -> str:
    """Normalize citeproc HTML output for front matter storage."""
    citation_html = html.unescape(citation_html)
    citation_html = re.sub(
        r'<a[^>]*href="([^"]+)"[^>]*>.*?</a>',
        r"\1",
        citation_html,
    )
    citation_html = citation_html.replace("<i>", "<em>").replace(
        "</i>", "</em>"
    )
    citation_html = citation_html.replace("<b>", "").replace("</b>", "")
    citation_html = citation_html.replace("\xa0", " ")
    citation_html = re.sub(r"\bURL:\s*(https?://\S+)", r"\1", citation_html)
    citation_html = re.sub(r"([A-Z])\.\.", r"\1.", citation_html)
    citation_html = re.sub(r"(?<=\.)and\b", " and", citation_html)
    citation_html = re.sub(r"^\[(\d+)\](?=\S)", r"[\1] ", citation_html)
    citation_html = normalize_terminal_title_punctuation(citation_html)
    citation_html = re.sub(r"\s+", " ", citation_html).strip()
    return citation_html


def extract_authors_from_apa_citation(citation_apa: str) -> str:
    """Extract the author block from an APA citation string."""
    match = re.match(r"^(.*?)\s+\((?:n\.d\.|\d{4}[a-z]?)\)\.", citation_apa)
    return match.group(1).strip() if match else ""


def extract_publication_venue(fields: Dict[str, str]) -> str:
    """Extract journal/booktitle venue for list-style rendering."""
    return fields.get("journal", fields.get("booktitle", "")).strip()


def year_from_front_matter(date_value: object) -> str:
    """Extract a 4-digit year from YAML date front matter values."""
    if date_value is None:
        return ""
    if isinstance(date_value, (dt.date, dt.datetime)):
        return str(date_value.year)
    text = str(date_value).strip()
    match = re.match(r"^(\d{4})", text)
    return match.group(1) if match else ""


def first_bibtex_entry_data(bibtex: str):
    """Get the first pybtex entry key and object from a BibTeX blob."""
    bibliography = parse_string(bibtex, "bibtex")
    if not bibliography.entries:
        raise ValueError("No bibliography entry found in BibTeX.")
    entry_key, entry = next(iter(bibliography.entries.items()))
    return entry_key, entry


def entry_type_to_csl(entry_type: str) -> str:
    """Map BibTeX entry types to CSL item types."""
    return ENTRY_TYPE_MAP.get(entry_type.lower(), "article")


def person_to_csl_name(person) -> Dict[str, str]:
    """Convert a pybtex person object into a CSL name object."""
    family = " ".join(
        person.prelast_names + person.last_names + person.lineage_names
    ).strip()
    given = " ".join(person.first_names + person.middle_names).strip()
    name: Dict[str, str] = {}
    if family:
        name["family"] = family
    if given:
        name["given"] = given
    return name


def bibtex_to_csl_item(
    bibtex: str,
    link: str,
    inpress: bool,
    year: str,
) -> Tuple[str, Dict]:
    """Convert one BibTeX entry into CSL-JSON item data."""
    entry_key, entry = first_bibtex_entry_data(bibtex)
    fields = entry.fields

    item: Dict = {
        "id": entry_key,
        "type": entry_type_to_csl(entry.type),
        "title": fields.get("title", ""),
    }

    authors = [person_to_csl_name(p) for p in entry.persons.get("author", [])]
    authors = [a for a in authors if a]
    if authors:
        item["author"] = authors

    venue = fields.get("journal", fields.get("booktitle", "")).strip()
    if venue:
        item["container-title"] = venue

    effective_year = year.strip()
    if not effective_year:
        year_match = re.search(r"\d{4}", fields.get("year", ""))
        effective_year = year_match.group(0) if year_match else ""
    if effective_year:
        item["issued"] = {"date-parts": [[int(effective_year)]]}

    doi_raw = fields.get("doi", "").strip()
    doi_norm = normalize_doi(doi_raw)
    if doi_norm:
        item["DOI"] = doi_norm.removeprefix("https://doi.org/")

    if link:
        item["URL"] = link

    if inpress:
        item["status"] = "forthcoming"

    return entry_key, item


def render_csl_citation(
    bibtex: str,
    csl_style: str,
    link: str,
    inpress: bool,
    year: str,
) -> str:
    """Render a single citation with citeproc and a CSL style name."""
    entry_key, csl_item = bibtex_to_csl_item(
        bibtex=bibtex,
        link=link,
        inpress=inpress,
        year=year,
    )
    source = CiteProcJSON([csl_item])
    style = CitationStylesStyle(csl_style, validate=False)
    bibliography = CitationStylesBibliography(style, source, formatter.html)
    bibliography.register(Citation([CitationItem(entry_key)]))
    rendered = str(bibliography.bibliography()[0])
    return normalize_citeproc_html(rendered)


def build_front_matter_text(data: Dict) -> str:
    """Serialize YAML front matter with stable key order."""
    yaml_text = yaml.dump(
        data,
        Dumper=PublicationDumper,
        sort_keys=False,
        allow_unicode=True,
    ).strip()
    yaml_text = inject_autogen_comments(yaml_text)
    return f"---\n{yaml_text}\n---\n"


def inject_autogen_comments(yaml_text: str) -> str:
    """Insert generated-field warning comments in serialized front matter."""
    out_lines = []
    in_autogen_block = False
    for line in yaml_text.splitlines():
        stripped = line.lstrip()
        is_top_level = not line.startswith(" ")
        if is_top_level and ":" in stripped:
            key = stripped.split(":", 1)[0]
            if key in AUTOGEN_FIELDS:
                if not in_autogen_block:
                    out_lines.append(AUTOGEN_COMMENT)
                in_autogen_block = True
            else:
                in_autogen_block = False
        out_lines.append(line)
    return "\n".join(out_lines)


def update_publication_file(path: Path) -> bool:
    """Update one publication markdown file from its BibTeX field."""
    original = path.read_text(encoding="utf-8")
    front_matter, body = split_front_matter(original)
    bibtex = front_matter.get("bibtex", "")
    if not bibtex:
        return False

    fields = parse_bibtex_fields(bibtex)
    venue = extract_publication_venue(fields)
    if venue:
        front_matter["journal"] = venue

    link = publication_link(fields)
    front_matter["doi"] = link

    year = year_from_front_matter(front_matter.get("date")) or fields.get(
        "year", ""
    ).strip()
    inpress = bool(front_matter.get("inpress", False))

    for citation_key, csl_style in CSL_STYLE_MAP.items():
        front_matter[citation_key] = render_csl_citation(
            bibtex=bibtex,
            csl_style=csl_style,
            link=link,
            inpress=inpress,
            year=year,
        )

    front_matter["authors"] = extract_authors_from_apa_citation(
        front_matter["citation_apa"]
    )

    updated = build_front_matter_text(front_matter) + body
    if updated == original:
        return False

    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    """Run citation generation for publication markdown files."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate citation fields and doi from publication BibTeX fields."
        )
    )
    parser.add_argument(
        "publications_dir",
        nargs="?",
        default="content/publications",
        help="Directory containing publication markdown files.",
    )
    args = parser.parse_args()

    publications_dir = Path(args.publications_dir)
    if not publications_dir.exists():
        raise SystemExit(f"Directory not found: {publications_dir}")

    changed = 0
    for path in sorted(publications_dir.glob("*.md")):
        if path.name.startswith("_"):
            continue
        if update_publication_file(path):
            changed += 1

    print(f"Updated {changed} publication file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
