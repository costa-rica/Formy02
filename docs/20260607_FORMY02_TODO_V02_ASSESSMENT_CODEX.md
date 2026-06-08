---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5)
modified_by: codex (gpt-5)
---

# Formy02 TODO V02 Assessment — Codex

Assessment target: `docs/20260607_FORMY02_TODO_V02.md`

Reference plan: `docs/20260607_FORMY02_PLAN_V08.md`

Reference PRD: `docs/20260607_FORMY02_PRD.md`

Reference apps: `/home/limited_user/applications/Formy` and
`/home/limited_user/applications/GoLightly04`

## Qualifying concerns

### 1. Auth API docs task lists the wrong and incomplete route surface

TODO V02 Phase 8 lists the auth endpoint documentation set as:

```text
POST /register
GET /verify
POST /login
GET /logout
POST /forgot-password
POST /reset-password
```

This contradicts the Formy source route surface that the PRD requires Formy02 to
preserve. In `/home/limited_user/applications/Formy/src/app/routes/auth.py`, the
actual auth routes are:

- `GET /login`
- `POST /login`
- `GET /register`
- `POST /register`
- `GET /verify`
- `POST /logout`
- `GET /forgot-password`
- `POST /forgot-password`
- `GET /reset-password/{token}`
- `POST /reset-password/{token}`

The TODO currently invents `GET /logout`, omits the GET page routes, and drops
the `{token}` path parameter from reset-password routes. This is material because
Phase 8 also says response shapes and route docs must be sourced from actual
handler code; following the current checklist would produce incorrect API docs
and could encourage an implementer to add or link to the wrong logout method.

Required TODO correction:

- Replace `GET /logout` with `POST /logout`.
- Add `GET /login`, `GET /register`, `GET /forgot-password`,
  `GET /reset-password/{token}`, and `POST /reset-password/{token}` to
  `endpoints/auth.md`.
- Ensure any base/header logout control preserved or created by earlier phases
  submits a `POST /logout` form, matching Formy's `base.html` and route handler.

### 2. Admin whitelist env-var guidance is ambiguous and conflicts with PRD/source naming

TODO V02 Phase 1.5 says:

```text
The ALLOWED_ADMIN_EMAILS env var is retained in config.py
```

In the Formy source and PRD, `EMAIL_ADMIN_USER` is the environment variable.
`ALLOWED_ADMIN_EMAILS` is a derived Python set in `config.py`, built from
`EMAIL_ADMIN_USER`, and `routes/auth.py` checks registration against that derived
set. The PRD explicitly names the `EMAIL_ADMIN_USER` whitelist.

This ambiguity risks a broken `.env.example`, README, or config implementation
where a new `ALLOWED_ADMIN_EMAILS` environment variable is introduced and the
existing `EMAIL_ADMIN_USER` contract drifts.

Required TODO correction:

- State that `EMAIL_ADMIN_USER` remains the required env var for the admin email
  whitelist.
- State that `config.ALLOWED_ADMIN_EMAILS` remains a derived set computed from
  `EMAIL_ADMIN_USER`.
- Ensure `.env.example` and README document `EMAIL_ADMIN_USER`, not an
  `ALLOWED_ADMIN_EMAILS` env var.

## Assessment result

TODO V02 is close to implementable, but the two issues above are qualifying
concerns because they contradict the preserved Formy route/config contracts and
would produce incorrect documentation or authentication wiring. A V03 TODO should
correct these before implementation begins.
