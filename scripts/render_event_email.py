#!/usr/bin/env python3
"""Render a copyable rich-text email preview for an event."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - import guard for CLI usage.
    raise ImportError(
        "PyYAML is required. Install it with: pip install pyyaml"
    ) from exc


FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
DEFAULT_BASE_URL = "https://centre-for-music-and-science.github.io/"
EMAIL_RECIPIENTS = (
    "mus-cms-news@lists.cam.ac.uk <mus-cms-news@lists.cam.ac.uk>; "
    "visitors@mus.cam.ac.uk <visitors@mus.cam.ac.uk>; "
    "grads@mus.cam.ac.uk <grads@mus.cam.ac.uk>; "
    "utos@mus.cam.ac.uk <utos@mus.cam.ac.uk>; "
    "ecrs@mus.cam.ac.uk <ecrs@mus.cam.ac.uk>; "
    "Music II Mailing List <part2@mus.cam.ac.uk>; "
    "Music IB Mailing List <part1b@mus.cam.ac.uk>; "
    "Music IA Mailing List <part1a@mus.cam.ac.uk>"
)


def split_front_matter(content: str) -> tuple[dict[str, Any], str]:
    """Split a markdown document into YAML front matter and body."""
    match = FRONT_MATTER_RE.match(content)
    if not match:
        raise ValueError("File does not contain YAML front matter.")
    front_matter = yaml.safe_load(match.group(1)) or {}
    body = content[match.end():]
    return front_matter, body


def load_event(path: Path) -> dict[str, Any]:
    """Load event front matter from a content markdown file."""
    front_matter, _ = split_front_matter(path.read_text(encoding="utf-8"))
    return front_matter


def read_base_url(repo_root: Path) -> str:
    """Read ``baseURL`` from ``hugo.toml`` when available."""
    config_path = repo_root / "hugo.toml"
    if not config_path.exists():
        return DEFAULT_BASE_URL
    match = re.search(
        r"""(?m)^baseURL\s*=\s*['"]([^'"]+)['"]""",
        config_path.read_text(encoding="utf-8"),
    )
    return match.group(1) if match else DEFAULT_BASE_URL


def absolute_url(base_url: str, maybe_path: str) -> str:
    """Return an absolute URL for a site-relative path or existing URL."""
    if not maybe_path:
        return ""
    if maybe_path.startswith(("http://", "https://")):
        return maybe_path
    return f"{base_url.rstrip('/')}/{maybe_path.lstrip('/')}"


def format_date(value: Any) -> str:
    """Format an event date in a readable email style."""
    if isinstance(value, dt.datetime):
        event_dt = value
    elif isinstance(value, dt.date):
        event_dt = dt.datetime.combine(value, dt.time())
    else:
        event_dt = dt.datetime.fromisoformat(str(value))
    return event_dt.strftime("%A %-d %B %Y")


def format_time_range(start_value: Any, end_value: Any | None = None) -> str:
    """Format the event start time, adding an end time when supplied."""
    if isinstance(start_value, dt.datetime):
        start = start_value
    else:
        start = dt.datetime.fromisoformat(str(start_value))
    if not end_value:
        return start.strftime("%H:%M")
    if isinstance(end_value, dt.datetime):
        end = end_value
    else:
        end = dt.datetime.fromisoformat(str(end_value))
    if start.date() == end.date():
        return f"{start:%H:%M}-{end:%H:%M}"
    return f"{start:%H:%M} to {end:%A %-d %B %Y, %H:%M}"


def speaker_summary(speakers: list[dict[str, Any]]) -> str:
    """Return a compact speaker line with affiliations."""
    if not speakers:
        return ""
    speaker = speakers[0]
    name = speaker.get("name", "")
    affiliations = speaker.get("affiliations") or []
    if affiliations:
        return f"{name}, {', '.join(str(item) for item in affiliations)}"
    return str(name)


def email_subject(event_type: str, speaker_name: str, title: str) -> str:
    """Return a descriptive subject line for the email announcement."""
    if title:
        return f"{event_type} tomorrow: {speaker_name}, {title}"
    return f"{event_type} tomorrow: {speaker_name}"


def render_text_block(text: str) -> str:
    """Render source text as escaped HTML paragraphs."""
    paragraphs = [
        paragraph.strip()
        for paragraph in text.strip().split("\n\n")
        if paragraph.strip()
    ]
    return "\n".join(
        f"<p>{html.escape(paragraph).replace(chr(10), '<br>')}</p>"
        for paragraph in paragraphs
    )


def render_detail_row(label: str, value: str) -> str:
    """Render one escaped event detail row."""
    return (
        f"<p><strong>{html.escape(label)}:</strong> "
        f"{html.escape(value)}</p>"
    )


def render_location_row(location: str, livestream_url: str) -> str:
    """Render location details, including online access when available."""
    if not location and not livestream_url:
        return ""

    rows = []
    if location:
        rows.append(render_detail_row("Location", location))
    if livestream_url:
        escaped_url = html.escape(livestream_url)
        rows.append(
            f'<p><strong>Zoom:</strong> <a href="{escaped_url}">'
            f"{escaped_url}</a></p>"
        )
    return "\n".join(rows)


def copy_button(label: str, action: str) -> str:
    """Render a small clipboard button for the preview page."""
    button_style = (
        "font:inherit;font-size:13px;padding:5px 10px;"
        "border:1px solid #9aa7b2;border-radius:4px;"
        "background:#fff;cursor:pointer;"
    )
    return (
        f'<button type="button" style="{button_style}" {action}>'
        f"{label}</button>"
    )


def render_event_email(event: dict[str, Any], base_url: str) -> str:
    """Render event front matter as a copyable HTML email preview."""
    speakers = event.get("speakers") or []
    primary_speaker = speakers[0] if speakers else {}
    event_type = str(event.get("event_type") or "Seminar")
    speaker_name = str(primary_speaker.get("name") or "our speaker")
    title = str(event.get("title") or "")
    date_value = event.get("date")
    image_url = absolute_url(base_url, str(primary_speaker.get("image") or ""))
    livestream_url = str(event.get("livestream_url") or "")

    detail_rows = [
        ("Date", format_date(date_value)),
        ("Time", format_time_range(date_value, event.get("end_date"))),
        ("Speaker", speaker_summary(speakers)),
    ]
    details = [
        render_detail_row(label, value)
        for label, value in detail_rows
        if value
    ]
    details.insert(
        2,
        render_location_row(str(event.get("location") or ""), livestream_url),
    )
    details_html = "\n".join(detail for detail in details if detail)

    image_html = ""
    if image_url:
        image_html = (
            f'<img src="{html.escape(image_url)}" '
            f'alt="{html.escape(speaker_name)}" '
            'width="160" style="width:160px;max-width:35%;height:auto;'
            'border-radius:8px;'
            'float:right;margin:0 0 16px 24px;">'
        )

    abstract = render_text_block(str(event.get("abstract") or ""))
    biography = render_text_block(str(event.get("biography") or ""))
    body_style = (
        "font-family:Aptos, Calibri, Arial, sans-serif;font-size:11pt;"
        "line-height:1.5;"
        "color:#222;max-width:720px;"
    )
    intro = (
        "I'm very pleased to share details of our upcoming "
        f"{html.escape(event_type)}, taking place tomorrow with "
        f"{html.escape(speaker_name)}."
    )
    heading = html.escape(title or f"{event_type}: {speaker_name}")
    subject = email_subject(event_type, speaker_name, title)
    setup_style = (
        "background:#f4f6f8;border:1px solid #d9e0e7;"
        "border-radius:8px;padding:16px;margin:0 0 24px;"
    )
    copy_style = "word-break:break-word;margin:4px 0 8px;"
    copy_buttons = {
        "recipients": copy_button(
            "Copy recipients",
            'onclick="copyTextFrom(\'email-recipients\', this)"',
        ),
        "subject": copy_button(
            "Copy subject",
            'onclick="copyTextFrom(\'email-subject\', this)"',
        ),
        "body": copy_button(
            "Copy body",
            'onclick="copyBody(\'email-body\', this)"',
        ),
    }

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html.escape(subject)}</title>
</head>
<body style="{body_style}">
  <div style="{setup_style}">
    <h2 style="font-size:16px;margin:0 0 12px;">Email setup</h2>
    <p style="{copy_style}">
      <strong>To:</strong>
      <span id="email-recipients">{html.escape(EMAIL_RECIPIENTS)}</span>
    </p>
    <p style="margin:0 0 12px;">{copy_buttons["recipients"]}</p>
    <p style="{copy_style}">
      <strong>Subject:</strong>
      <span id="email-subject">{html.escape(subject)}</span>
    </p>
    <p style="margin:0 0 12px;">{copy_buttons["subject"]}</p>
    <p style="margin:0;">{copy_buttons["body"]}</p>
  </div>

  <div id="email-body" style="{body_style}">
    <p>{intro}</p>

    {image_html}

    <h1 style="font-size:22px;margin:24px 0 8px;">{heading}</h1>
    <div style="margin:0 0 20px;">
      {details_html}
    </div>

    <h2 style="font-size:18px;margin:24px 0 8px;">Abstract</h2>
    {abstract}

    <h2 style="font-size:18px;margin:24px 0 8px;">Biography</h2>
    {biography}
  </div>

  <script>
    async function copyTextFrom(id, button) {{
      const text = document.getElementById(id).textContent.trim();
      await navigator.clipboard.writeText(text);
      showCopied(button);
    }}

    async function copyBody(id, button) {{
      const element = document.getElementById(id);
      const html = element.outerHTML;
      const text = element.innerText.trim();
      if (window.ClipboardItem) {{
        await navigator.clipboard.write([
          new ClipboardItem({{
            "text/html": new Blob([html], {{type: "text/html"}}),
            "text/plain": new Blob([text], {{type: "text/plain"}}),
          }}),
        ]);
      }} else {{
        await navigator.clipboard.writeText(text);
      }}
      showCopied(button);
    }}

    function showCopied(button) {{
      const original = button.textContent;
      button.textContent = "Copied";
      setTimeout(() => {{
        button.textContent = original;
      }}, 1200);
    }}
  </script>
</body>
</html>
"""


def default_output_path(event_path: Path) -> Path:
    """Return the default generated preview path for an event."""
    return Path("public") / "email-previews" / f"{event_path.stem}.html"


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Render a rich-text email preview from an event markdown file."
        )
    )
    parser.add_argument(
        "event",
        type=Path,
        help="Path to an event markdown file.",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Public site base URL. Defaults to baseURL in hugo.toml.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "HTML output path. Defaults to "
            "public/email-previews/<event>.html."
        ),
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print HTML to stdout instead of writing a preview file.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Render the requested event email preview."""
    args = parse_args(argv or sys.argv[1:])
    repo_root = Path(__file__).resolve().parents[1]
    base_url = args.base_url or read_base_url(repo_root)
    event = load_event(args.event)
    rendered = render_event_email(event, base_url)

    if args.stdout:
        print(rendered, end="")
        return 0

    output_path = args.output or default_output_path(args.event)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(f"Wrote {output_path}")
    print(
        "Open it in a browser and copy the rendered page into your email "
        "composer."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
