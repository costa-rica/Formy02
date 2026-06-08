---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Formy02 Plan V05 Assessment

## 1. The audio preservation plan can carry forward broken recording and playback details

V05 says backend route signatures and audio behavior are preserved, and §8 says
to preserve the per-question MediaRecorder widget and admin audio playback. That
is directionally correct, but the Formy reference has concrete audio defects that
must not be copied unchanged if Formy02 is to satisfy the PRD's acceptance
criterion: "Audio record → playback → upload → admin playback works end to end."

Evidence:

- `Formy/src/app/templates/questionnaire.html` renders the record button with
  `class="... record-btn d-none"` and the stop button with
  `class="... stop-btn d-none"`. The local script only hides the record button
  after it is clicked and shows it again after stop; no initialization code ever
  removes `d-none` from the record button. As written, users cannot start an
  audio recording.
- `Formy/src/app/routes/admin.py` mounts the audio file route on
  `APIRouter(prefix="/admin")` as `@router.get("/audio/{file_path:path}")`, so
  the actual URL is `/admin/audio/{file_path}`. However,
  `Formy/src/app/templates/admin/responses.html` builds modal audio sources as
  `/audio/${encodeURIComponent(item.audio_path)}`. Preserving that template URL
  will not hit the admin route.
- `Formy/src/app/utilities/audio.py` always saves uploaded audio with a `.mp3`
  extension, while the browser recorder creates a `File` named `audio_<id>.webm`
  with MIME type `audio/webm`. The admin route then serves every audio file as
  `audio/mpeg`. That extension/MIME mismatch is another risk to admin playback.

Rewrite guidance: add an explicit audio subsection to V05 §8 that treats these
as required fixes while preserving the overall Formy mechanism:

- Questionnaire recorder: render the Record control visible/enabled for
  questions where `allows_for_audio` is true and `MediaRecorder` is available;
  keep Stop and Playback hidden until their normal states. Preserve the hidden
  file input naming contract `audio_<question_id>` and the DataTransfer upload
  mechanism.
- Audio file saving: preserve the dated subdirectory and zero-padded filename
  convention, but derive the extension from the uploaded filename or content
  type (`audio/webm` should store as `.webm`; fallback to a safe known audio
  extension only when the upload has no usable extension). Store the full saved
  path in `Response.audio_file_path_and_filename` as before.
- Admin playback route/template: choose one canonical protected URL and make the
  route and template agree. The smallest change is to keep the admin router
  route and generate sources as `/admin/audio/${encodeURIComponent(item.audio_path)}`;
  alternatively expose a top-level `/audio/{file_path:path}` route, but it must
  still require `require_admin`. Serve a media type that matches the stored file
  extension/content rather than hard-coding `audio/mpeg` for all recordings.

Without this clarification, an implementer following "preserve audio" literally
can reproduce the reference app's broken controls and route mismatch, leaving a
core PRD feature nonfunctional.
