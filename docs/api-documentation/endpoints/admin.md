---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Admin Endpoints

All endpoints require an authenticated admin session.

## GET /admin

Description: Renders dashboard with backup list. Parameters: none. Sample Response: HTML with `backups`.

## GET /admin/questions

Description: Renders question management table and create form. Parameters: none. Sample Response: HTML with `questions`.

## POST /admin/questions

Description: Creates a question.

Parameters: form fields `question`, `type`, `is_active`, `allows_for_audio`, optional `options`.

Sample Response: `303 See Other` redirect to `/admin/questions`.

Error Responses: 401, 403, 422, or 500 standard errors.

## PUT /admin/questions/{id}

Description: Updates question fields from JSON.

Parameters: path `id`; JSON fields `question`, `type`, `is_active`, `allows_for_audio`, `options`.

Sample Response:

```json
{"ok":true,"id":1}
```

Error Responses: 404 `Question not found.`

## DELETE /admin/questions/{id}

Description: Deletes a question.

Sample Response:

```json
{"ok":true}
```

Error Responses: 404 `Question not found.`

## GET /admin/responses

Description: Renders surveyed person response summary table. Sample Response: HTML with `people` and `summaries`.

## GET /admin/responses/{person_id}/detail

Description: Returns a surveyed person's response details for the modal.

Sample Response:

```json
{"person":{"id":1,"name":"Ada","email":"ada@example.com","phone":null},"updated_at":"2026-06-08T05:00:00","responses":[]}
```

Error Responses: 404 `Surveyed person not found.`

## DELETE /admin/responses/{person_id}

Description: Deletes a surveyed person, related junction rows, responses, and associated audio files.

Sample Response:

```json
{"ok":true}
```

Error Responses: 404 `Surveyed person not found.`

## POST /admin/db/backup

Description: Runs `pg_dump` and creates a `.dump` backup.

Sample Response:

```json
{"ok":true,"filename":"backup_20260608_050000.dump"}
```

Error Responses: 500 with backup failure detail.

## POST /admin/db/restore

Description: Restores database from an uploaded `.dump` using the restore-specific auth boundary.

Parameters: multipart file `backup_file`.

Sample Response:

```json
{"ok":true}
```

Error Responses: 400 when extension is not `.dump`; 500 with restore failure detail.

## GET /admin/db/backups/{filename}

Description: Downloads a backup after path traversal validation.

Sample Response: binary response with `Content-Type: application/octet-stream`.

Error Responses: 404 for invalid or missing backup path.

## DELETE /admin/db/backups/{filename}

Description: Deletes a backup after path traversal validation.

Sample Response:

```json
{"ok":true}
```

Error Responses: 404 for invalid or missing backup path.

## GET /admin/audio/{file_path}

Description: Serves an audio file under `AUDIO_FILES_PATH` with a dynamic audio MIME type.

Sample Response: binary audio response.

Error Responses: 403 for path traversal; 404 when file does not exist.
