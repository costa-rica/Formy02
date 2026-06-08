# Formy02

Formy02 is a FastAPI/Jinja questionnaire app based on the original Formy backend, restyled with the GoLightly04 visual system and moved from SQLite to PostgreSQL. It collects optional public questionnaire responses, optional audio recordings, and provides admin pages for questions, responses, and database backup/restore.

## Prerequisites

- Python 3.13
- PostgreSQL with a Formy02 database and user
- `pg_dump` and `pg_restore` available in `PATH`
- Node.js and npm for the Tailwind CLI path used here

## Setup

1. Clone the repo.
2. Create and activate the venv: `python -m venv venv && source venv/bin/activate`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Install Tailwind tooling: `npm install`.
5. Copy `.env.example` to `.env` and fill in required values.
6. Build CSS: `npm run build:css`.
7. Run development server: `uvicorn src.app.main:app --reload`.

Production can run with `RUN_ENVIRONMENT=production uvicorn src.app.main:app --host 0.0.0.0 --port 8000`. Configure `PATH_TO_LOGS` before production startup.

The checked-in `src/app/static/app.css` is present for convenience, but regenerate it with `npm run build:css` after changing templates or `src/styles/tailwind.css`.

## First Admin

SMTP must be configured before first admin registration because email verification is required and there is no startup seeding workaround.

1. Add the admin email address to `EMAIL_ADMIN_USER`.
2. Register at `/register` with that whitelisted email.
3. Click the verification link sent by email.
4. Log in at `/login`.

## Environment Variables

| Key | Purpose |
| --- | --- |
| `NAME_APP` | Application name and log filename prefix. |
| `RUN_ENVIRONMENT` | `development`, `testing`, or `production`. |
| `SECRET_KEY` | JWT and signed session cookie secret. |
| `URL_BASE_WEBSITE` | Public base URL for email links. |
| `EMAIL_ADMIN_USER` | Comma-separated admin registration whitelist. |
| `PATH_PROJECT_RESOURCES` | App-managed resources such as database backups. |
| `AUDIO_FILES_PATH` | Root directory for uploaded audio files. |
| `DB_HOST` | PostgreSQL host. |
| `DB_PORT` | PostgreSQL port. |
| `DB_NAME` | PostgreSQL database name. |
| `DB_USER` | PostgreSQL user. |
| `DB_PASSWORD` | PostgreSQL password. |
| `DB_SCHEMA` | Optional PostgreSQL schema. |
| `GMAIL_SMTP_USER` | SMTP user for verification/reset email. |
| `GMAIL_SMTP_APP_PASSWORD` | SMTP app password. |
| `GMAIL_SMTP_HOST` | SMTP host. |
| `GMAIL_SMTP_PORT` | SMTP port. |
| `PATH_TO_LOGS` | Log directory for testing/production. |
| `LOG_MAX_SIZE_IN_MB` | Size threshold for log rotation. |
| `LOG_MAX_FILES` | Retained log file count. |

## Backup And Restore

Admins can create custom-format PostgreSQL `.dump` backups from `/admin`. Restore uploads require `.dump` files and run `pg_restore` with a bounded timeout.
