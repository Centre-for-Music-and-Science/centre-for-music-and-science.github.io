#!/usr/bin/env python3
"""Generate publication citation fields from BibTeX front matter."""

from __future__ import annotations

import argparse
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
    from pybtex.database import parse_string
    from pybtex.plugin import find_plugin
except ImportError as exc:  # pragma: no cover - import guard for CLI usage.
    raise ImportError(
        "pybtex and pybtex-apa-style are required. "
        "Install them with: pip install pybtex pybtex-apa-style"
    ) from exc


FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
FIELD_RE = re.compile(r"(\w+)\s*=\s*\{([^{}]*)\}|(\w+)\s*=\s*\"([^\"]*)\"")
AUTOGEN_COMMENT = "# generated from bibtex; do not edit manually"
AUTOGEN_FIELDS = ("citation_apa", "authors", "journal", "doi")


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
    """Resolve the outbound link for a publication (DOI preferred, else explicit URL)."""
    doi_raw = fields.get("doi", "").strip().strip("{}")
    url_raw = fields.get("url", "").strip().strip("{}")
    if doi_raw.startswith("10."):
        return normalize_doi(doi_raw)
    if doi_raw.startswith(("http://", "https://")):
        return doi_raw
    if url_raw.startswith(("http://", "https://")):
        return url_raw
    return normalize_doi(doi_raw)


def normalize_pybtex_html(citation_html: str) -> str:
    """Normalize pybtex HTML output for front matter storage."""
    citation_html = html.unescape(citation_html)
    citation_html = citation_html.replace("\xa0", " ")
    citation_html = re.sub(
        r'<span class="bibtex-protected">([^<]*)</span>',
        r"\1",
        citation_html,
    )
    citation_html = re.sub(
        r'<a\s+href="(https?://doi\.org/[^"]+)">[^<]*</a>',
        r"\1",
        citation_html,
        flags=re.IGNORECASE,
    )
    citation_html = re.sub(
        r'URL:\s*<a\s+href="([^"]+)">\s*\1\s*</a>',
        r"\1",
        citation_html,
        flags=re.IGNORECASE,
    )
    citation_html = re.sub(r"\s+", " ", citation_html).strip()
    return citation_html


def extract_authors_from_apa_citation(citation_apa: str) -> str:
    """Extract the author block from an APA citation string."""
    match = re.match(r"^(.*?)\s+\((?:n\.d\.|\d{4}[a-z]?)\)\.", citation_apa)
    return match.group(1).strip() if match else ""


def render_apa_citation(
    bibtex: str,
) -> str:
    """Render an APA citation from BibTeX via pybtex."""
    bibliography = parse_string(bibtex, "bibtex")
    style = find_plugin("pybtex.style.formatting", "apa")()
    backend = find_plugin("pybtex.backends", "html")()
    entries = list(style.format_bibliography(bibliography))
    if not entries:
        raise ValueError("No bibliography entry found in BibTeX.")
    return normalize_pybtex_html(entries[0].text.render(backend))


def extract_publication_venue(fields: Dict[str, str]) -> str:
    """Extract journal/booktitle venue for list-style rendering."""
    return fields.get("journal", fields.get("booktitle", "")).strip()


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
    citation_apa = render_apa_citation(bibtex)
    front_matter["citation_apa"] = citation_apa
    front_matter["authors"] = extract_authors_from_apa_citation(citation_apa)
    venue = extract_publication_venue(fields)
    if venue:
        front_matter["journal"] = venue
    front_matter["doi"] = publication_link(fields)

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
