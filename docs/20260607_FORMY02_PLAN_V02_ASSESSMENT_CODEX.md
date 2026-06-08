---
created_at: 2026-06-07
updated_at: 2026-06-07
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Formy02 Plan V02 Assessment

## 1. The theme precedence algorithm conflicts with the PRD

V02 says the Formy02 pre-paint script should read `?theme=` first, then fall
back to Formy02's stored preference, then default to light. In the same section,
it also says that once the user toggles in Formy02, the Formy02 preference
overrides future incoming params. Those two rules cannot both be true if the
script always prioritizes `?theme=`.

Evidence:

- PRD §7.2 requires the incoming `theme` parameter to be an initial hint only.
- PRD §7.2 also requires that once the user toggles in Formy02, their Formy02
  preference takes precedence over the incoming param.
- V02 §7 instructs the script to read `?theme=` before the stored `formy.theme`
  value. That means a later click from GoLightly04 with `?theme=dark` or
  `?theme=light` would override a Formy02 user preference that was already set
  by the local toggle.

This risks implementing a theme handoff that works on first visit but breaks the
required local preference behavior on later visits.

Rewrite guidance: make the plan distinguish a GoLightly-provided initial hint
from a user-set Formy02 preference. For example, store both `formy.theme` and a
small marker such as `formy.themeUserSet`; the pre-paint order should be:

1. If `formy.themeUserSet` is true and `formy.theme` is valid, apply the stored
   Formy02 preference and ignore `?theme=`.
2. Otherwise, if `?theme=` is exactly `light` or `dark`, apply it and persist it
   as the current theme without marking it user-set.
3. Otherwise, fall back to a valid stored `formy.theme`, then default to light.
4. The in-app toggle writes `formy.theme` and sets `formy.themeUserSet=true`.

That preserves GoLightly's cross-site first-visit handoff while satisfying the
PRD's requirement that Formy02's own toggle wins after the user chooses locally.
