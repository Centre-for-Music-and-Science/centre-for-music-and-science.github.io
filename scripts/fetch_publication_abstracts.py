#!/usr/bin/env python3
"""Fill publication ``abstract`` from CrossRef, OpenAlex, then the landing-page HTML."""

from __future__ import annotations

import argparse
import html as html_module
import re
import sys
import time
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from urllib.parse import quote
from urllib.parse import urlparse

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import requests
from bs4 import BeautifulSoup

from scripts.generate_publication_citations import build_front_matter_text
from scripts.generate_publication_citations import split_front_matter

USER_AGENT = (
    "CMSPublicationFetcher/1.0 "
    "(+https://centre-for-music-and-science.github.io; research site maintenance)"
)
REQUEST_TIMEOUT = 28
CROSSREF_DELAY_S = 0.35
OPENALEX_DELAY_S = 0.25
PAGE_DELAY_S = 1.0


def doi_from_params(doi_param: Any) -> Optional[str]:
    """Return a raw DOI (10.x/...) if the param looks like a DOI link or id."""
    if not doi_param or not isinstance(doi_param, str):
        return None
    s = doi_param.strip()
    m = re.search(r"(10\.\d{4,9}/[^\s\"'<>]+)", s, re.I)
    return m.group(1).rstrip(".,);]") if m else None


def arxiv_landing_url(doi_or_url: str) -> Optional[str]:
    """Map arXiv DOI or URL to https://arxiv.org/abs/<id> when possible."""
    m = re.search(
        r"(?:arxiv\.org/(?:abs|pdf)/|arxiv\.)(\d{4}\.\d{5,})(?:v\d+)?",
        doi_or_url,
        re.I,
    )
    if m:
        return f"https://arxiv.org/abs/{m.group(1)}"
    m = re.search(r"10\.48550/arxiv\.(\d{4}\.\d{5,})", doi_or_url, re.I)
    if m:
        return f"https://arxiv.org/abs/{m.group(1)}"
    return None


def normalize_crossref_abstract(raw: Any) -> Optional[str]:
    """Turn CrossRef ``message.abstract`` into plain text."""
    if raw is None:
        return None
    if isinstance(raw, list):
        chunks: list[str] = []
        for item in raw:
            if isinstance(item, dict):
                t = item.get("text")
                if isinstance(t, str):
                    chunks.append(t)
            elif isinstance(item, str):
                chunks.append(item)
        text = " ".join(chunks) if chunks else ""
    else:
        text = str(raw)
    if not text.strip():
        return None
    text = re.sub(r"<jats:title>\s*Abstract\s*</jats:title>", "", text, flags=re.I)
    text = re.sub(r"</?jats:[^>]+>", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_module.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if text.lower().startswith("abstract"):
        text = text[8:].lstrip(" :.—-\u2014\u2212").strip()
    return text or None


def fetch_crossref_abstract(session: requests.Session, doi: str) -> Optional[str]:
    """Request abstract for a DOI from the CrossRef REST API."""
    url = f"https://api.crossref.org/works/{quote(doi, safe=':')}"
    r = session.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    if r.status_code != 200:
        return None
    data = r.json()
    msg = data.get("message") or {}
    return normalize_crossref_abstract(msg.get("abstract"))


def abstract_from_openalex_inverted_index(inv: Any) -> Optional[str]:
    """Rebuild abstract text from OpenAlex ``abstract_inverted_index``."""
    if not inv or not isinstance(inv, dict):
        return None
    pairs: list[tuple[int, str]] = []
    for word, positions in inv.items():
        if not isinstance(word, str):
            continue
        if isinstance(positions, list):
            for pos in positions:
                if isinstance(pos, int):
                    pairs.append((pos, word))
    if not pairs:
        return None
    pairs.sort(key=lambda x: x[0])
    text = " ".join(w for _, w in pairs)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def fetch_openalex_abstract(session: requests.Session, doi: str) -> Optional[str]:
    """Request abstract for a DOI from the OpenAlex API."""
    url = f"https://api.openalex.org/works/https://doi.org/{quote(doi, safe=':')}"
    r = session.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    if r.status_code != 200:
        return None
    work = r.json()
    return abstract_from_openalex_inverted_index(
        work.get("abstract_inverted_index"),
    )


def _meta_contents(soup: BeautifulSoup, attrs: dict[str, Any]) -> list[str]:
    """Collect ``content`` from ``meta`` tags matching ``attrs``."""
    out: list[str] = []
    for tag in soup.find_all("meta", attrs=attrs):
        c = tag.get("content")
        if c and isinstance(c, str) and c.strip():
            out.append(html_module.unescape(c.strip()))
    return out


def extract_abstract_from_html(page_html: str, page_url: str) -> Optional[str]:
    """Best-effort abstract extraction from publisher HTML."""
    soup = BeautifulSoup(page_html, "html.parser")

    for name in ("citation_abstract", "dc.Description", "dc.description"):
        parts = _meta_contents(
            soup,
            {"name": re.compile(f"^{re.escape(name)}$", re.I)},
        )
        if parts:
            text = re.sub(r"\s+", " ", " ".join(parts)).strip()
            if len(text) > 80:
                return text

    og = _meta_contents(soup, {"property": "og:description"})
    if og:
        text = re.sub(r"\s+", " ", og[0]).strip()
        if len(text) > 120 and not re.search(
            r"\b(sign up|subscribe|cookie)\b", text, re.I
        ):
            return text

    for sel in (
        "#abstract",
        "div#abstract",
        "blockquote.abstract",
        "blockquote.latexmath",
        ".abstract.mathjax",
        "div.abstract",
        "section.abstract",
        "[data-test='abstract']",
        "[id*='abstract'][class*='Abstract']",
        ".c-article-section__content",
        ".ArticleAbstract",
    ):
        node = soup.select_one(sel)
        if node:
            text = node.get_text(separator=" ", strip=True)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) > 80:
                if text.lower().startswith("abstract"):
                    text = text[8:].lstrip(" :.—-\u2014").strip()
                return text

    return None


