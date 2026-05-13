---
description: Slash command `/session-management:handoff`. Write every load-bearing piece of session knowledge into the project's Obsidian folder, structured per the documentation manual bundled with this plugin (Diátaxis categories, descriptive titles, split/merge rules). Use when wrapping up a session, before context compaction, or whenever the user invokes the command. Project state lives in Obsidian, never in the repo working tree, and never bloated into CLAUDE.md.
argument-hint: "[optional focus area]"
allowed-tools: Read, Bash, Glob, Grep, TaskList, TaskGet, mcp__obsidian__obsidian_list_notes, mcp__obsidian__obsidian_get_note, mcp__obsidian__obsidian_write_note, mcp__obsidian__obsidian_append_to_note, mcp__obsidian__obsidian_manage_frontmatter, mcp__obsidian__obsidian_search_notes
---

# /session-management:handoff

Capture every load-bearing piece of session knowledge into the project's Obsidian folder so the next session can pick up productively from turn one. Project state lives in Obsidian, never in the repo working tree, and never bloated into CLAUDE.md (overlap with CLAUDE.md is fine — same fact, different depth, different audience).

Walk the steps in order. Skip a step only if its output would be empty, and say so explicitly in the final report.

## Step 0 — Read the documentation manual

Read `${CLAUDE_PLUGIN_ROOT}/references/documentation_tutorial_manual.md` (the manual bundled with this plugin). It is the contract for how every page is shaped. The rules that matter here:

- Every page falls into exactly one Diátaxis category: **Tutorial** (learning), **How-to** (goal-oriented), **Reference** (lookup), **Explanation** (understanding, including ADRs).
- Titles are descriptive and search-friendly — what a reader would type. "How to add a plugin to the marketplace", not "Plugin addition procedure".
- Page structure: title, `updated`/`owner` frontmatter, a one-or-two-sentence purpose statement, TOC for longer pages, body with most-important-first, related links at the bottom. Aim for ≤10% bold text.
- Split/merge rules in order (stop at the first match): different Diátaxis category → split; different update cadences → split; different audiences/owners → usually split; always read together → merge; one meaningless without the other → merge; combined size >20 pages → split.
- ADRs: one short page per decision, filename `ADR - YYYY-MM-DD - <decision>.md`.
- Hierarchy is shallow — flat under the project folder unless there's a reason to nest.

If the manual file is missing at the expected path, tell the user the plugin's reference is missing and proceed using the principles summarized above; don't silently improvise a different shape.

## Step 1 — Verify the Obsidian MCP is connected

Look for `mcp__obsidian__*` tools in the current session. If they are absent, **stop and tell the user** the Obsidian MCP is not connected, with the error if any. Do not write a local-file fallback under any circumstance — cross-machine sync is the entire point of routing state through Obsidian, and a quiet local fallback would let state diverge silently.

## Step 2 — Determine the project's vault folder

Convention: `claude/<cwd-basename>`. Get the basename via `Bash` (e.g. `basename "$PWD"`) and use that for every path below. Example: cwd `G:/projects/pgatzka-skills` → folder `claude/pgatzka-skills`.

The Obsidian MCP creates the folder implicitly on the first `obsidian_write_note`, so no explicit "create folder" call is needed.

## Step 3 — Inventory existing pages

Call `obsidian_list_notes` on the project folder. Note what already exists and infer each page's Diátaxis category from its title. This is the basis for deciding whether new session content extends an existing page or creates a new one.

## Step 4 — Walk the completeness checklist

For each item, capture what this session produced. If nothing applies, write "nothing this session" in the final report — never fabricate content.

