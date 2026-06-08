---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Questionnaire Endpoints

## GET /

Description: Renders the public questionnaire with active questions ordered by ID.

Flags: no auth required; no side effects.

Parameters: none.

Sample Request: `GET /?theme=dark`

Sample Response: HTML questionnaire page.

Error Responses: standard 500 error on unhandled server failure.

## POST /submit

Description: Creates a `SurveyedPerson`, saves non-empty answers, stores uploaded audio files, and links responses to questions.

Flags: no auth required; writes database rows and audio files.

Parameters: multipart form fields `name`, `email`, `phone`, `question_{id}`, and optional file `audio_{id}`.

Sample Request: `POST /submit` with multipart form data.

Sample Response: `303 See Other` redirect to `/thank-you`.

Error Responses: standard 422 validation error or 500 internal error.

## GET /thank-you

Description: Renders the submission confirmation page.

Flags: no auth required; no side effects.

Parameters: none.

Sample Request: `GET /thank-you`

Sample Response: HTML thank-you page.

Error Responses: standard 500 error on unhandled server failure.