def fetch_page_abstract(session: requests.Session, url: str) -> Optional[str]:
    """GET a URL and parse an abstract from HTML."""
    r = session.get(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
        },
        timeout=REQUEST_TIMEOUT,
        allow_redirects=True,
    )
    if r.status_code != 200 or not r.text:
        return None
    return extract_abstract_from_html(r.text, r.url)


def candidate_urls(doi_param: Any) -> list[str]:
    """Ordered list of URLs to try for HTML fallback."""
    if not doi_param or not isinstance(doi_param, str):
        return []
    raw = doi_param.strip()
    urls: list[str] = []
    seen: set[str] = set()

    def add(u: str) -> None:
        if u not in seen:
            seen.add(u)
            urls.append(u)

    arx = arxiv_landing_url(raw)
    if arx:
        add(arx)

    if raw.startswith(("http://", "https://")):
        add(raw)

    d = doi_from_params(raw)
    if d:
        add(f"https://doi.org/{d}")

    return urls


def merge_abstract(front_matter: Dict[str, Any], abstract: str) -> Dict[str, Any]:
    """Return front matter with ``abstract`` inserted after ``doi`` if present."""
    base = {k: v for k, v in front_matter.items() if k != "abstract"}
    out: Dict[str, Any] = {}
    inserted = False
    for key, val in base.items():
        if key == "bibtex" and "doi" not in base and not inserted:
            out["abstract"] = abstract
            inserted = True
        out[key] = val
        if key == "doi" and not inserted:
            out["abstract"] = abstract
            inserted = True
    if not inserted:
        out["abstract"] = abstract
    return out


def publication_has_nonempty_abstract(front_matter: Dict[str, Any]) -> bool:
    a = front_matter.get("abstract")
    return bool(a and str(a).strip())


def update_file(
    path: Path,
    session: requests.Session,
    *,
    force: bool,
    dry_run: bool,
) -> tuple[bool, str]:
    """
    Return (changed, status_message).
    """
    text = path.read_text(encoding="utf-8")
    front_matter, body = split_front_matter(text)

    if publication_has_nonempty_abstract(front_matter) and not force:
        return False, "skip (abstract already set)"

    doi_param = front_matter.get("doi")
    abstract: Optional[str] = None
    source = ""

    d = doi_from_params(doi_param)
    if d:
        time.sleep(CROSSREF_DELAY_S)
        abstract = fetch_crossref_abstract(session, d)
        if abstract:
            source = "crossref"

    if not abstract and d:
        time.sleep(OPENALEX_DELAY_S)
        abstract = fetch_openalex_abstract(session, d)
        if abstract:
            source = "openalex"

    if not abstract:
        for url in candidate_urls(doi_param):
            time.sleep(PAGE_DELAY_S)
            abstract = fetch_page_abstract(session, url)
            if abstract:
                source = f"html:{urlparse(url).netloc}"
                break

    if not abstract:
        return False, "no abstract found"

    abstract = re.sub(r"\s+", " ", abstract).strip()
    new_fm = merge_abstract(front_matter, abstract)
    new_text = build_front_matter_text(new_fm) + body

    if new_text == text:
        return False, "unchanged"

    if dry_run:
        return False, f"dry-run would write ({source}, {len(abstract)} chars)"

    path.write_text(new_text, encoding="utf-8")
    return True, f"updated ({source}, {len(abstract)} chars)"


def main() -> int:
    """Fetch abstracts for publication markdown files."""
    parser = argparse.ArgumentParser(
        description=(
            "Fill abstract from CrossRef, OpenAlex (by DOI), then publication HTML."
        ),
    )
    parser.add_argument(
        "publications_dir",
        nargs="?",
        default="content/publications",
        help="Directory of publication markdown files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing non-empty abstract fields.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write files; report what would happen.",
    )
    args = parser.parse_args()
    root = Path(args.publications_dir)
    if not root.is_dir():
        print(f"Directory not found: {root}", file=sys.stderr)
        return 1

    session = requests.Session()
    changed = 0
    skipped = 0
    failed = 0

    paths = sorted(p for p in root.glob("*.md") if not p.name.startswith("_"))
    for path in paths:
        try:
            did_change, msg = update_file(
                path, session, force=args.force, dry_run=args.dry_run
            )
        except (requests.RequestException, ValueError) as exc:
            failed += 1
            print(f"{path.name}: error {exc}", file=sys.stderr)
            continue
        if did_change:
            changed += 1
        elif "skip" in msg or "dry-run" in msg or msg == "unchanged":
            skipped += 1
        elif "no abstract" in msg:
            failed += 1
        print(f"{path.name}: {msg}")

    print(
        f"Done. updated={changed}, skipped/other={skipped}, "
        f"no abstract or errors={failed}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
