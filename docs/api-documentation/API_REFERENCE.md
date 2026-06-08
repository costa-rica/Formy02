---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# API Reference

Formy02 is a server-rendered FastAPI app with public questionnaire routes, auth routes, and admin routes.

- [Questionnaire](endpoints/questionnaire.md)
- [Auth](endpoints/auth.md)
- [Admin](endpoints/admin.md)

Standard JSON errors use:

```json
{"error":{"code":"NOT_FOUND","message":"Resource not found.","details":null,"status":404}}
```
