"""Helpers for applicant topic front matter."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def split_front_matter(content: str) -> tuple[dict[str, Any], str]:
    """Split a markdown document into YAML front matter and body."""
    if not content.startswith("---"):
        raise ValueError("File does not contain YAML front matter.")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError("File does not contain YAML front matter.")
    front_matter = yaml.safe_load(parts[1]) or {}
    return front_matter, parts[2]


def topic_open(front_matter: dict[str, Any]) -> bool:
    """Return whether a topic should appear in the brochure.

    Defaults to True when ``open`` is omitted.
    """
    if "open" not in front_matter:
        return True
    return bool(front_matter["open"])


def topic_projects(front_matter: dict[str, Any]) -> list[str]:
    """Return linked project slugs."""
    projects = front_matter.get("projects") or []
    if not isinstance(projects, list):
        raise ValueError("projects must be a list")
    return [
        str(project).strip()
        for project in projects
        if str(project).strip()
    ]


def topic_publications(front_matter: dict[str, Any]) -> list[str]:
    """Return linked publication slugs."""
    publications = front_matter.get("publications") or []
    if not isinstance(publications, list):
        raise ValueError("publications must be a list")
    return [
        str(publication).strip()
        for publication in publications
        if str(publication).strip()
    ]


def topic_supervisor(front_matter: dict[str, Any]) -> str | None:
    """Return the linked supervisor person slug, if set."""
    if "supervisor" not in front_matter:
        return None
    supervisor = front_matter["supervisor"]
    if not isinstance(supervisor, str):
        raise ValueError("supervisor must be a string")
    supervisor = supervisor.strip()
    return supervisor or None


def topic_cosupervisors(front_matter: dict[str, Any]) -> list[str]:
    """Return linked possible-cosupervisor person slugs."""
    cosupervisors = front_matter.get("cosupervisors") or []
    if not isinstance(cosupervisors, list):
        raise ValueError("cosupervisors must be a list")
    return [
        str(person).strip()
        for person in cosupervisors
        if str(person).strip()
    ]


def validate_topic(
    slug: str,
    front_matter: dict[str, Any],
    *,
    project_slugs: set[str] | None = None,
    publication_slugs: set[str] | None = None,
    people_slugs: set[str] | None = None,
) -> list[str]:
    """Validate front matter for one topic record.

    Parameters
    ----------
    slug :
        Topic content basename.
    front_matter :
        Parsed YAML front matter.
    project_slugs :
        Optional set of valid project slugs for ``projects`` checks.
    publication_slugs :
        Optional set of valid publication slugs for ``publications`` checks.
    people_slugs :
        Optional set of valid people slugs for ``supervisor`` /
        ``cosupervisors`` checks.

    Returns
    -------
    list of str
        Human-readable error messages (empty if valid).
    """
    errors: list[str] = []

    if "open" in front_matter and not isinstance(front_matter["open"], bool):
        errors.append(f"topic {slug!r}: open must be a boolean")

    if "collaborators" in front_matter:
        errors.append(
            f"topic {slug!r}: collaborators is no longer supported; "
            "use cosupervisors with person slugs"
        )

    if "supervisor" in front_matter:
        supervisor = front_matter["supervisor"]
        if not isinstance(supervisor, str) or not supervisor.strip():
            errors.append(
                f"topic {slug!r}: supervisor must be a "
                "non-empty string"
            )
        elif people_slugs is not None and supervisor.strip() not in people_slugs:
            errors.append(
                f"topic {slug!r}: person {supervisor.strip()!r} "
                "does not exist"
            )

    cosupervisors = front_matter.get("cosupervisors")
    if cosupervisors is not None and not isinstance(cosupervisors, list):
        errors.append(f"topic {slug!r}: cosupervisors must be a list")
    elif any(
        not isinstance(person, str) or not person.strip()
        for person in (cosupervisors or [])
    ):
        errors.append(
            f"topic {slug!r}: cosupervisor slugs must be "
            "non-empty strings"
        )
    elif people_slugs is not None:
        for person in topic_cosupervisors(front_matter):
            if person in people_slugs:
                continue
            errors.append(
                f"topic {slug!r}: person {person!r} does not exist"
            )

    projects = front_matter.get("projects")
    if projects is not None and not isinstance(projects, list):
        errors.append(f"topic {slug!r}: projects must be a list")
    elif project_slugs is not None:
        for project in topic_projects(front_matter):
            if project in project_slugs:
                continue
            errors.append(
                f"topic {slug!r}: project {project!r} does not exist"
            )

    publications = front_matter.get("publications")
    if publications is not None and not isinstance(publications, list):
        errors.append(f"topic {slug!r}: publications must be a list")
    elif publication_slugs is not None:
        for publication in topic_publications(front_matter):
            if publication in publication_slugs:
                continue
            errors.append(
                f"topic {slug!r}: publication {publication!r} "
                "does not exist"
            )

    return errors


def validate_topics_dir(
    topics_dir: Path,
    *,
    projects_dir: Path | None = None,
    publications_dir: Path | None = None,
    people_dir: Path | None = None,
) -> list[str]:
    """Validate all topic markdown files under ``topics_dir``."""
    project_slugs: set[str] | None = None
    if projects_dir is not None:
        project_slugs = {
            path.stem
            for path in projects_dir.glob("*.md")
            if not path.name.startswith("_")
        }

    publication_slugs: set[str] | None = None
    if publications_dir is not None:
        publication_slugs = {
            path.stem
            for path in publications_dir.glob("*.md")
            if not path.name.startswith("_")
        }

    people_slugs: set[str] | None = None
    if people_dir is not None:
        people_slugs = {
            path.stem
            for path in people_dir.glob("*.md")
            if not path.name.startswith("_")
        }

    errors: list[str] = []
    for path in sorted(topics_dir.glob("*.md")):
        if path.name.startswith("_"):
            continue
        front_matter, _ = split_front_matter(path.read_text(encoding="utf-8"))
        errors.extend(
            validate_topic(
                path.stem,
                front_matter,
                project_slugs=project_slugs,
                publication_slugs=publication_slugs,
                people_slugs=people_slugs,
            )
        )
    return errors


def filter_open_topics(
    topics: list[tuple[str, dict[str, Any]]],
) -> list[tuple[str, dict[str, Any]]]:
    """Keep open topics."""
    result: list[tuple[str, dict[str, Any]]] = []
    for slug, fm in topics:
        if not topic_open(fm):
            continue
        result.append((slug, fm))
    return result
