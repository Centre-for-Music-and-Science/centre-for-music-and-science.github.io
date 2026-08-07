"""Tests for applicant opportunity front-matter helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.opportunities import (
    filter_open_opportunities,
    opportunity_cosupervisors,
    opportunity_open,
    opportunity_projects,
    opportunity_publications,
    opportunity_supervisor,
    validate_opportunities_dir,
    validate_opportunity,
)


class OpportunityOpenTests(unittest.TestCase):
    def test_defaults_to_true_when_omitted(self):
        self.assertTrue(opportunity_open({}))

    def test_respects_explicit_false(self):
        self.assertFalse(opportunity_open({"open": False}))


class ValidationTests(unittest.TestCase):
    def test_open_without_levels_is_valid(self):
        errors = validate_opportunity(
            "melodic-memory",
            {"open": True},
        )
        self.assertEqual(errors, [])

    def test_missing_project_slug_is_rejected(self):
        errors = validate_opportunity(
            "melodic-memory",
            {"open": True, "projects": ["memory", "nope"]},
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
                "projects": ["memory", "expectation"],
            },
            project_slugs={"memory", "expectation"},
        )
        self.assertEqual(errors, [])

    def test_projects_must_be_a_list(self):
        errors = validate_opportunity(
            "melodic-memory",
            {"open": True, "projects": "memory"},
            project_slugs={"memory"},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("projects must be a list", errors[0])

    def test_missing_publication_slug_is_rejected(self):
        errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "publications": ["lee-globalmood", "nope"],
            },
            publication_slugs={"lee-globalmood"},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0])

    def test_multiple_publications_are_supported(self):
        self.assertEqual(
            opportunity_publications(
                {
                    "publications": [
                        "lee-globalmood",
                        "frank-chord-pleasantness",
                    ]
                }
            ),
            ["lee-globalmood", "frank-chord-pleasantness"],
        )
        errors = validate_opportunity(
            "combined-topic",
            {
                "open": True,
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
                "publications": "lee-globalmood",
            },
            publication_slugs={"lee-globalmood"},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("publications must be a list", errors[0])

    def test_person_slug_supervisor_is_valid(self):
        self.assertEqual(
            opportunity_supervisor({"supervisor": "peter-harrison"}),
            "peter-harrison",
        )
        errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "supervisor": "peter-harrison",
            },
            people_slugs={"peter-harrison"},
        )
        self.assertEqual(errors, [])

    def test_missing_supervisor_slug_is_rejected(self):
        errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "supervisor": "nope",
            },
            people_slugs={"peter-harrison"},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0])

    def test_supervisor_must_be_a_non_empty_string(self):
        errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "supervisor": ["peter-harrison"],
            },
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("supervisor must be a non-empty string", errors[0])

    def test_person_slug_cosupervisors_are_valid(self):
        self.assertEqual(
            opportunity_cosupervisors(
                {"cosupervisors": ["harin-lee", "nori-jacoby"]}
            ),
            ["harin-lee", "nori-jacoby"],
        )
        errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "cosupervisors": ["harin-lee", "nori-jacoby"],
            },
            people_slugs={"harin-lee", "nori-jacoby"},
        )
        self.assertEqual(errors, [])

    def test_missing_cosupervisor_slug_is_rejected(self):
        errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "cosupervisors": ["harin-lee", "nope"],
            },
            people_slugs={"harin-lee"},
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0])

    def test_cosupervisors_must_be_a_list_of_slugs(self):
        scalar_errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "cosupervisors": "harin-lee",
            },
        )
        item_errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "cosupervisors": [{"slug": "harin-lee"}],
            },
        )
        self.assertIn("cosupervisors must be a list", scalar_errors[0])
        self.assertIn(
            "cosupervisor slugs must be non-empty strings", item_errors[0]
        )

    def test_legacy_collaborators_field_is_rejected(self):
        errors = validate_opportunity(
            "melodic-memory",
            {
                "open": True,
                "collaborators": ["Alex Smith"],
            },
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("collaborators is no longer supported", errors[0])


class FilterTests(unittest.TestCase):
    def test_filters_out_closed_opportunities(self):
        opportunities = [
            ("a", {"open": True}),
            ("b", {}),
            ("c", {"open": False}),
        ]
        open_opportunities = filter_open_opportunities(opportunities)
        self.assertEqual([slug for slug, _ in open_opportunities], ["a", "b"])


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
                "---\ntitle: Ok\nopen: true\n"
                "projects: [memory]\npublications: [lee-globalmood]\n---\n",
                encoding="utf-8",
            )
            (opps / "bad.md").write_text(
                '---\ntitle: Bad\nopen: "yes"\n---\n',
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
