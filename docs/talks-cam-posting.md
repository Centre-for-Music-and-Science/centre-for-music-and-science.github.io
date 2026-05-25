# Talks.cam posting procedure

Use this procedure to post CMS seminars from `content/events/*.md` to
Talks.cam with the Cursor browser MCP. The agent should fill the form but stop
before saving so the organiser can review and submit manually.

## Browser workflow

1. Open `https://talks.cam.ac.uk/talk/new/111130/` in the Cursor browser.
2. The organiser logs in manually.
3. Confirm the page title is `New Talk - Talks.cam` and the breadcrumb includes
   `CMS seminar series in the Faculty of Music`.
4. Read the CMS seminar source file from `content/events/`.
5. Fill the Talks.cam form using the mapping below.
6. Do not press `Save`. Leave the browser on the completed form for organiser
   review.

## Field mapping

- `Title`: use event `title`.
- `Abstract`: begin with an `Abstract` heading formatted as `Heading 1`, then
  use event `abstract`, followed by a `Biography` heading also formatted as
  `Heading 1` and event `biography`.
- `Speaker's e-mail`: leave blank unless the event record or organiser provides
  a speaker email.
- `Send e-mail invitation to speaker`: leave unchecked unless explicitly asked.
- `Speaker's name and affiliation`: use the speaker name followed by
  affiliations in parentheses, separated with semicolons.
- `Speaker's website address`: leave blank unless the event record provides a
  speaker website.
- `Picture of speaker or other image`: use the event speaker image when
  present. Browser MCP cannot currently set Talks.cam file inputs reliably, so
  the organiser should upload this manually during review.
- `Organiser's e-mail`: keep the Talks.cam default unless explicitly changed.
- `Special message`: use `Also available on Zoom: <livestream_url>` when
  `livestream_url` is present; otherwise leave blank.
- `Venue`: use event `location`.
- `Start time`: use event `date`.
- `End time`: use event `end_date` when present; otherwise use one hour after
  `date` as a reviewable default.
- `Ex-directory or Publicity?`: make sure this is unchecked for public seminar
  listings.

## Review checklist

Before saving, check:

- The talk belongs to `CMS seminar series in the Faculty of Music`.
- The title has not been truncated.
- The date, start time, and end time are correct.
- The venue is specific enough for attendees.
- The abstract and biography have pasted cleanly into the rich-text editor, with
  `Abstract` and `Biography` formatted as `Heading 1`.
- The speaker image, if present in the event file, has been uploaded manually.
- Zoom information, if present, is in the special message or another suitable
  visible field.
- `Ex-directory or Publicity?` is unchecked unless the talk should be hidden.
