---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: hermes nws-go-lightly-dev (gpt-5.5)
---

# Ubuntu PostgreSQL And Service Setup

This guide targets an Ubuntu host running apt-managed PostgreSQL and the Formy02 FastAPI service. Formy02 follows the GoLightly04 local-trust pattern: the app connects over loopback with a project-specific PostgreSQL role and no database password in `.env`.

## First Build

### 1. Install and start PostgreSQL

```bash
sudo apt update
sudo apt install -y postgresql postgresql-client postgresql-contrib
sudo systemctl enable --now postgresql
pg_isready -h 127.0.0.1 -p 5432
sudo systemctl status postgresql
```

### 2. Allow Formy02 local connections without a password

Find the active `pg_hba.conf`:

```bash
sudo -u postgres psql -c "SHOW hba_file;"
```

Edit the file shown by that command and add Formy02-specific trust rules near the top, before broader `local`/`host` rules:

```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

```text
# Formy02 application role
local   formy02   formy02   trust
host    formy02   formy02   127.0.0.1/32   trust
```

Reload PostgreSQL and confirm the database port is not exposed publicly:

```bash
sudo systemctl reload postgresql
sudo ufw status
ss -ltnp | grep 5432
```

### 3. Create the role and database

```bash
sudo -u postgres psql -c "CREATE ROLE formy02 WITH LOGIN;"
sudo -u postgres createdb -O formy02 formy02
```

### 4. Grant schema privileges

PostgreSQL 15+ does not grant `CREATE` on the `public` schema to everyone by default. Formy02 creates SQLModel tables on startup, so the app role needs schema creation rights.

```bash
sudo -u postgres psql -d formy02 -c "GRANT ALL ON SCHEMA public TO formy02;"
```

### 5. Configure `.env`

Use loopback so the connection matches the `host` trust rule above. Do not set `DB_PASSWORD`.

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=formy02
DB_USER=formy02
DB_SCHEMA=
```

### 6. Configure the systemd service

Adjust `WorkingDirectory` and `EnvironmentFile` if your checkout lives somewhere other than `/opt/formy02`.

```ini
[Unit]
Description=Formy02
After=network.target postgresql.service
Requires=postgresql.service

[Service]
WorkingDirectory=/opt/formy02
EnvironmentFile=/opt/formy02/.env
ExecStart=/home/limited_user/environments/formy02/bin/uvicorn src.app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable the app service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now formy02
sudo systemctl status formy02
```

### 7. Verify the database connection

Use `-h 127.0.0.1` to force a TCP loopback connection that matches the `host` trust rule. Without `-h`, `psql` may try peer auth and fail unless the Unix user is also named `formy02`.

```bash
psql -h 127.0.0.1 -U formy02 -d formy02 -c "SELECT current_user, current_database();"
```

After the app starts and creates tables:

```bash
psql -h 127.0.0.1 -U formy02 -d formy02 -c "\dt"
```

## Backup and restore

Admin UI routes can create/list/delete custom-format PostgreSQL `.dump` backups under `${PATH_PROJECT_RESOURCES}/backups_db`.

Operator restore from a `.dump` file:

```bash
sudo systemctl stop formy02
pg_restore --clean --if-exists --no-owner --no-privileges \
  --format=custom --host=127.0.0.1 --port=5432 --username=formy02 \
  --dbname=formy02 backup_20260608_050000.dump
sudo systemctl start formy02
```

## Environment variables reference

| Variable | Value | Notes |
| --- | --- | --- |
| `DB_HOST` | `127.0.0.1` | Use loopback to match the `host` trust rule. |
| `DB_PORT` | `5432` | Default PostgreSQL port. |
| `DB_NAME` | `formy02` | Application database. |
| `DB_USER` | `formy02` | Passwordless local application role. |
| `DB_SCHEMA` | blank or `public` | Optional; leave blank for SQLModel default schema. |
| `DB_PASSWORD` | not set | Omit entirely; localhost trust auth is used. |
