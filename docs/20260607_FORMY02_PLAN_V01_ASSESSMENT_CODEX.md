---
created_at: 2026-06-07
updated_at: 2026-06-07
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Formy02 Plan V01 Assessment

## 1. The Postgres plan misunderstands the existing `Question.options` mapping

The plan says `Question.options` is a `list[str]` that should map directly to a
Postgres JSON/ARRAY column. In the Formy reference app, `Question.options` is not
the persisted SQLModel field. The persisted field is `options_json`, declared as
`Field(default=None, sa_column=Column("options", Text))`, and `options` is a
Python property that serializes/deserializes JSON strings.

Evidence:

- `Formy/src/app/models/question.py` stores the database column as
  `options_json` on column name `options`.
- `Formy/src/app/routes/admin.py` creates and updates questions through
  `q.options = parsed_options`.
- `Formy/src/app/templates/questionnaire.html` reads `q.options` when rendering
  multiple-choice radios.

As written, an implementer could either leave the SQLite-style text serializer in
place while claiming Postgres JSON support, or replace it with a mapped
`options: list[str]` field and accidentally collide with the existing property
and route/template expectations. Either path risks breaking multiple-choice
question creation, display, or update.

Rewrite guidance: make the plan choose one concrete mapping. Recommended:
preserve the public model API (`q.options`) and database column name (`options`),
but change the backing column to a Postgres JSON/JSONB-compatible SQLAlchemy
column. Update the getter/setter accordingly so it no longer `json.dumps` values
when the database stores native JSON. The plan should name the exact field and
route/template contract to preserve.

## 2. Startup admin seeding conflicts with the PRD's auth flow and security requirements

The plan preserves the Formy startup flow as
`check_database() -> create_admin_user()` and says it seeds whitelisted admins
from `ALLOWED_ADMIN_EMAILS`. In the Formy reference, `create_admin_user()` creates
missing whitelisted users as verified admins with a hardcoded password of
`"test"` and also flips existing unverified users to verified.

Evidence:

- `Formy/src/app/utilities/on_start_up.py` creates missing users with
  `password=hash_password("test")`, `is_admin=True`, and `email_verified=True`.
- The PRD's auth requirement says registration should be whitelist-gated, create
  users with `email_verified = false`, send verification email, and block login
  until verification.
- The PRD's non-functional security requirements require hashed passwords,
  whitelist gating, and no weakened admin access on a publicly linked app.

If V01 is followed literally, Formy02 may launch with automatically verified
admin accounts protected by a known default password, bypassing the verification
flow the PRD asks to preserve. That is a risk to existing/auth functionality and
to the stated security posture.

Rewrite guidance: explicitly replace or constrain `create_admin_user()`. The plan
should either remove automatic admin creation and rely on the whitelisted
registration/verification flow, or require startup bootstrap credentials from
secure env vars with no hardcoded password and no automatic email verification.
Do not leave "seed whitelisted admins" as an unqualified carry-over from Formy.

## 3. The backup plan does not preserve Formy's in-app backup/restore surface

V01 says to adapt `db_backup.py` to a `pg_dump`-based dump and leaves the exact
CLI invocation/scheduling as a TODO-phase detail. Formy's backup utility is not
just an operator-side script: the admin dashboard exposes create, restore, list,
download, and delete actions through routes and UI.

Evidence:

- `Formy/src/app/routes/admin.py` defines `/admin/db/backup`,
  `/admin/db/restore`, `/admin/db/backups/{filename}` download, and backup
  deletion routes.
- `Formy/src/app/templates/admin/index.html` includes the database management UI
  for creating backups, restoring uploaded backups, listing saved backups, and
  deleting backups.
- The PRD says to preserve 100% of Formy's utility and to preserve an equivalent
  backup capability adapted for PostgreSQL, including restore.

A generic `pg_dump` note is not enough to preserve this feature. `pg_dump` output
is also not compatible with the existing CSV zip upload/restore workflow, so the
plan needs to specify how the admin routes and UI change. Otherwise an
implementer could produce only a shell/runbook backup path and silently drop the
admin-facing functionality.

Rewrite guidance: state that the admin database management routes and dashboard
section remain part of scope. Define the new backup artifact format (for example,
custom-format `pg_dump` files or zipped dumps), storage location under
`PATH_PROJECT_RESOURCES`, restore command/path, list/download/delete behavior,
and user-facing warnings. Also note that restore must be designed around
Postgres connections and cannot rely on the old SQLite CSV restore logic.
