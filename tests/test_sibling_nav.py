"""Smoke tests for opportunity and news sibling navigation."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("hugo"), "hugo not installed")
class SiblingNavSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmpdir = tempfile.TemporaryDirectory()
        cls.public = Path(cls._tmpdir.name) / "public"
        result = subprocess.run(
            [
                "hugo",
                "--destination",
                str(cls.public),
                "--minify",
                "--cleanDestinationDir",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "hugo build failed:\n"
                f"{result.stdout}\n{result.stderr}"
            )

    @classmethod
    def tearDownClass(cls):
        cls._tmpdir.cleanup()

    def _read(self, relative: str) -> str:
        path = self.public / relative
        self.assertTrue(path.is_file(), f"missing build output: {relative}")
        return path.read_text(encoding="utf-8")

    def test_opportunity_middle_links_prev_and_next_by_weight(self):
        html = self._read(
            "opportunities/computational-analysis-musical-style/index.html"
        )
        self.assertIn('aria-label="Research topics"', html)
        self.assertIn("Previous topic", html)
        self.assertIn("Next topic", html)
        self.assertIn("/opportunities/computational-music-cognition/", html)
        self.assertIn("/opportunities/music-pleasure/", html)

    def test_opportunity_first_has_next_only(self):
        html = self._read(
            "opportunities/computational-music-cognition/index.html"
        )
        self.assertIn("Next topic", html)
        self.assertIn("/opportunities/computational-analysis-musical-style/", html)
        self.assertNotIn("Previous topic", html)
        self.assertNotIn("/opportunities/microtonal-jazz/", html)

    def test_opportunity_last_has_prev_only(self):
        html = self._read("opportunities/microtonal-jazz/index.html")
        self.assertIn("Previous topic", html)
        self.assertIn(
            "/opportunities/individual-and-cross-cultural-differences/",
            html,
        )
        self.assertNotIn("Next topic", html)
        self.assertNotIn(
            "/opportunities/computational-music-cognition/",
            html,
        )

    def test_news_middle_links_newer_and_older_by_date(self):
        html = self._read(
            "news/british-academy-postdoctoral-fellowships-2026/index.html"
        )
        self.assertIn("sibling-nav", html)
        self.assertIn("Newer", html)
        self.assertIn("Older", html)
        self.assertIn("/news/sempre-pgr-ecr-conference-report-2026/", html)
        self.assertIn("/news/sempre-conference-registration-2026/", html)

    def test_news_newest_has_older_only(self):
        html = self._read(
            "news/sempre-pgr-ecr-conference-report-2026/index.html"
        )
        self.assertIn("Older", html)
        self.assertIn(
            "/news/british-academy-postdoctoral-fellowships-2026/",
            html,
        )
        self.assertNotIn("Newer", html)

    def test_news_oldest_has_newer_only(self):
        html = self._read("news/library-exhibition-2024/index.html")
        self.assertIn("Newer", html)
        self.assertIn("/news/jazz-trio-database-2024/", html)
        self.assertNotIn("Older", html)


if __name__ == "__main__":
    unittest.main()
