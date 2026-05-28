# Faculty of Music event posting procedure

Use this procedure to post CMS seminars from `content/events/*.md` to the
Faculty of Music website. The agent should fill the form after manual
authentication, then stop before saving or publishing so the organiser can
review.

## Browser workflow

1. Open `https://www.mus.cam.ac.uk/user` in the Cursor browser.
2. The organiser logs in manually with their University account.
3. Open `https://www.mus.cam.ac.uk/node/add/event`.
4. Confirm the page is the authenticated event creation form, not
   `Access denied`.
5. Read the CMS seminar source file from `content/events/`.
6. Before filling the form, check whether the Faculty events list already
   includes this talk. Search the existing events for the event title; if a
   matching entry is present, stop and tell the user instead of creating a
   duplicate.
7. Add a `Text` component under `About`, then fill the Faculty of Music form
   using the mapping below.
8. Do not press `Save`, `Preview`, `Publish`, or any equivalent submit button.
   Leave the browser on the completed form for organiser review.

## Field mapping

- `Title`: use `CMS Seminar: <event title>`. Do not duplicate the prefix if it
  is already present.
- `Subtitle`: use the speaker name followed by affiliations in parentheses,
  separated with semicolons.
- `Location` > `Display name`: use event `location`.
- `Location` > `Room`: leave blank unless the source event gives a room.
- `Location` > `Full address`: use `Faculty of Music, 11 West Road, Cambridge
  CB3 9DP` unless the event source gives a more specific address.
- `Summary`: leave empty. The field has a short character limit and is easy to
  truncate accidentally.
- `Event link`: use `https://cms.mus.cam.ac.uk/events/`.
- `Event image`: click `+ Add`, choose `Image`, then click `Add media`. Browser
  MCP can open the `Add or select media` modal and search existing media, but
  cannot set the local `Choose file` upload control. If the image is not already
  in the media library, the organiser should choose and upload it manually
  during review unless a Playwright workflow is introduced. Set `Aspect ratio`
  to `1:1 Square`.
- `About`: click `+ Add`, choose `Text`, then use the rich-text editor. Begin
  directly with event `abstract`; do not add an `Abstract` heading, because the
  field is already displayed under an `About` heading. Then add a `Biography`
  heading and event `biography`. The Faculty editor offers the biography heading
  as `Heading 2` in the text component.
- `Livestream`: the pilot form did not expose a dedicated livestream field. If
  `livestream_url` is present, include it at the end of the `About` text as
  `Also available on Zoom: <livestream_url>`.
- `Contact name` and `Contact email`: use the organiser details if known.
- `Date`: use the event date.
- Start `Time`: use the event start time.
- End `Date` and `Time`: use event `end_date` when present; otherwise use one
  hour after `date` as a reviewable default.
- `Moderation state`: leave as the default `Draft` for review.

## Review checklist

Before saving or publishing, check:

- The Faculty events list did not already include an entry for the same talk
  before this draft was started.
- The title begins with `CMS Seminar:`.
- The date, start time, and end time are correct.
- The event is assigned to the right CMS seminar category, series, or listing
  area if the form provides one. The pilot form did not show a CMS seminar
  category in the main form.
- The event link points to `https://cms.mus.cam.ac.uk/events/`.
- The venue is specific enough for attendees.
- The abstract and biography have pasted cleanly into the rich-text editor, with
  no redundant `Abstract` heading and a `Biography` heading formatted as
  `Heading 2`.
- The speaker image, if present in the event file, has been uploaded or the
  empty image component has been removed before saving, and the image aspect
  ratio is set to `1:1 Square`.
- Zoom information, if present, is visible in an appropriate field.
- The form is still in draft/review state and has not been saved or published
  by the agent.

## Pilot notes

The unauthenticated `node/add/event` page returns `Access denied`, so manual
browser authentication is required. In the first logged-in pilot, the form was a
Drupal event form with component-based `Event image` and `About` sections. The
agent can add the required `Text` component and fill CKEditor content, but image
media upload/selection remains a manual review step.
