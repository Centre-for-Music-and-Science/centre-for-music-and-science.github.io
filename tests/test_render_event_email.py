"""Tests for event email rendering."""

import html
import unittest

from scripts.render_event_email import EMAIL_RECIPIENTS
from scripts.render_event_email import email_subject
from scripts.render_event_email import render_event_email


class RenderEventEmailTests(unittest.TestCase):
    def test_render_event_email_preserves_abstract_text(self) -> None:
        abstract = (
            'Original abstract with "probe" tones and musical contingent '
            "self-worth. Do not paraphrase this sentence."
        )
        rendered = render_event_email(
            {
                "title": "Example talk",
                "date": "2026-06-16T11:00:00",
                "location": "Centre for Music and Science",
                "speakers": [
                    {
                        "name": "Ron Friedman",
                        "image": "/images/events/ron-friedman.jpg",
                        "affiliations": ["University at Albany"],
                    }
                ],
                "event_type": "CMS seminar",
                "abstract": abstract,
                "biography": "Speaker biography.",
            },
            "https://centre-for-music-and-science.github.io/",
        )

        self.assertIn(abstract, html.unescape(rendered))

    def test_render_event_email_uses_absolute_speaker_image_url(self) -> None:
        rendered = render_event_email(
            {
                "title": "Example talk",
                "date": "2026-06-16T11:00:00",
                "speakers": [
                    {
                        "name": "Ron Friedman",
                        "image": "/images/events/ron-friedman.jpg",
                    }
                ],
                "abstract": "Abstract.",
                "biography": "Biography.",
            },
            "https://centre-for-music-and-science.github.io/",
        )

        self.assertIn(
            'src="https://centre-for-music-and-science.github.io/images/'
            'events/ron-friedman.jpg"',
            rendered,
        )

    def test_render_event_email_includes_copyable_setup_fields(self) -> None:
        rendered = render_event_email(
            {
                "title": "Example talk",
                "date": "2026-06-16T11:00:00",
                "speakers": [{"name": "Ron Friedman"}],
                "event_type": "CMS seminar",
                "abstract": "Abstract.",
                "biography": "Biography.",
            },
            "https://centre-for-music-and-science.github.io/",
        )
        plain_rendered = html.unescape(rendered)

        self.assertIn("Email setup", rendered)
        self.assertIn(EMAIL_RECIPIENTS, plain_rendered)
        self.assertIn(
            "CMS seminar tomorrow: Ron Friedman, Example talk",
            plain_rendered,
        )

    def test_email_subject_omits_empty_title(self) -> None:
        self.assertEqual(
            email_subject("CMS seminar", "Ron Friedman", ""),
            "CMS seminar tomorrow: Ron Friedman",
        )

    def test_talk_title_is_main_heading_without_detail_row(self) -> None:
        rendered = render_event_email(
            {
                "title": "Example talk",
                "date": "2026-06-16T11:00:00",
                "speakers": [{"name": "Ron Friedman"}],
                "event_type": "CMS seminar",
                "abstract": "Abstract.",
                "biography": "Biography.",
            },
            "https://centre-for-music-and-science.github.io/",
        )

        self.assertIn(
            '<h1 style="font-size:22px;margin:24px 0 8px;">'
            "Example talk</h1>",
            rendered,
        )
        self.assertNotIn("<strong>Title:</strong>", rendered)

    def test_zoom_link_is_folded_into_location_row(self) -> None:
        rendered = render_event_email(
            {
                "title": "Example talk",
                "date": "2026-06-16T11:00:00",
                "location": "Centre for Music and Science, Faculty of Music",
                "livestream_url": "https://zoom.us/j/example",
                "speakers": [{"name": "Ron Friedman"}],
                "event_type": "CMS seminar",
                "abstract": "Abstract.",
                "biography": "Biography.",
            },
            "https://centre-for-music-and-science.github.io/",
        )

        self.assertIn(
            "<strong>Location:</strong> Centre for Music and Science, "
            "Faculty of Music</p>\n<p><strong>Zoom:</strong>",
            rendered,
        )
        self.assertNotIn("Online access", rendered)

    def test_render_event_email_includes_copy_buttons(self) -> None:
        rendered = render_event_email(
            {
                "title": "Example talk",
                "date": "2026-06-16T11:00:00",
                "speakers": [{"name": "Ron Friedman"}],
                "event_type": "CMS seminar",
                "abstract": "Abstract.",
                "biography": "Biography.",
            },
            "https://centre-for-music-and-science.github.io/",
        )

        self.assertIn("Copy recipients", rendered)
        self.assertIn("Copy subject", rendered)
        self.assertIn("Copy body", rendered)
        self.assertIn('id="email-body"', rendered)
        self.assertIn("copyBody('email-body', this)", rendered)


if __name__ == "__main__":
    unittest.main()
