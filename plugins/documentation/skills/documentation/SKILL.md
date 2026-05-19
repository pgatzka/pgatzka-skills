---
name: documentation
description: This skill should be used whenever the user asks Claude Code to write, update, or remove documentation outside of session handoff — phrases like "update the docs for X", "document this feature", "the docs are out of date on Y", "delete the old section about Z", "remove the obsolete page about W", "rewrite the Y section", "fix the documentation for the hook", "the X behavior changed — reflect in docs", "the Z page is wrong, fix it", "merge these two pages", "split the X page into Y and Z", "consolidate the docs about A", "supersede the old ADR", "this section no longer applies", "write documentation for X", "add a how-to for installing the plugin", "write a reference page for the hook behavior", "add an ADR for the database choice", "explain why we picked Obsidian", "document our conventions", "where should we document this?", "we should write this down", "capture this in the docs", "make a page for the deployment flow", "archive the old auth notes", "this needs documentation". Also fires when Claude is about to produce documentation as part of a task and a deliberate page-shape decision matters (e.g. user just shipped a feature and says "now document it"). One ask = a maintenance sweep across the project's Obsidian docs: create what's missing, update what's stale, delete what's obsolete, in one pass. Writes the result to the project's Obsidian folder structured per the same Diátaxis manual the session-management plugin bundles. Not for capturing session state (use /session-management:handoff), reading existing docs (use /session-management:pickup), or in-code comments. Requires the session-management plugin to be installed in the same marketplace — the manual it bundles is the shared contract this skill reuses.
allowed-tools: Read, Bash, AskUserQuestion, mcp__obsidian__obsidian_list_notes, mcp__obsidian__obsidian_get_note, mcp__obsidian__obsidian_search_notes, mcp__obsidian__obsidian_write_note, mcp__obsidian__obsidian_append_to_note, mcp__obsidian__obsidian_patch_note, mcp__obsidian__obsidian_replace_in_note, mcp__obsidian__obsidian_delete_note
---

# /documentation:documentation

Treat the user's ask as a **maintenance pass** on the project's Obsidian documentation — not a single-page write. One ask can produce any mix of creates, updates, and deletes across multiple pages, all in service of leaving the doc set accurately reflecting current truth.

Walk the steps in order. Skip a step only if its output would be empty, and say so explicitly in the final report.

## Step 0 — Read the shared documentation manual

Read `${CLAUDE_PLUGIN_ROOT}/../session-management/references/documentation_tutorial_manual.md` via the `Read` tool now. It is the contract for every page — Diátaxis (Tutorial / How-to / Reference / Explanation) categories, page structure, split/merge rules, ADR naming, hierarchy depth.

The manual physically lives in the `session-management` plugin because `handoff`/`pickup` were its first consumers; this skill is a second consumer of the same contract, so the marketplace ships them together and this skill loads the file via the cross-plugin relative path above.

If the file is missing at that path, the `session-management` plugin is probably not installed in this marketplace. Tell the user this skill depends on `session-management` and stop — don't improvise page shapes without the manual.

## Step 1 — Verify the Obsidian MCP is connected

Look for `mcp__obsidian__*` tools in the current session. If they are absent, **stop and tell the user** the Obsidian MCP is not connected, with the error if any. Do not fall back to writing local files under any circumstance — the destination is Obsidian by design, and a quiet local fallback would let project knowledge diverge between machines.

## Step 2 — Determine the project's vault folder

Convention: `claude/<cwd-basename>`. Get the basename via `Bash` (e.g. `basename "$PWD"`) and use that for every path below. Example: cwd `G:/projects/pgatzka-skills` → folder `claude/pgatzka-skills`.

This is the same folder convention `session-management` uses, so anything this skill writes is visible to `/session-management:pickup` on the next session.

The Obsidian MCP creates the folder implicitly on the first `obsidian_write_note`, so no explicit "create folder" call is needed.

## Step 3 — Inventory and search

Two calls, in parallel where possible:

1. `obsidian_list_notes` on the project folder — full set of existing pages.
2. `obsidian_search_notes` with the topic terms from the user's ask — surfaces pages that mention the topic even when the title doesn't.

The goal is a complete view of what touches the topic. Pages that are merely *related* (cross-link the topic, mention it in passing) matter too, because an update may need to follow those references and adjust linked pages.

