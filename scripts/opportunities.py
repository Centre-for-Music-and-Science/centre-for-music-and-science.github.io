"""Helpers for applicant opportunity front matter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

APPLICATION_LEVELS = (
    "undergraduate",
    "mphil",
    "phd",
    "postdoc",
    "internship",
    "visitor",
)

LEVEL_LABELS = {
    "undergraduate": "Undergraduate",
    "mphil": "MPhil",
    "phd": "PhD",
    "postdoc": "Postdoctoral",
    "internship": "Internship",
    "visitor": "Visitor",
}

APPLICANT_PAGE_LEVELS = {
    "undergraduate": "undergraduate",
    "mphil": "mphil",
    "phd": "phd",
    "postdoctoral-researchers": "postdoc",
    "internships": "internship",
    "visitors": "visitor",
}


def split_front_matter(content: str) -> tuple[dict[str, Any], str]:
    """Split a markdown document into YAML front matter and body."""
    if not content.startswith("---"):
        raise ValueError("File does not contain YAML front matter.")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("File does not contain YAML front matter.")
    front_matter = yaml.safe_load(parts[1]) or {}
    return front_matter, parts[2]


def opportunity_open(front_matter: dict[str, Any]) -> bool:
    """Return whether an opportunity should appear in the brochure.

    Defaults to True when ``open`` is omitted.
    """
    if "open" not in front_matter:
        return True
    return bool(front_matter["open"])


def opportunity_levels(front_matter: dict[str, Any]) -> list[str]:
    """Return the list of application levels for an opportunity."""
    levels = front_matter.get("levels") or []
    if not isinstance(levels, list):
        raise ValueError("levels must be a list")
    return [str(level) for level in levels]


def opportunity_projects(front_matter: dict[str, Any]) -> list[str]:
    """Return linked project slugs."""
    projects = front_matter.get("projects") or []
    if not isinstance(projects, list):
        raise ValueError("projects must be a list")
    return [str(project).strip() for project in projects if str(project).strip()]


def validate_opportunity(
    slug: str,
    front_matter: dict[str, Any],
    *,
    project_slugs: set[str] | None = None,
) -> list[str]:
    """Validate front matter for one opportunity record.

    Parameters
    ----------
    slug :
        Opportunity content basename.
    front_matter :
        Parsed YAML front matter.
    project_slugs :
        Optional set of valid project slugs for ``projects`` checks.

    Returns
    -------
    list of str
        Human-readable error messages (empty if valid).
    """
    errors: list[str] = []

    if "open" in front_matter and not isinstance(front_matter["open"], bool):
        errors.append(f"opportunity {slug!r}: open must be a boolean")

    levels = front_matter.get("levels")
    if levels is not None and not isinstance(levels, list):
        errors.append(f"opportunity {slug!r}: levels must be a list")
        return errors

    level_list = [str(level) for level in (levels or [])]
    for level in level_list:
        if level not in APPLICATION_LEVELS:
            errors.append(
                f"opportunity {slug!r}: unknown level {level!r}; "
                f"expected one of {', '.join(APPLICATION_LEVELS)}"
            )

    is_open = opportunity_open(front_matter)
    if is_open and not level_list:
        errors.append(
            f"opportunity {slug!r}: open is true but levels is empty"
        )

    projects = front_matter.get("projects")
    if projects is not None and not isinstance(projects, list):
        errors.append(f"opportunity {slug!r}: projects must be a list")
        return errors

    if project_slugs is not None:
        for project in opportunity_projects(front_matter):
            if project in project_slugs:
                continue
            errors.append(
                f"opportunity {slug!r}: project {project!r} does not exist"
            )

    return errors


def validate_opportunities_dir(
    opportunities_dir: Path,
    *,
    projects_dir: Path | None = None,
) -> list[str]:
    """Validate all opportunity markdown files under ``opportunities_dir``."""
    project_slugs: set[str] | None = None
    if projects_dir is not None:
        project_slugs = {
            path.stem
            for path in projects_dir.glob("*.md")
            if not path.name.startswith("_")
        }

    errors: list[str] = []
    for path in sorted(opportunities_dir.glob("*.md")):
        if path.name.startswith("_"):
            continue
        front_matter, _ = split_front_matter(path.read_text(encoding="utf-8"))
        errors.extend(
            validate_opportunity(
                path.stem,
                front_matter,
                project_slugs=project_slugs,
            )
        )
    return errors


def filter_open_opportunities(
    opportunities: list[tuple[str, dict[str, Any]]],
    *,
    level: str | None = None,
) -> list[tuple[str, dict[str, Any]]]:
    """Keep open opportunities, optionally filtered by level."""
    result: list[tuple[str, dict[str, Any]]] = []
    for slug, fm in opportunities:
        if not opportunity_open(fm):
            continue
        if level is not None and level not in opportunity_levels(fm):
            continue
        result.append((slug, fm))
    return result
