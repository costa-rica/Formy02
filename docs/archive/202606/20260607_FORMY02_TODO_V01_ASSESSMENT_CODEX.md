---
created_at: 2026-06-08
updated_at: 2026-06-08
created_by: codex (gpt-5.5)
modified_by: codex (gpt-5.5)
---

# Formy02 TODO V01 Assessment

## Concern 1: Phase 9 is not implementable from the Formy02 workspace

TODO V01 includes Phase 9 work in `/home/limited_user/applications/GoLightly04`
and asks for a commit in that separate repository. In this workflow, the writable
workspace is `/home/limited_user/applications/Formy02`; `GoLightly04` is only a
local reference app. That makes Phase 9's edit, validation, and commit steps
infeasible for an implementation agent constrained to this repository.

Required correction: split the GoLightly04 footer-link change into a separate
repo-scoped TODO or explicitly mark it as requiring a writable GoLightly04
checkout and separate implementation pass. Keep Formy02 implementation phases
independent, with Phase 2 providing the receiving `?theme=` behavior.

## Concern 2: Admin response routes are omitted from preservation/docs tasks

The Formy reference admin router includes `GET /admin/responses/{person_id}/detail`
for the modal and `DELETE /admin/responses/{person_id}` for deleting a surveyed
person and related responses/audio. PLAN_V08 says backend route signatures and
Formy's utility are preserved, and the PRD requires preserving 100% of Formy's
existing utility. TODO V01 mentions preserving the modal behavior but does not
explicitly preserve the delete action during the admin responses restyle, and
Phase 8's API docs list omits both routes.

Required correction: add explicit Phase 4 tasks to preserve the responses-table
delete action and its JavaScript flow while restyling. Add both routes to the
Phase 8 `endpoints/admin.md` API documentation list, sourcing response and error
shapes from the implemented handlers.

## Concern 3: Markdown frontmatter instructions contradict AGENTS.md

TODO V01 hardcodes `created_by: claude (opus-4.8)` in Phase 8 validation and
the cross-phase Markdown constraint. AGENTS.md requires `created_by` and
`modified_by` to identify the agent and model that actually creates or modifies
the file. If a non-Claude agent implements Phase 8, following TODO V01 would
produce invalid repository metadata.

Required correction: replace hardcoded `claude (opus-4.8)` checks with
`<implementing agent> (<model>)` per AGENTS.md. Validation should check for the
four required frontmatter keys and correct dates, not a specific planner
identity.

## Concern 4: Tailwind CLI acquisition depends on unavailable network access

Phase 2 requires downloading the standalone Tailwind CLI binary, but the current
implementation environment has restricted network access and no local
`tailwindcss` executable was found. That makes the Phase 2 setup and validation
steps infeasible as written.

Required correction: add an offline-compatible tooling path, such as requiring a
pre-provisioned `tailwindcss` binary, documenting its expected local path, or
using a checked-in/package-managed build tool that can run without an ad hoc
network download during implementation.
