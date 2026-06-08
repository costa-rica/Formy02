---
created_at: 2026-06-07
updated_at: 2026-06-07
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Formy02 Plan V03 Assessment

## 1. The backup route plan mixes the old SQLite call contract with the new Postgres utility contract

V03 correctly replaces the old CSV zip backup with `pg_dump` custom-format
`.dump` files, but §10.1 still says the backup route handlers call the utility
functions at the "same call sites as Formy" while §10.3-§10.4 define new
sessionless utility calls: `db_backup.create_backup()` and
`db_backup.restore_backup(dump_bytes: bytes)`.

Evidence:

- In Formy, `/admin/db/backup` accepts `db: Session = Depends(get_session)` and
  calls `db_backup.create_backup(db)`.
- In Formy, `/admin/db/restore` validates `.zip` uploads and calls
  `db_backup.restore_backup(db, zip_bytes)`.
- In Formy, the download route returns `media_type="application/zip"`.
- V03's new `pg_dump` / `pg_restore` design reads DB parameters from config and
  does not use an ORM session for the dump or restore subprocesses.

If an implementer follows the "same call sites as Formy" instruction literally,
the routes can keep passing an ORM `Session` into utilities that no longer take
one, leave the `.zip` server-side validation in place, or continue serving
downloads as `application/zip`. That would break the preserved admin-facing
backup/restore functionality even though the UI text and file input were updated
to `.dump`.

Rewrite guidance: revise §10.1 and §10.5 to distinguish preserved public route
surface from changed handler internals. Keep the same HTTP paths, methods,
auth requirement, and JSON response shapes, but explicitly update the handler
calls and file handling:

- `/admin/db/backup` should require admin auth, call `db_backup.create_backup()`
  with no ORM session argument, and return `{"ok": true, "filename": dump_path.name}`.
- `/admin/db/restore` should require admin auth, validate that
  `backup_file.filename.endswith(".dump")`, read the bytes, and call
  `db_backup.restore_backup(dump_bytes)` with no ORM session argument.
- `/admin/db/backups/{filename}` should serve `.dump` files with an appropriate
  binary download media type such as `application/octet-stream` or
  `application/vnd.postgresql.dump`.
- Remove or replace the "same call sites as Formy" wording; the route surface is
  preserved, but the utility function signatures and server-side extension/media
  handling must change for the Postgres backup design to work.
