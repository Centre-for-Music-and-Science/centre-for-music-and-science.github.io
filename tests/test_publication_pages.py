"""Smoke tests for publication pages."""

from __future__ import annotations

import unittest

from tests.hugo_smoke import HugoSiteSmokeTest


class PublicationPageSmokeTests(HugoSiteSmokeTest):
    def test_publication_detail_shows_volume_issue_pages(self):
        html = self._read("publications/cheston-jazz-piano/index.html")
        self.assertIn("Nature Machine Intelligence", html)
        self.assertIn("8(8)", html)
        self.assertIn("1261–1274", html)
        self.assertIn("(2026)", html)

    def test_featured_publication_title_links_to_detail_page(self):
        html = self._read("publications/index.html")
        self.assertIn("href=/publications/cheston-jazz-piano/", html)
        self.assertIn("Machine learning of artistic fingerprints in jazz", html)

    def test_publication_detail_shows_related_project_and_app(self):
        html = self._read("publications/cheston-jazz-piano/index.html")
        self.assertIn("Related projects", html)
        self.assertIn("href=/projects/jazz/", html)
        self.assertIn("Related apps", html)
        self.assertIn("href=/explore/jazz-piano-styles/", html)
        self.assertIn("Jazz piano style explorer", html)

    def test_publication_detail_shows_optional_media_coverage(self):
        html = self._read("publications/cheston-jazz-piano/index.html")
        self.assertIn("Media coverage", html)
        self.assertIn("Scientific American", html)
        self.assertIn(
            "https://www.scientificamerican.com/article/ai-decodes-the-mathematical-fingerprints-of-famous-jazz-musicians-from-chick-corea-to-thelonious-monk/",
            html,
        )
        self.assertIn("https://phys.org/news/2026-08-iconic-jazz-musicians.html", html)
        self.assertIn(
            "https://www.iflscience.com/jazz-musicians-leave-hidden-fingerprints-in-their-work-newly-trained-computer-models-can-identify-them-with-over-90-percent-accuracy-84409",
            html,
        )

    def test_publication_detail_omits_media_coverage_when_unset(self):
        html = self._read("publications/tan-mood-regulation/index.html")
        self.assertNotIn("Media coverage", html)


if __name__ == "__main__":
    unittest.main()
