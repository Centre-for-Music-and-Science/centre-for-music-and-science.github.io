import unittest

from scripts.generate_publication_citations import normalize_citeproc_html


class CitationPunctuationRuleTests(unittest.TestCase):
    def test_apa_title_ending_with_question_mark_has_no_trailing_period(self):
        citation_html = (
            "Doe, J. (2024). Why do people like music?. "
            "<em>Music Perception</em>, 12(3), 1-10."
        )
        out = normalize_citeproc_html(citation_html)
        self.assertIn(
            "Why do people like music? <em>Music Perception</em>",
            out,
        )
        self.assertNotIn("music?. <em>Music Perception</em>", out)

    def test_apa_title_ending_with_exclamation_mark_has_no_trailing_period(self):
        citation_html = (
            "Doe, J. (2024). Listen now!. "
            "<em>Music Perception</em>, 12(3), 1-10."
        )
        out = normalize_citeproc_html(citation_html)
        self.assertIn(
            "Listen now! <em>Music Perception</em>",
            out,
        )
        self.assertNotIn("Listen now!. <em>Music Perception</em>", out)

    def test_non_apa_quoted_title_ending_question_mark_has_no_period(self):
        citation_html = (
            "Tan, C. and P. M. C. Harrison. "
            "“What Music Do People Use for Mood Regulation?”. "
            "<em>Psychology of Music</em>, 2026."
        )
        out = normalize_citeproc_html(citation_html)
        self.assertIn(
            "“What Music Do People Use for Mood Regulation?” "
            "<em>Psychology of Music</em>",
            out,
        )
        self.assertNotIn("Regulation?”. <em>Psychology of Music</em>", out)


if __name__ == "__main__":
    unittest.main()