If either call errors (and the folder isn't just empty), report the error in the final report and probe likely paths with `obsidian_get_note` before deciding any operation. Don't proceed blind.

## Step 4 — Map the ask to operations

For every page that touches the topic, decide one of:

- **CREATE** — no page exists for content that should exist; write a new one.
- **UPDATE** — page exists and is partly correct; modify the affected sections, leave the rest. Subtypes: rewrite a section, add a section, remove a section, replace a phrase, append a new entry to a log.
- **DELETE** — page exists and is entirely obsolete or superseded; remove it. (See Step 5 for the guardrail.)
- **SUPERSEDE** — applies to ADRs only: write a new dated ADR that names the prior one as superseded; do *not* delete or edit the prior ADR (the historical record is the value).
- **LEAVE** — page is correct as-is; no operation. Note it in the report so the user sees it was considered.

Apply the manual's split/merge rules when shaping UPDATEs:

- If a page has grown to cover two distinct topics, the update may *split* it: write a second page for the offloaded topic, then UPDATE the original to drop that content and link out.
- If two near-duplicate pages exist, the update may *merge* them: pick one as the canonical home, UPDATE it with the merged content, DELETE the other.

Read each candidate page with `obsidian_get_note` before classifying — operation choice depends on the current content, not a guess from the title.

## Step 5 — Confirm any deletes the user did not explicitly name

`DELETE` is destructive and not always recoverable from Obsidian (depends on the user's vault setup). Apply this guardrail:

- If the user **explicitly named** the page to delete ("delete the old auth notes page", "remove the OAuth ADR"), proceed without asking.
- If the delete is **inferred** from the ask ("merge these two pages" → implies deleting the non-canonical one; "supersede X" with the user expecting cleanup → implies deleting the old reference), confirm via a single `AskUserQuestion` listing every inferred delete. Use a binary `Confirm`/`Cancel` pair (no marker, no Pros/Cons — `structured-questions` Rule 2 Y/N exemption) for each individual page, or a non-Y/N question if there's a third path ("delete vs archive vs keep").

If the user declines a delete, demote it to a SUPERSEDE-style UPDATE: leave the page in place but prepend a deprecation note (`> **Deprecated.** Superseded by [[<new page>]] on YYYY-MM-DD.`) so readers landing on it via search aren't misled.

The user said "make the reasonable call and continue" — for low-stakes calls. Destructive operations like file deletion are higher-stakes and explicitly carve out a confirmation in the system instructions about reversibility. This guardrail respects that.

## Step 6 — Read the page-shape and write-routing reference

Read `${CLAUDE_PLUGIN_ROOT}/../session-management/skills/handoff/references/page_template.md` via the `Read` tool now, before executing any operation. That file is the canonical reference for:

- Frontmatter shape (`project`, `type`, `updated`, `owner`).
- Filename conventions per page kind: project root index = basename verbatim; sub-pages = descriptive Title Case with spaces; ADRs = `ADR - YYYY-MM-DD - <decision>.md`.
- Write-call routing semantics: `obsidian_write_note` for new pages and snapshot overwrites; `obsidian_append_to_note` for log-style pages; `get_note`+reconcile+`write_note` for merge-style Reference updates.
- Per-call Obsidian failure handling — surface errors in the final report, never silently swallow.

Same template governs `handoff`'s output, so pages this skill produces are indistinguishable in shape from `handoff`'s — which is the point: one consistent vault.

## Step 7 — Execute the operations

For each operation classified in Step 4:

- **CREATE**: `obsidian_write_note` with the new page. Set `updated` frontmatter to today's date (from `currentDate` context, or `Bash` `date -I`).
- **UPDATE — small targeted edit** (one section's heading is wrong, one bullet is stale, a function name changed): `obsidian_patch_note` for heading/block-level surgery, or `obsidian_replace_in_note` for find/replace within the page. These keep diffs small and preserve unrelated content.
- **UPDATE — section rewrite or larger reshape**: `obsidian_get_note` → reconcile in memory (keep what's still true, rewrite what changed, remove what's obsolete) → `obsidian_write_note` with the merged content. Bump `updated` frontmatter.
- **UPDATE — append to log-style page**: `obsidian_append_to_note`.
- **DELETE** (already gated by Step 5): `obsidian_delete_note`.
- **SUPERSEDE** (ADR): `obsidian_write_note` to a new `ADR - YYYY-MM-DD - <decision>.md` whose body explicitly names the prior ADR as superseded and links to it. Do *not* touch the prior ADR.

For ADRs: today's date is `currentDate` from the session context (or shell `date -I` via `Bash`); convert any relative date the user gives ("yesterday's decision") to an absolute YYYY-MM-DD before naming the file.

If any single operation fails, surface the error in the final report and continue with the remaining operations — don't abort the whole sweep on one failure. If the MCP itself goes away mid-sweep (multiple consecutive failures across different pages), stop and report — cross-machine sync is broken.

## Step 8 — Reconcile the project root index

The project root index at `claude/<basename>/<basename>.md` lists every page under "Pages in this project" (Tutorials / How-to / Reference / Explanation / Decisions). The maintenance sweep can have added or removed pages, so the index needs reconciling **only if** Step 7 produced any CREATE or DELETE.

If yes, use a **merge update**, not a wholesale overwrite — wholesale overwrite is `handoff`'s job:

1. `obsidian_get_note` the index.
2. In memory: add a `[[Descriptive Title]]` link under the right heading for each CREATE; remove the link for each DELETE; leave everything else untouched.
3. `obsidian_write_note` the merged content back.

If the index returns *not found* (no prior handoff has ever run for this project), create a minimal index with at least:

- A `Purpose` paragraph (one sentence inferred from cwd basename + the topics touched in this sweep).
- A `Current state` line: "Index bootstrapped by `/documentation:documentation` on `<YYYY-MM-DD>`; flesh out at next `/session-management:handoff`."
- A `Pages in this project` section listing the pages this sweep created, under their categories.

This minimal index satisfies the handoff↔pickup contract — both "Current state" and "Pages in this project" markers must be present so `pickup` Step 3's sanity-check recognizes it as a valid index. See `${CLAUDE_PLUGIN_ROOT}/../session-management/skills/handoff/SKILL.md` Step 7 for the full required-section list. The next `/session-management:handoff` will overwrite this minimal index with the full snapshot.

If `obsidian_get_note` on the index returns a non-404 error (MCP threw, permission denied), stop and surface the error — do *not* treat the error as "missing" and write a fresh index over what might be a real one.

If the existing index is present but **doesn't look like an index** (missing both "Current state"/"Open tasks" and "Pages in this project" markers), a same-named non-index note may be sitting at that path. Ask the user via `AskUserQuestion` (compliant per `structured-questions`) how to proceed — same defense `handoff` does at its Step 7.

If Step 7 only produced UPDATEs (no CREATE, no DELETE), leave the index untouched — the link set hasn't changed.

## Step 9 — Report

Output a structured report grouped by operation:

- **Vault folder path used.**
- **Created**: each new page — path + Diátaxis category + one-line purpose.
- **Updated**: each changed page — path + what changed (which sections; which write call used; one-line diff summary).
- **Deleted**: each removed page — path + reason + whether the user explicitly named it or confirmed via the Step 5 guardrail.
- **Superseded** (ADRs): each new dated ADR + path of the prior ADR it supersedes.
- **Left as-is**: pages that touched the topic but were correct; list them so the user sees they were considered.
- **Index reconciliation**: which links were added or removed, or "index untouched" if only UPDATEs ran.
- **Errors**: any per-call Obsidian failures (which page, which call, what to do next time).

Then **stop**. Do not start another sweep unless the user explicitly asks — one ask = one sweep across the affected pages.

## Relationship to session-management

Three different operations on the same Obsidian vault:

- `/session-management:handoff` — fires at session end. Captures session state across many pages in one pass. Overwrites the project root index wholesale.
- `/session-management:pickup` — fires at session start. Reads the index and briefs the user. Never writes.
- `/documentation:documentation` (this skill) — fires on any explicit user ask to write, update, or remove docs. Sweeps the project's doc set: creates, updates, deletes as needed. Reconciles the index by merge, not by overwrite.

All three share the vault folder (`claude/<basename>`), the manual, and the page template. Pages this skill writes (or unlinks) will surface in the next `pickup` brief under "Pages in this project".

If the user is wrapping up a session and asks for both a doc sweep and a handoff in the same turn, prefer running this skill first (so the doc set is current) and then `/session-management:handoff` (so its index overwrite picks up the latest link set). Don't run them in the opposite order — handoff's snapshot would be stale by one sweep within seconds.

## When in doubt

Re-read the relevant section of the manual at `${CLAUDE_PLUGIN_ROOT}/../session-management/references/documentation_tutorial_manual.md` or the page template at `${CLAUDE_PLUGIN_ROOT}/../session-management/skills/handoff/references/page_template.md`.

Defaults when judgment is needed:

- Split over merge — two well-scoped pages beat one overgrown one.
- Descriptive titles over short ones — the title is the wiki-link target.
- Update in place over create-new when category and topic match — duplicate pages are worse than slightly larger ones.
- Confirm deletes the user didn't explicitly name — destructive operations are hard to reverse.
- Write or correct the page over skipping — if it's not in Obsidian, the next session can't find it.
