"""Smoke tests for the applicants / topics page funnel."""

from __future__ import annotations

import unittest

from tests.hugo_smoke import HugoSiteSmokeTest


class ApplicantsFunnelSmokeTests(HugoSiteSmokeTest):
    def test_applicants_hub_links_to_pathways_not_topics_index(self):
        html = self._read("applicants/index.html")
        self.assertIn("/applicants/phd/", html)
        self.assertIn("/applicants/mphil/", html)
        self.assertNotIn("Explore research topics", html)
        self.assertNotIn("applicants-hub-primary", html)
        self.assertNotIn("/topics/", html)
        self.assertNotIn("applicants-nav-btn", html)
        self.assertNotIn("applicants-panel", html)

    def test_internships_card_is_non_clickable_stub(self):
        html = self._read("applicants/index.html")
        self.assertIn("Internships", html)
        self.assertIn(
            "Unfortunately we are currently unable to host internships at the CMS.",
            html,
        )
        self.assertIn("applicants-hub-card--stub", html)
        self.assertNotIn("/applicants/internships/", html)
        self.assertFalse(
            (self.public / "applicants" / "internships" / "index.html").is_file()
        )

    def test_pathway_pages_are_real_urls(self):
        html = self._read("applicants/phd/index.html")
        self.assertIn("PhD", html)
        self.assertIn("/applicants/", html)
        self.assertIn("applicants-pathway-tabs", html)
        self.assertIn("data-tab=programme", html)
        self.assertIn("data-tab=topics", html)
        self.assertIn("data-tab=prerequisites", html)
        self.assertIn("data-tab=finances", html)
        self.assertIn("data-tab=applying", html)
        self.assertIn("id=panel-programme", html)
        self.assertIn("id=panel-topics", html)
        self.assertIn("id=panel-prerequisites", html)
        self.assertIn("id=panel-finances", html)
        self.assertIn("id=panel-applying", html)
        # Tab order: Programme, Topics, Prerequisites, Finances, Applying.
        programme_tab = html.index("data-tab=programme")
        topics_tab = html.index("data-tab=topics")
        prerequisites_tab = html.index("data-tab=prerequisites")
        finances_tab = html.index("data-tab=finances")
        applying_tab = html.index("data-tab=applying")
        self.assertLess(programme_tab, topics_tab)
        self.assertLess(topics_tab, prerequisites_tab)
        self.assertLess(prerequisites_tab, finances_tab)
        self.assertLess(finances_tab, applying_tab)
        self.assertIn("/topics/computational-music-cognition/", html)
        self.assertIn("/topics/", html)
        self.assertIn("/people/peter-harrison/", html)
        self.assertIn(
            "We are currently offering PhD projects in the following areas.",
            html,
        )
        self.assertNotIn("data-tab=faq", html)
        self.assertNotIn("data-tab=about", html)

    def test_postdoctoral_pathway_tabs(self):
        html = self._read("applicants/postdoctoral-researchers/index.html")
        self.assertIn("applicants-pathway-tabs", html)
        self.assertIn("data-tab=overview", html)
        self.assertIn("data-tab=topics", html)
        self.assertIn("data-tab=funding", html)
        self.assertIn("data-tab=applying", html)
        self.assertIn("id=panel-overview", html)
        self.assertIn("id=panel-topics", html)
        self.assertIn("id=panel-funding", html)
        self.assertIn("id=panel-applying", html)
        overview_tab = html.index("data-tab=overview")
        topics_tab = html.index("data-tab=topics")
        funding_tab = html.index("data-tab=funding")
        applying_tab = html.index("data-tab=applying")
        self.assertLess(overview_tab, topics_tab)
        self.assertLess(topics_tab, funding_tab)
        self.assertLess(funding_tab, applying_tab)
        self.assertIn(
            "We particularly welcome fellowship proposals that connect with",
            html,
        )
        self.assertIn("/news/british-academy-postdoctoral-fellowships-2026/", html)
        self.assertNotIn("data-tab=about", html)
        self.assertNotIn("data-tab=faq", html)
        self.assertNotIn("data-tab=finances", html)
        self.assertIn("/topics/", html)

    def test_undergraduate_omits_topics_tab(self):
        html = self._read("applicants/undergraduate/index.html")
        self.assertIn("applicants-pathway-tabs", html)
        self.assertIn("id=panel-about", html)
        self.assertNotIn("applicants-pathway-tab-bar", html)
        self.assertNotIn("data-tab=about", html)
        self.assertNotIn("data-tab=topics", html)
        self.assertNotIn("id=panel-topics", html)
        self.assertNotIn("/topics/", html)

    def test_topics_list_is_the_brochure(self):
        html = self._read("topics/index.html")
        self.assertIn("Research topics", html)
        self.assertIn("/topics/computational-music-cognition/", html)
        self.assertIn("/applicants/", html)

    def test_topic_detail_shows_related_projects_and_publications(self):
        html = self._read(
            "topics/individual-and-cross-cultural-differences/index.html"
        )
        self.assertIn("Related projects", html)
        self.assertIn("/projects/emotions/", html)
        self.assertIn("/projects/consonance/", html)
        self.assertIn("Related publications", html)
        # Direct project-tagged publication.
        self.assertIn("lee-globalmood", html)
        # Descendant project (music-mood-regulation under emotions) publication.
        self.assertIn("tan-mood-regulation", html)

    def test_topic_detail_shows_supervisor_and_cosupervisors(self):
        html = self._read(
            "topics/individual-and-cross-cultural-differences/index.html"
        )
        self.assertIn("Supervisor:", html)
        self.assertIn("/people/peter-harrison/", html)
        self.assertIn("Possible cosupervisors", html)
        self.assertIn("/people/nori-jacoby/", html)
        self.assertIn("/people/daniel-mullensiefen/", html)
        self.assertIn("/people/harin-lee/", html)

    def test_collaborator_people_are_not_listed_on_people_index(self):
        html = self._read("people/index.html")
        self.assertNotIn("/people/nori-jacoby/", html)
        self.assertNotIn("/people/daniel-mullensiefen/", html)
        self.assertNotIn("/people/lars-seniuk/", html)
        # Detail pages still exist for linking from topics.
        self.assertTrue(
            (self.public / "people/nori-jacoby/index.html").is_file()
        )


if __name__ == "__main__":
    unittest.main()
