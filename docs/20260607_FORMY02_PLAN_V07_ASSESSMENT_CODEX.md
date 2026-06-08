---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Formy02 Plan V07 Assessment

## Prior V06 concern resolved

V07 resolves the V06 styling concern. The plan now explicitly requires
dark-theme-safe component definitions based on GoLightly04 semantic tokens
(`bg-raised`, `bg-inset`, `border-subtle`, `text-ink`, `text-ink-muted`) and
warns implementers not to copy the light-only helper definitions from
`GoLightly04/web/src/styles/globals.css` verbatim.

## 1. Restore can hang while the admin auth session is still open

V07 correctly changes the Postgres backup utility so `restore_backup()` no
longer accepts an ORM `Session`. However, the admin restore route is still
specified as preserving Formy's admin route surface and auth requirement. In the
Formy reference, `require_admin` depends on `get_current_user`, which depends on
`get_session`; that SQLModel session is a yielded FastAPI dependency and is not
closed until the request finishes.

That matters because V07's restore flow runs `pg_restore --clean --if-exists`
inside the same request. On PostgreSQL, the auth dependency's user lookup can
leave an open transaction on the app connection while `pg_restore` tries to drop
and recreate tables such as `users`. The restore subprocess can then block
waiting for locks held by the still-open request dependency, and the request
cannot finish and release that dependency until the subprocess returns. This is
a material implementation risk for the required admin-facing restore feature.

Required correction: revise §10 so the restore route performs admin
authentication without holding any ORM session or open transaction while
`pg_restore` runs. Acceptable designs include a restore-specific auth dependency
that opens a short-lived session, validates the signed cookie/admin user, then
commits or rolls back and closes before returning; or an equivalent explicit
session-close boundary before invoking `restore_backup(dump_bytes)`. The plan
should also require a bounded subprocess timeout or Postgres lock timeout so a
failed restore cannot hang the admin request indefinitely. The optional
`pg_terminate_backend` note is not sufficient unless the app's own auth/session
connection is closed before restore begins.