1. **Project overview** — purpose, tech stack one-liner, top-level structure. Updates the project root index page.
2. **Current state of work** — what's implemented and working, what's stubbed, what's incomplete. Concrete file:line pointers over prose.
3. **Open tasks** — what the next session should pick up. Priority-ordered, with acceptance criteria per task. Read from `TaskList` if present.
4. **Open questions** — decisions pending the user. Include why each blocks progress.
5. **Decisions made this session** — each becomes an ADR (Explanation, one page per decision). Title `ADR - YYYY-MM-DD - <short decision>.md`. Body: context, decision, alternatives considered, reasoning, links to related pages.
6. **Tech-stack changes** — new deps, version bumps, tool swaps. Merges into the tech-stack Reference page.
7. **New or extended features** — one Reference or Explanation page per feature ("Structured Questions Plugin", "Session Management Plugin", etc.). Reference for *what it is*; Explanation for *why it's shaped that way*.
8. **Gotchas and dead ends** — surprises hit, with root cause and fix or workaround. File:line pointers. Usually a Reference page ("Known issues") or appended to the relevant feature page.
9. **Conventions or rules learned** — durable preferences the user expressed (commit style, error-handling preference, naming convention). Reference page per area.
10. **Next-session orientation** — a one-paragraph "start here" pointer; lives on the index page.

For each captured item, also classify whether it is *universally applicable to every session in this project*. If yes, flag it as a possible CLAUDE.md addition in the final report — but **do not modify CLAUDE.md from this skill**. CLAUDE.md edits are the user's call. Overlap with Obsidian is expected: CLAUDE.md gets the one-liner, Obsidian gets the depth.

## Step 5 — Classify and route each item

For each captured item from Step 4:

- **Diátaxis category.** Tutorial / How-to / Reference / Explanation. ADRs are Explanation.
- **New page vs. extend existing.** Apply the manual's split/merge rules. Only reuse an existing page when the Diátaxis category matches AND the topic matches AND the update cadence is similar.
- **Descriptive title.** Reflect what a reader would search. Title Case. Spaces, not dashes, in the file name where Obsidian renders it.

## Step 6 — Write each page

Every page follows this shape:

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

Pick the write call that matches the semantics:

- **New page** → `obsidian_write_note` (creates path implicitly).
- **Snapshot overwrite** (the index page, current-state pages) → `obsidian_write_note`.
- **Append to log-style page** (dated journals, running status notes) → `obsidian_append_to_note`.
- **Merge into a Reference page** (tech stack, conventions, known issues) → `obsidian_get_note` first to read current content, reconcile in memory (keep what's still true, update what changed, add what's new), then `obsidian_write_note` to replace. Never blindly overwrite a Reference page.
- **ADRs** → always `obsidian_write_note` to a fresh dated file. Never modify a prior ADR. If a new decision supersedes an old one, write a new ADR that names and links the prior one.

## Step 7 — Update the project root index page

Path: `claude/<basename>/<basename>.md` (e.g. `claude/pgatzka-skills/pgatzka-skills.md`). Overwrite on every handoff — this is the snapshot, not a log.

Required sections:

1. **Purpose** — what this project is, one paragraph.
2. **Tech stack** — one-liner; link to the Reference page for depth.
3. **Current state** — a paragraph summarizing where work stands right now.
4. **Open tasks** — bullets, priority-ordered.
5. **Open questions** — bullets.
6. **Pages in this project** — categorized links: Tutorials / How-to / Reference / Explanation / Decisions (ADRs). Each link is a wiki link `[[Descriptive Title]]`.
7. **Next-session orientation** — one line: "Picking this up fresh? Start with [[<page>]]."

## Step 8 — Report

Output a structured report:

- Vault folder path used.
- Pages created (path + Diátaxis category + one-line purpose).
- Pages updated (path + what changed).
- Items captured per checklist step, or "nothing this session" if skipped.
- Anything flagged as a possible CLAUDE.md addition, with a recommended one-liner the user can paste in.

Then **stop**. Do not start new implementation work — the session is wrapping up.

## When in doubt

The manual is the contract. If a situation isn't covered above, re-read the relevant section of `${CLAUDE_PLUGIN_ROOT}/references/documentation_tutorial_manual.md`. Default to splitting over merging; default to descriptive titles over short ones; default to writing the page over skipping — if it's not in Obsidian, the next session can't find it.
