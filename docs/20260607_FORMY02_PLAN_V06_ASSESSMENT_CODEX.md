---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Formy02 Plan V06 Assessment

## 1. The Tailwind component-class plan can break dark-mode surfaces

V06 correctly requires the semantic GoLightly04 color tokens (`bg-raised`,
`bg-inset`, `text-ink`, `border-subtle`, etc.) and a class-based dark theme, but
it also tells implementers to copy the `@layer components` helper classes from
`GoLightly04/web/src/styles/globals.css` and convert templates to those
component classes. In the local reference app, those helper classes are not the
main dark-mode surface system: `.card` is `bg-white ... border-calm-200`,
`.input-field` uses fixed light borders, and `.section-heading` uses
`text-calm-800`. The actual GoLightly04 screens mostly use semantic utilities
such as `border-subtle bg-raised text-ink` and `bg-inset`, which are backed by
the light/dark CSS variables.

Evidence:

- V06 §6 says to include `.input-field`, `.card`, and `.section-heading`, then
  convert all Jinja templates from Bootstrap to the Tailwind/component classes.
- `GoLightly04/web/src/styles/globals.css` defines `.card` as `bg-white` with a
  fixed calm border and no `.dark` variant.
- `GoLightly04/web/src/app/profile/page.tsx` uses
  `border-subtle bg-raised text-ink` for a card-like section and `bg-inset` for
  controls, demonstrating the token-based pattern that actually adapts to dark
  mode.
- The PRD acceptance criteria require all pages to render in GoLightly04's
  visual language in both light and dark themes.

If V06 is followed literally, Formy02 can ship with white cards, light borders,
and light-only headings inside the dark theme. That would not break routing, but
it materially risks the required dark-mode implementation and the visual match to
the local GoLightly04 architecture.

Required correction: revise §6 to state that Formy02 component classes must be
dark-theme safe. Either redefine `.card`, `.input-field`, `.btn-outline`, and
`.section-heading` around the semantic tokens (`bg-raised`, `bg-inset`,
`bg-overlay`, `border-subtle`, `text-ink`, `text-ink-muted`, plus dark-safe focus
states), or avoid those helper classes for surfaces and use the semantic utility
classes directly in the Jinja templates. Do not copy GoLightly04's light-only
helper definitions verbatim when they are used as the primary Formy02 page
building blocks.
