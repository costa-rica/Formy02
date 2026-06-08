---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# macOS PostgreSQL Setup

Install and start PostgreSQL:

```bash
brew install postgresql@16
brew services start postgresql@16
```

Create user and database:

```bash
createuser formy02
createdb formy02 -O formy02
psql postgres -c "ALTER USER formy02 WITH PASSWORD 'change-me';"
```

Grant schema privileges:

```bash
psql formy02 -c "GRANT ALL ON SCHEMA public TO formy02;"
```

Set `.env` database keys:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=formy02
DB_USER=formy02
DB_PASSWORD=change-me
```

Operator restore from a `.dump` file:

```bash
PGPASSWORD=change-me pg_restore --clean --if-exists --no-owner --no-privileges \
  --format=custom --host=localhost --port=5432 --username=formy02 \
  --dbname=formy02 backup_20260608_050000.dump
```
