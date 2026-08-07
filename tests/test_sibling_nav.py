"""Smoke tests for topic and news sibling navigation."""

from __future__ import annotations

import unittest

from tests.hugo_smoke import HugoSiteSmokeTest


class SiblingNavSmokeTests(HugoSiteSmokeTest):
    def test_topic_middle_links_prev_and_next_by_weight(self):
        html = self._read(
            "topics/computational-analysis-musical-style/index.html"
        )
        self.assertIn('aria-label="Research topics"', html)
        self.assertIn("Previous topic", html)
        self.assertIn("Next topic", html)
        self.assertIn("/topics/computational-music-cognition/", html)
        self.assertIn("/topics/music-pleasure/", html)

    def test_topic_first_has_next_only(self):
        html = self._read(
            "topics/computational-music-cognition/index.html"
        )
        self.assertIn("Next topic", html)
        self.assertIn("/topics/computational-analysis-musical-style/", html)
        self.assertNotIn("Previous topic", html)
        self.assertNotIn("/topics/microtonal-jazz/", html)

    def test_topic_last_has_prev_only(self):
        html = self._read("topics/microtonal-jazz/index.html")
        self.assertIn("Previous topic", html)
        self.assertIn(
            "/topics/individual-and-cross-cultural-differences/",
            html,
        )
        self.assertNotIn("Next topic", html)
        self.assertNotIn(
            "/topics/computational-music-cognition/",
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
