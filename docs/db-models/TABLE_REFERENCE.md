---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Table Reference

## User (`users`)

| Column | Python Type | SQL Type | Constraints |
| --- | --- | --- | --- |
| `id` | `Optional[int]` | integer | PK |
| `username` | `str` | text/varchar | unique, indexed, not null |
| `password` | `str` | text/varchar | not null, bcrypt hash |
| `email` | `str` | text/varchar | unique, indexed, not null |
| `is_admin` | `bool` | boolean | default false |
| `email_verified` | `bool` | boolean | default false |
| `created_at` | `datetime` | timestamp | default utcnow |
| `updated_at` | `datetime` | timestamp | default utcnow |

Relationships: referenced by signed session cookie user IDs; no SQLModel relationship attributes are declared.

## SurveyedPerson (`surveyed_person`)

| Column | Python Type | SQL Type | Constraints |
| --- | --- | --- | --- |
| `id` | `Optional[int]` | integer | PK |
| `name` | `Optional[str]` | text/varchar | nullable |
| `email` | `Optional[str]` | text/varchar | nullable |
| `phone` | `Optional[str]` | text/varchar | nullable |
| `created_at` | `datetime` | timestamp | default utcnow |
| `updated_at` | `datetime` | timestamp | default utcnow |

Relationships: linked to questions and responses through `contract_surveyed_person_questions_responses.surveyed_person_id`.

## Question (`questions`)

| Column | Python Type | SQL Type | Constraints |
| --- | --- | --- | --- |
| `id` | `Optional[int]` | integer | PK |
| `question` | `str` | text/varchar | not null |
| `is_active` | `bool` | boolean | default true |
| `type` | `str` | text/varchar | default `text` |
| `allows_for_audio` | `bool` | boolean | default true |
| `options` | `Optional[List[str]]` | JSONB | nullable |
| `created_at` | `datetime` | timestamp | default utcnow |
| `updated_at` | `datetime` | timestamp | default utcnow |

`Question.options` is mapped directly to PostgreSQL JSONB. SQLAlchemy handles serialization, so application code assigns and reads Python lists without `json.dumps` or `json.loads`.

Relationships: linked to responses through `contract_surveyed_person_questions_responses.question_id`.

## Response (`responses`)

| Column | Python Type | SQL Type | Constraints |
| --- | --- | --- | --- |
| `id` | `Optional[int]` | integer | PK |
| `response` | `Optional[str]` | text/varchar | nullable |
| `audio_file_path_and_filename` | `Optional[str]` | text/varchar | nullable |
| `summary` | `Optional[str]` | text/varchar | nullable |
| `created_at` | `datetime` | timestamp | default utcnow |
| `updated_at` | `datetime` | timestamp | default utcnow |

Relationships: linked to surveyed people and questions through `contract_surveyed_person_questions_responses.response_id`.

## ContractSurveyedPersonQuestionResponse (`contract_surveyed_person_questions_responses`)

| Column | Python Type | SQL Type | Constraints |
| --- | --- | --- | --- |
| `id` | `Optional[int]` | integer | PK |
| `surveyed_person_id` | `int` | integer | FK `surveyed_person.id`, indexed |
| `question_id` | `int` | integer | FK `questions.id`, indexed |
| `response_id` | `int` | integer | FK `responses.id`, indexed |
| `created_at` | `datetime` | timestamp | default utcnow |
| `updated_at` | `datetime` | timestamp | default utcnow |

Relationships: junction table that connects one surveyed person, one question, and one response.
