---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: hermes nws-go-lightly-dev (gpt-5.5)
---

# Table Reference

Formy02 uses SQLModel metadata and creates these tables at application startup via `SQLModel.metadata.create_all(engine)`. PostgreSQL is the only supported database backend.

## User (`users`)

| Column | Python Type | SQL Type | Constraints / Notes |
| --- | --- | --- | --- |
| `id` | `Optional[int]` | integer | Primary key. |
| `username` | `str` | text/varchar | Unique, indexed, not null. |
| `password` | `str` | text/varchar | Bcrypt hash, not null. |
| `email` | `str` | text/varchar | Unique, indexed, not null. |
| `is_admin` | `bool` | boolean | Default `false`. |
| `email_verified` | `bool` | boolean | Default `false`. |
| `created_at` | `datetime` | timestamp | Defaults to UTC creation time. |
| `updated_at` | `datetime` | timestamp | Defaults to UTC creation time; application updates when rows change. |

Relationships: no SQLModel relationship attributes are declared. FastAPI auth stores user IDs in signed session cookies.

## SurveyedPerson (`surveyed_person`)

| Column | Python Type | SQL Type | Constraints / Notes |
| --- | --- | --- | --- |
| `id` | `Optional[int]` | integer | Primary key. |
| `name` | `Optional[str]` | text/varchar | Nullable. |
| `email` | `Optional[str]` | text/varchar | Nullable. |
| `phone` | `Optional[str]` | text/varchar | Nullable. |
| `created_at` | `datetime` | timestamp | Defaults to UTC creation time. |
| `updated_at` | `datetime` | timestamp | Defaults to UTC creation time; application updates when rows change. |

Relationships: linked to questions and responses through `contract_surveyed_person_questions_responses.surveyed_person_id`.

## Question (`questions`)

| Column | Python Type | SQL Type | Constraints / Notes |
| --- | --- | --- | --- |
| `id` | `Optional[int]` | integer | Primary key. |
| `question` | `str` | text/varchar | Question prompt, not null. |
| `is_active` | `bool` | boolean | Default `true`; inactive questions are hidden from the public form. |
| `type` | `str` | text/varchar | Default `text`; intended values include `text`, `yes/no`, and `multiple_choice`. |
| `allows_for_audio` | `bool` | boolean | Default `true`. |
| `options` | `Optional[List[str]]` | JSONB | Nullable; stores multiple-choice options as a JSON array. |
| `created_at` | `datetime` | timestamp | Defaults to UTC creation time. |
| `updated_at` | `datetime` | timestamp | Defaults to UTC creation time; application updates when rows change. |

`Question.options` is mapped directly to PostgreSQL JSONB. Application code reads and writes normal Python lists.

Relationships: linked to responses through `contract_surveyed_person_questions_responses.question_id`.

## Response (`responses`)

| Column | Python Type | SQL Type | Constraints / Notes |
| --- | --- | --- | --- |
| `id` | `Optional[int]` | integer | Primary key. |
| `response` | `Optional[str]` | text/varchar | Nullable text answer. |
| `audio_file_path_and_filename` | `Optional[str]` | text/varchar | Nullable path to an uploaded audio file under `AUDIO_FILES_PATH`. |
| `summary` | `Optional[str]` | text/varchar | Nullable summary text. |
| `created_at` | `datetime` | timestamp | Defaults to UTC creation time. |
| `updated_at` | `datetime` | timestamp | Defaults to UTC creation time; application updates when rows change. |

Relationships: linked to surveyed people and questions through `contract_surveyed_person_questions_responses.response_id`.

## SurveyedPersonQuestionResponse (`contract_surveyed_person_questions_responses`)

| Column | Python Type | SQL Type | Constraints / Notes |
| --- | --- | --- | --- |
| `id` | `Optional[int]` | integer | Primary key. |
| `surveyed_person_id` | `int` | integer | Foreign key to `surveyed_person.id`, indexed, not null. |
| `question_id` | `int` | integer | Foreign key to `questions.id`, indexed, not null. |
| `response_id` | `int` | integer | Foreign key to `responses.id`, indexed, not null. |
| `created_at` | `datetime` | timestamp | Defaults to UTC creation time. |
| `updated_at` | `datetime` | timestamp | Defaults to UTC creation time; application updates when rows change. |

Relationships: junction table connecting one surveyed person, one question, and one response.
