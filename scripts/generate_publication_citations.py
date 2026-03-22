#!/usr/bin/env python3
"""Generate publication citation fields from BibTeX front matter."""

from __future__ import annotations

import argparse
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


FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
FIELD_RE = re.compile(r"(\w+)\s*=\s*\{([^{}]*)\}|(\w+)\s*=\s*\"([^\"]*)\"")


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


def format_author(author: str) -> str:
    """Format one BibTeX author name in APA style."""
    author = author.strip()
    if "," in author:
        last, given = [part.strip() for part in author.split(",", 1)]
    else:
        parts = author.split()
        if len(parts) < 2:
            return author
        last = parts[-1]
        given = " ".join(parts[:-1])

    initials = []
    for token in given.replace("-", " ").split():
        if token:
            initials.append(f"{token[0].upper()}.")
    initials_str = " ".join(initials)
    return f"{last}, {initials_str}".strip()


def format_authors_apa(authors_raw: str) -> str:
    """Format a BibTeX author list to APA author string."""
    authors = [
        format_author(author)
        for author in authors_raw.split(" and ")
        if author.strip()
    ]
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]}, & {authors[1]}"
    return f"{', '.join(authors[:-1])}, & {authors[-1]}"


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


def render_apa_citation(fields: Dict[str, str]) -> str:
    """Render a best-effort APA citation from parsed BibTeX fields."""
    authors = format_authors_apa(fields.get("author", ""))
    year = fields.get("year", "n.d.")
    title = fields.get("title", "").replace("{", "").replace("}", "").strip()
    journal = fields.get("journal", fields.get("booktitle", "")).strip()
    volume = fields.get("volume", "").strip()
    number = fields.get("number", "").strip()
    pages = fields.get("pages", "").replace("--", "-").strip()
    doi = normalize_doi(fields.get("doi", ""))

    parts = []
    if authors:
        parts.append(authors)
    parts.append(f"({year}).")
    if title:
        parts.append(f"{title}.")
    if journal:
        journal_part = f"<em>{journal}</em>"
        if volume:
            journal_part += f", {volume}"
            if number:
                journal_part += f"({number})"
        if pages:
            journal_part += f", {pages}"
        journal_part += "."
        parts.append(journal_part)
    if doi:
        parts.append(doi)
    return " ".join(parts).strip()


def build_front_matter_text(data: Dict) -> str:
    """Serialize YAML front matter with stable key order."""
    yaml_text = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=False,
    ).strip()
    return f"---\n{yaml_text}\n---\n"


def update_publication_file(path: Path) -> bool:
    """Update one publication markdown file from its BibTeX field."""
    original = path.read_text(encoding="utf-8")
    front_matter, body = split_front_matter(original)
    bibtex = front_matter.get("bibtex", "")
    if not bibtex:
        return False

    fields = parse_bibtex_fields(bibtex)
    if not fields:
        return False

    front_matter["citation_apa"] = render_apa_citation(fields)
    raw_doi = fields.get("doi", front_matter.get("doi", ""))
    front_matter["doi"] = normalize_doi(raw_doi)

    updated = build_front_matter_text(front_matter) + body
    if updated == original:
        return False

    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    """Run citation generation for publication markdown files."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate citation_apa and doi from publication BibTeX fields."
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
