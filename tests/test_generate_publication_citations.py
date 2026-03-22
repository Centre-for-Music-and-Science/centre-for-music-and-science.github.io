import unittest

from scripts.generate_publication_citations import build_front_matter_text
from scripts.generate_publication_citations import (
    extract_authors_from_apa_citation,
)
from scripts.generate_publication_citations import extract_publication_venue
from scripts.generate_publication_citations import inject_autogen_comments
from scripts.generate_publication_citations import normalize_citeproc_html
from scripts.generate_publication_citations import normalize_doi
from scripts.generate_publication_citations import parse_bibtex_fields
from scripts.generate_publication_citations import publication_link
from scripts.generate_publication_citations import render_csl_citation


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

    def test_normalize_citeproc_html_decodes_and_flattens_output(self):
        citation_html = (
            "Frank, J., &amp; Harrison, P.&nbsp;M.&nbsp;C. (2026). "
            "<em>Journal</em>. <a href=\"https://doi.org/10.1000/example\">"
            "doi:10.1000/example</a>"
        )
        out = normalize_citeproc_html(citation_html)
        self.assertEqual(
            out,
            "Frank, J., & Harrison, P. M. C. (2026). <em>Journal</em>. "
            "https://doi.org/10.1000/example",
        )

    def test_extract_authors_from_apa_citation_uses_text_before_year(self):
        citation = "Frank, J., & Harrison, P. M. C. (2026). Example title."
        self.assertEqual(
            extract_authors_from_apa_citation(citation),
            "Frank, J., & Harrison, P. M. C.",
        )

    def test_render_csl_citation_apa_includes_journal_and_doi(self):
        bibtex = """
        @article{frank2026,
          author = {Frank, Joshua and Harrison, Peter M. C.},
          title = {
            Modeling individual differences in chord pleasantness judgments
          },
          journal = {Psychology of Aesthetics, Creativity, and the Arts},
          volume = {20},
          number = {1},
          pages = {10--21},
          doi = {10.1037/aca0000836},
          year = {2026}
        }
        """
        fields = parse_bibtex_fields(bibtex)
        citation = render_csl_citation(
            bibtex=bibtex,
            csl_style="apa",
            link=publication_link(fields),
            inpress=False,
            year=fields["year"],
        )
        self.assertIn("Frank, J., & Harrison, P. M. C. (2026).", citation)
        self.assertIn(
            "<em>Psychology of Aesthetics, Creativity, and the Arts</em>",
            citation,
        )
        self.assertIn("https://doi.org/10.1037/aca0000836", citation)

    def test_normalize_doi_accepts_url_or_raw(self):
        self.assertEqual(
            normalize_doi("https://doi.org/10.1000/xyz"),
            "https://doi.org/10.1000/xyz",
        )
        self.assertEqual(
            normalize_doi("10.1000/xyz"),
            "https://doi.org/10.1000/xyz",
        )

    def test_publication_link_prefers_registered_doi_over_url(self):
        self.assertEqual(
            publication_link(
                {"doi": "10.1000/xyz", "url": "https://example.com/a"}
            ),
            "https://doi.org/10.1000/xyz",
        )

    def test_publication_link_falls_back_to_url(self):
        self.assertEqual(
            publication_link(
                {"url": "https://www.aes.org/e-lib/browse.cfm?elib=1"}
            ),
            "https://www.aes.org/e-lib/browse.cfm?elib=1",
        )

    def test_normalize_citeproc_html_flattens_url_field_anchor(self):
        citation_html = (
            "Doe, J. (2022). <em>Proceedings</em>. "
            'URL: <a href="https://example.com/x">https://example.com/x</a>'
        )
        out = normalize_citeproc_html(citation_html)
        self.assertEqual(
            out,
            "Doe, J. (2022). <em>Proceedings</em>. https://example.com/x",
        )

    def test_extract_publication_venue_uses_journal_or_booktitle(self):
        self.assertEqual(
            extract_publication_venue({"journal": "Music Perception"}),
            "Music Perception",
        )
        self.assertEqual(
            extract_publication_venue({"booktitle": "Proceedings of ISMIR"}),
            "Proceedings of ISMIR",
        )

    def test_build_front_matter_formats_bibtex_and_marks_generated_fields(
        self,
    ):
        front_matter = {
            "title": "Example",
            "bibtex": (
                "@article{example,\n"
                "  author = {Doe, Jane},\n"
                "  year = {2026}\n"
                "}"
            ),
            "citation_apa": "Doe, J. (2026). Example.",
            "authors": "Doe, J.",
            "journal": "Journal",
            "doi": "https://doi.org/10.1000/example",
        }
        output = build_front_matter_text(front_matter)
        self.assertIn("bibtex: |", output)
        self.assertIn("  @article{example,", output)
        self.assertIn("# generated from bibtex; do not edit manually", output)

    def test_inject_autogen_comments_keeps_single_comment_block(self):
        yaml_text = (
            "title: Example\n"
            "citation_apa: Citation\n"
            "authors: Doe\n"
            "journal: Journal\n"
            "doi: https://doi.org/x\n"
        )
        out = inject_autogen_comments(yaml_text)
        self.assertEqual(
            out.count("# generated from bibtex; do not edit manually"),
            1,
        )


if __name__ == "__main__":
    unittest.main()
