# Page template + naming + write routing

Every Obsidian page the handoff skill writes follows this shape. The structure exists so that future readers (Claude or human) can scan a page in under thirty seconds.

## Page shape

```markdown
---
project: <repo-basename>
type: <tutorial|howto|reference|explanation|adr|index>
updated: <YYYY-MM-DD>
owner: <username or Claude>
---

# <Title>

> **Purpose.** <One or two sentences naming the audience and what they get from this page.>

<Body — most important information first. Headings as needed.>

## Related

- [[<linked page 1>]]
- [[<linked page 2>]]
```

## Which document types actually apply

The bundled documentation manual catalogs ~25 document types in its Part 2 (Project Charter, Business Case, Stakeholder Register, Risk Register, Change Requests, Closure Reports, etc.), aimed at formal-project documentation. Most do not apply to a typical Claude Code project handoff. The manual has an applicability matrix (look for the table headed "Deciding Which Documents Your Project Needs"); use it to scope.

For most repos handled by this plugin, the relevant page types are:

- **Project root index** — always (the path `pickup` reads from).
- **Feature / Reference pages** — one per significant feature or technical aspect.
- **ADRs** — one short page per decision.
- **How-to pages** — for procedures that recur or are non-obvious.
- **Learnings / gotchas** — known issues, surprises, workarounds.
- **Tech-stack reference** — versions, why-these-tools, gotchas at the dependency layer.
- **Getting Started tutorial** — only if the project is shareable / has new collaborators.

Anything in the manual's catalog not in this list is almost certainly out of scope for a single-developer plugin or library repo. Don't write a Stakeholder Register for a hobby project.

## Filename and title conventions

There are three distinct page kinds and they name differently:

- **Project root index page.** Filename is the project basename literally: `claude/<basename>/<basename>.md` (e.g. `claude/pgatzka-skills/pgatzka-skills.md`). This is the path `pickup` reads from, so the filename must match the basename character-for-character — dashes stay dashes, no Title-Casing. The H1 *title* inside the file may be human-readable ("# pgatzka-skills" or "# pgatzka-skills — marketplace overview").
- **Feature / Reference / How-to / Tutorial / Explanation pages.** Filename uses descriptive Title Case with spaces: `Structured Questions Plugin.md`, `How to Add a New Plugin.md`, `Marketplace Layout.md`. Spaces (not dashes) because Obsidian wiki-links resolve cleanly off the title shown in the sidebar.
- **ADRs.** Filename `ADR - YYYY-MM-DD - <short decision>.md` with spaces around the dashes (e.g. `ADR - 2026-05-13 - Use Python for Hook Scripts.md`). ISO date sorts chronologically.

When in doubt: the project root index uses the basename verbatim; everything else uses descriptive Title Case with spaces.

## Write routing

Pick the write call that matches the semantics of the page:

- **New page** → `obsidian_write_note` (creates the path implicitly; no need to create folders first).
- **Snapshot overwrite** (the project root index page, current-state pages) → `obsidian_write_note` with `overwrite: true`. Because: these pages reflect the *latest* — keeping history would grow them unboundedly and pickup would have to dig through stale snapshots.
- **Append to log-style page** (dated journals, running status notes) → `obsidian_append_to_note`.
- **Merge into a Reference page** (tech stack, conventions, known issues) → `obsidian_get_note` first to read current content, reconcile in memory (keep what's still true, update what changed, add what's new), then `obsidian_write_note` with `overwrite: true`. Never blindly overwrite a Reference page, because Reference pages accumulate facts across many sessions — a fresh write would discard prior knowledge that's still true.
- **ADRs** → always `obsidian_write_note` to a fresh dated file. Never modify a prior ADR, because the historical record is the value — readers look for "what did we decide when, and why". If a new decision supersedes an old one, write a new ADR that names and links the prior one.

## Per-call Obsidian failure handling

If `obsidian_get_note` or `obsidian_list_notes` errors on a specific path that should exist (e.g. `list_notes` reported the page but `get_note` 404s, or the MCP throws on a single call while staying connected for others):

- Surface the error in the final handoff report — don't silently swallow it.
- Skip writing to that page; do NOT call `obsidian_write_note` blindly as a recovery, because that risks overwriting a page whose current contents are unknown.
- Continue with the remaining checklist items so a partial handoff still lands.

If the MCP itself goes away mid-handoff (multiple calls all failing), stop entirely and report — the cross-machine sync guarantee is broken.

## Quality bar per page

Before considering a page written, verify:

- One Diátaxis category — the page does not mix Tutorial with Reference, etc.
- Title matches what a reader would search.
- Purpose statement appears in the first two lines after the H1.
- Body leads with the most important information.
- Related links at the bottom point at sibling pages, the index, and any superseding/superseded ADRs.
- Frontmatter `updated` is today's date in ISO format.
