import unittest

from scripts.generate_publication_citations import format_authors_apa
from scripts.generate_publication_citations import normalize_doi
from scripts.generate_publication_citations import parse_bibtex_fields
from scripts.generate_publication_citations import render_apa_citation


class PublicationCitationTests(unittest.TestCase):
    def test_parse_bibtex_fields_extracts_common_fields(self):
        bibtex = """
        @article{frank2026,
          author = {Frank, Joshua and Harrison, Peter M. C.},
          title = {
            Modeling individual differences in chord pleasantness judgments
          },
          journal = {Psychology of Aesthetics, Creativity, and the Arts},
          year = {2026},
          doi = {10.1037/aca0000836}
        }
        """
        fields = parse_bibtex_fields(bibtex)
        self.assertEqual(fields["year"], "2026")
        self.assertEqual(fields["doi"], "10.1037/aca0000836")
        self.assertIn("Modeling individual differences", fields["title"])

    def test_format_authors_apa_handles_ampersand_joining(self):
        authors = format_authors_apa("Frank, Joshua and Harrison, Peter M. C.")
        self.assertEqual(authors, "Frank, J., & Harrison, P. M. C.")

    def test_render_apa_citation_includes_journal_and_doi(self):
        fields = {
            "author": "Frank, Joshua and Harrison, Peter M. C.",
            "year": "2026",
            "title": (
                "Modeling individual differences in chord pleasantness judgments"
            ),
            "journal": "Psychology of Aesthetics, Creativity, and the Arts",
            "volume": "20",
            "number": "1",
            "pages": "10--21",
            "doi": "10.1037/aca0000836",
        }
        citation = render_apa_citation(fields)
        self.assertIn("Frank, J., & Harrison, P. M. C. (2026).", citation)
        self.assertIn(
            (
                "<em>Psychology of Aesthetics, Creativity, and the Arts</em>, "
                "20(1), 10-21."
            ),
            citation,
        )
        self.assertTrue(citation.endswith("https://doi.org/10.1037/aca0000836"))

    def test_normalize_doi_accepts_url_or_raw(self):
        self.assertEqual(
            normalize_doi("https://doi.org/10.1000/xyz"),
            "https://doi.org/10.1000/xyz",
        )
        self.assertEqual(
            normalize_doi("10.1000/xyz"),
            "https://doi.org/10.1000/xyz",
        )


if __name__ == "__main__":
    unittest.main()
