---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Ubuntu PostgreSQL And Service Setup

Install PostgreSQL:

```bash
sudo apt update
sudo apt install postgresql postgresql-client
sudo systemctl enable --now postgresql
```

Create database and user:

```bash
sudo -u postgres psql
CREATE USER formy02 WITH PASSWORD 'change-me';
CREATE DATABASE formy02 OWNER formy02;
\c formy02
GRANT ALL ON SCHEMA public TO formy02;
\q
```

Systemd service should depend on PostgreSQL:

```ini
[Unit]
Description=Formy02
After=network.target postgresql.service
Requires=postgresql.service

[Service]
WorkingDirectory=/opt/formy02
EnvironmentFile=/opt/formy02/.env
ExecStart=/opt/formy02/venv/bin/uvicorn src.app.main:app --host 0.0.0.0 --port 8000
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

Production restore from a `.dump` file:

```bash
sudo systemctl stop formy02
PGPASSWORD=change-me pg_restore --clean --if-exists --no-owner --no-privileges \
  --format=custom --host=localhost --port=5432 --username=formy02 \
  --dbname=formy02 backup_20260608_050000.dump
sudo systemctl start formy02
```
