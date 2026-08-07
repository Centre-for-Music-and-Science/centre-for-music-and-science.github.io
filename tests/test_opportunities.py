"""Tests for applicant opportunity front-matter helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.opportunities import (
    APPLICATION_LEVELS,
    filter_open_opportunities,
    opportunity_open,
    opportunity_projects,
    opportunity_publications,
    validate_opportunities_dir,
    validate_opportunity,
)


class OpportunityOpenTests(unittest.TestCase):
    def test_defaults_to_true_when_omitted(self):
        self.assertTrue(opportunity_open({}))

    def test_respects_explicit_false(self):
        self.assertFalse(opportunity_open({"open": False}))


class ValidationTests(unittest.TestCase):
    def test_open_requires_levels(self):
        errors = validate_opportunity(
            "melodic-memory",
            {"open": True, "levels": []},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("levels is empty", errors[0])

    def test_open_with_levels_is_valid(self):
        errors = validate_opportunity(
            "melodic-memory",
            {"open": True, "levels": ["phd", "mphil"]},
        )
        self.assertEqual(errors, [])

    def test_unknown_level_is_rejected(self):
        errors = validate_opportunity(
            "melodic-memory",
            {"open": True, "levels": ["masters"]},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("unknown level", errors[0])

    def test_closed_with_no_levels_is_valid(self):
        errors = validate_opportunity(
            "melodic-memory",
            {"open": False},
        )
        self.assertEqual(errors, [])

    def test_missing_project_slug_is_rejected(self):
        errors = validate_opportunity(
            "melodic-memory",
            {"open": True, "levels": ["phd"], "projects": ["memory", "nope"]},
            project_slugs={"memory"},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0])

    def test_multiple_projects_are_supported(self):
        self.assertEqual(
            opportunity_projects({"projects": ["memory", "expectation"]}),
            ["memory", "expectation"],
        )
        errors = validate_opportunity(
            "combined-topic",
            {
                "open": True,
                "levels": ["phd"],
                "projects": ["memory", "expectation"],
            },
            project_slugs={"memory", "expectation"},
        )
        self.assertEqual(errors, [])

    def test_projects_must_be_a_list(self):
        errors = validate_opportunity(
            "melodic-memory",
            {"open": True, "levels": ["phd"], "projects": "memory"},
            project_slugs={"memory"},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("projects must be a list", errors[0])

    def test_missing_publication_slug_is_rejected(self):
        errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "levels": ["phd"],
                "publications": ["lee-globalmood", "nope"],
            },
            publication_slugs={"lee-globalmood"},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0])

    def test_multiple_publications_are_supported(self):
        self.assertEqual(
            opportunity_publications(
                {"publications": ["lee-globalmood", "frank-chord-pleasantness"]}
            ),
            ["lee-globalmood", "frank-chord-pleasantness"],
        )
        errors = validate_opportunity(
            "combined-topic",
            {
                "open": True,
                "levels": ["phd"],
                "publications": ["lee-globalmood", "frank-chord-pleasantness"],
            },
            publication_slugs={"lee-globalmood", "frank-chord-pleasantness"},
        )
        self.assertEqual(errors, [])

    def test_publications_must_be_a_list(self):
        errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "levels": ["phd"],
                "publications": "lee-globalmood",
            },
            publication_slugs={"lee-globalmood"},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("publications must be a list", errors[0])

    def test_quoted_collaborator_names_are_valid(self):
        errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "levels": ["phd"],
                "collaborators": ["Alex Smith", "Sam Jones"],
            },
        )
        self.assertEqual(errors, [])

    def test_collaborators_must_be_a_list_of_names(self):
        scalar_errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "levels": ["phd"],
                "collaborators": "Alex Smith",
            },
        )
        item_errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "levels": ["phd"],
                "collaborators": [{"name": "Alex Smith"}],
            },
        )
        self.assertIn("collaborators must be a list", scalar_errors[0])
        self.assertIn(
            "collaborator names must be non-empty strings", item_errors[0]
        )

    def test_known_levels_enum_is_complete(self):
        self.assertEqual(
            set(APPLICATION_LEVELS),
            {
                "undergraduate",
                "mphil",
                "phd",
                "postdoc",
                "internship",
                "visitor",
            },
        )


class FilterTests(unittest.TestCase):
    def test_filter_open_by_level(self):
        opportunities = [
            ("a", {"open": True, "levels": ["phd"]}),
            ("b", {"open": True, "levels": ["mphil", "phd"]}),
            ("c", {"open": False, "levels": ["phd"]}),
            ("d", {"open": True, "levels": ["undergraduate"]}),
        ]
        phd = filter_open_opportunities(opportunities, level="phd")
        self.assertEqual([slug for slug, _ in phd], ["a", "b"])
        undergrad = filter_open_opportunities(
            opportunities, level="undergraduate"
        )
        self.assertEqual([slug for slug, _ in undergrad], ["d"])


class OpportunitiesDirValidationTests(unittest.TestCase):
    def test_validate_opportunities_dir_reports_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            opps = root / "opportunities"
            projects = root / "projects"
            opps.mkdir()
            projects.mkdir()
            (projects / "memory.md").write_text(
                "---\ntitle: Memory\n---\n",
                encoding="utf-8",
            )
            publications = root / "publications"
            publications.mkdir()
            (publications / "lee-globalmood.md").write_text(
                "---\ntitle: GlobalMood\n---\n",
                encoding="utf-8",
            )
            (opps / "ok.md").write_text(
                "---\ntitle: Ok\nopen: true\nlevels: [phd]\n"
                "projects: [memory]\npublications: [lee-globalmood]\n---\n",
                encoding="utf-8",
            )
            (opps / "bad.md").write_text(
                "---\ntitle: Bad\nopen: true\nlevels: []\n---\n",
                encoding="utf-8",
            )
            (opps / "_index.md").write_text(
                "---\ntitle: Index\n---\n",
                encoding="utf-8",
            )
            errors = validate_opportunities_dir(
                opps,
                projects_dir=projects,
                publications_dir=publications,
            )
            self.assertEqual(len(errors), 1)
            self.assertIn("bad", errors[0])


if __name__ == "__main__":
    unittest.main()
