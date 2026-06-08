---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: hermes nws-go-lightly-dev (gpt-5.5)
---

# macOS PostgreSQL Setup

This guide mirrors the Ubuntu passwordless-local pattern for a developer Mac. Formy02 should not put a database password in `.env`; the app connects as the local PostgreSQL role over loopback.

## Install and start PostgreSQL

```bash
brew install postgresql@16
brew services start postgresql@16
```

## Create role and database

```bash
createuser formy02
createdb formy02 -O formy02
psql formy02 -c "GRANT ALL ON SCHEMA public TO formy02;"
```

If `createuser formy02` reports that the role already exists, continue with `createdb`/grants or inspect the role with:

```bash
psql postgres -c "\du formy02"
```

## Configure `.env`

Do not include `DB_PASSWORD`.

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=formy02
DB_USER=formy02
DB_SCHEMA=
```

## Verify the connection

```bash
psql -h 127.0.0.1 -U formy02 -d formy02 -c "SELECT current_user, current_database();"
```

After the app starts and creates tables:

```bash
psql -h 127.0.0.1 -U formy02 -d formy02 -c "\dt"
```

## Operator restore from a `.dump` file

```bash
pg_restore --clean --if-exists --no-owner --no-privileges \
  --format=custom --host=127.0.0.1 --port=5432 --username=formy02 \
  --dbname=formy02 backup_20260608_050000.dump
```
