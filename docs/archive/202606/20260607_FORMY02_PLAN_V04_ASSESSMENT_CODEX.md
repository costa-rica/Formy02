---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Formy02 Plan V04 Assessment

## 1. The GoLightly footer-link implementation can break the existing new-tab behavior

V04 correctly scopes the GoLightly04 change to the existing "Help Us Improve"
footer link and correctly forwards the live theme via `?theme=`, but §11 permits
an implementation "via a React `onClick` handler that rewrites `location.href`."
That is not equivalent to the existing link behavior in the reference app.

Evidence:

- `GoLightly04/web/src/components/AppShell.tsx` currently renders the "Help Us
  Improve" anchor with `href="https://formy.go-lightly.love"`,
  `target="_blank"`, and `rel="noreferrer"`.
- Rewriting `location.href` from an `onClick` handler navigates the current tab
  and bypasses the anchor's `target="_blank"` behavior.
- The PRD says the only GoLightly04 change is to make the existing footer link
  forward the current theme. It does not ask to change how the link opens.

If an implementer chooses the `location.href` path allowed by V04, GoLightly04
would lose existing navigation behavior while implementing an otherwise small
theme handoff. That is a risk to existing functionality in the style/reference
app.

Rewrite guidance: constrain §11 to preserve anchor semantics. The plan should
say to keep an `<a>` with `target="_blank"` and `rel="noreferrer"`, and either:

- render a computed `href` such as
  `https://formy.go-lightly.love?theme=${currentTheme}` from React state, or
- in `onClick`, update `event.currentTarget.href` to include the current theme
  and then allow the browser's default anchor behavior to continue.

Do not set `window.location.href` or call `preventDefault()` unless the handler
also explicitly preserves the new-tab behavior with `window.open(..., "_blank",
"noreferrer")`; the computed-anchor approach is simpler and safer.
