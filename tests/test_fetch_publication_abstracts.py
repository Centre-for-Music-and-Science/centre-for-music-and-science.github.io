"""Tests for CrossRef / HTML abstract helpers (no network)."""

import unittest

from scripts.fetch_publication_abstracts import abstract_from_openalex_inverted_index
from scripts.fetch_publication_abstracts import arxiv_landing_url
from scripts.fetch_publication_abstracts import doi_from_params
from scripts.fetch_publication_abstracts import merge_abstract
from scripts.fetch_publication_abstracts import normalize_crossref_abstract


class FetchAbstractHelpersTests(unittest.TestCase):
    def test_doi_from_params_extracts_from_url(self) -> None:
        self.assertEqual(
            doi_from_params("https://doi.org/10.5334/tismir.230"),
            "10.5334/tismir.230",
        )

    def test_doi_from_params_returns_none_for_non_doi_url(self) -> None:
        self.assertIsNone(
            doi_from_params("https://www.aes.org/e-lib/browse.cfm?elib=21924"),
        )

    def test_arxiv_landing_url_from_doi_form(self) -> None:
        self.assertEqual(
            arxiv_landing_url("https://doi.org/10.48550/arXiv.2502.16694"),
            "https://arxiv.org/abs/2502.16694",
        )

    def test_normalize_crossref_strips_jats(self) -> None:
        raw = (
            "<jats:title>Abstract</jats:title>"
            "<jats:p>Hello world. Second sentence.</jats:p>"
        )
        self.assertEqual(
            normalize_crossref_abstract(raw),
            "Hello world. Second sentence.",
        )

    def test_merge_abstract_inserts_after_doi(self) -> None:
        fm = {"title": "T", "doi": "https://doi.org/10.1/x", "bibtex": "@"}
        out = merge_abstract(fm, "Abstract text.")
        keys = list(out.keys())
        self.assertEqual(
            keys,
            ["title", "doi", "abstract", "bibtex"],
        )

    def test_openalex_inverted_index_reconstruction(self) -> None:
        inv = {"Hello": [0], "world.": [1]}
        self.assertEqual(
            abstract_from_openalex_inverted_index(inv),
            "Hello world.",
        )


if __name__ == "__main__":
    unittest.main()
