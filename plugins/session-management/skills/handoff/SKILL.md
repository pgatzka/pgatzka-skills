---
name: handoff
description: This skill should be used whenever the user invokes `/session-management:handoff` or signals that the session is wrapping up — phrases like "let's wrap up", "end of session", "save state", "save this", "remember this", "checkpoint", "checkpoint this", "save progress", "write this down", "before we run out of context", "before I close my laptop", "switching machines", "pause here", "that's a wrap for today", "I'm out of time", "let's continue tomorrow", "compact incoming", "goodnight", "ttyl", "EOD", "logging off", "shutting down", "I need to stop here", "I need to step away", "see you Monday", "have a good weekend", "brb", or task-completion signals like "shipped it", "PR is merged", "feature is done", "that's the last todo", "save handoff", "do a handoff", "write the handoff", "summarize what we did today", "write up the session", "park this", "save state for tomorrow", "merged", "deployed", "released", "tagged", "snapshot this", "dump state", "before I forget", "context is getting full", "before the context window fills", "running low on context", "before /clear", or before a planned context compaction (whether user-invoked `/compact` or a harness low-context warning), or after `/clear` is announced. It writes every load-bearing piece of session knowledge into the project's Obsidian folder, structured per the documentation manual bundled with this plugin (Diátaxis categories, descriptive titles, split/merge rules). Project state lives in Obsidian, never in the repo working tree, and never bloated into CLAUDE.md.
allowed-tools: Read, Bash, AskUserQuestion, mcp__obsidian__obsidian_list_notes, mcp__obsidian__obsidian_get_note, mcp__obsidian__obsidian_write_note, mcp__obsidian__obsidian_append_to_note
---

# /session-management:handoff

Capture every load-bearing piece of session knowledge into the project's Obsidian folder so the next session can pick up productively from turn one. Overlap with CLAUDE.md is fine — same fact, different depth, different audience. See Step 1 for why the Obsidian-only routing is non-negotiable.

Walk the steps in order. Skip a step only if its output would be empty, and say so explicitly in the final report.

## Step 0 — Read the documentation manual

Read `${CLAUDE_PLUGIN_ROOT}/references/documentation_tutorial_manual.md` (the manual bundled with this plugin) via the `Read` tool now. It is the contract for how every page is shaped — Diátaxis (the four-category documentation framework: Tutorial / How-to / Reference / Explanation) categories, page structure, split/merge rules, ADR naming, hierarchy depth.

If the manual file is missing at the expected path, tell the user the plugin's reference is missing. The skill can still proceed: `page_template.md` (loaded at Step 6) carries the authoritative filename, frontmatter, and write-routing conventions, and Step 5 below states the Diátaxis category rule. Don't silently improvise shapes those references don't cover.

## Step 1 — Verify the Obsidian MCP is connected

Look for `mcp__obsidian__*` tools in the current session. If they are absent, **stop and tell the user** the Obsidian MCP is not connected, with the error if any. Do not write a local-file fallback under any circumstance — cross-machine sync is the entire point of routing state through Obsidian, and a quiet local fallback would let state diverge silently.

## Step 2 — Determine the project's vault folder

Convention: `claude/<cwd-basename>`. Get the basename via `Bash` (e.g. `basename "$PWD"`) and use that for every path below. Example: cwd `G:/projects/pgatzka-skills` → folder `claude/pgatzka-skills`.

The Obsidian MCP creates the folder implicitly on the first `obsidian_write_note`, so no explicit "create folder" call is needed.

## Step 3 — Inventory existing pages

Call `obsidian_list_notes` on the project folder. Note what already exists and infer each page's Diátaxis category from its title. This is the basis for deciding whether new session content extends an existing page or creates a new one.

If `obsidian_list_notes` errors (not because the folder is empty — that's a normal result — but because the MCP throws): report the error in the final handoff report and continue with the folder *assumed* empty, not *verified* empty. Prior pages may exist at filenames the failed call would have surfaced, so probe each Step 6 target with `obsidian_get_note` before writing a new page. If `get_note` returns content, the response depends on the page kind: for Reference-style pages (where the page-template routing is "merge"), switch the write to a `get_note`+reconcile+overwrite merge instead of creating a duplicate; for snapshot-overwrite pages (the project root index, current-state pages), apply Step 7's content sanity-check before deciding to overwrite; for ADRs, the dated filename should already disambiguate, so the probe is just a safety net. If `get_note` returns not-found, the path is genuinely free. Don't escalate to a full halt unless Step 1's MCP-availability check would also now fail; a transient error on a single call shouldn't abort an otherwise-completable handoff.

## Step 4 — Walk the completeness checklist

Read `${CLAUDE_PLUGIN_ROOT}/skills/handoff/references/completeness_checklist.md` via the `Read` tool now, before proceeding. The checklist covers ten categories: project overview, current state, open tasks, open questions, decisions made this session, tech-stack changes, new/extended features, gotchas and dead ends, conventions learned, and next-session orientation — plus the rule for flagging CLAUDE.md-candidate items without modifying CLAUDE.md.

For each item in the loaded checklist, capture content from this session or write "nothing this session" — never fabricate, because the next session orients off this report and a fabricated item costs more than a missing one.

## Step 5 — Classify and route each captured item

For each item from Step 4:

- **Diátaxis category.** Pick one of the four (ADRs are Explanation).
- **New page vs. extend existing.** Apply the manual's split/merge rules. Only reuse an existing page when the Diátaxis category matches AND the topic matches AND the update cadence is similar. Use `obsidian_get_note` to peek at any existing page before deciding to extend or supersede — that's the same call Step 6's merge flow uses, so the read is reusable.
- **Use only the categories that actually apply.** Most of the manual's ~25-type catalog doesn't apply to single-developer repos — for a typical Claude Code project handoff, the relevant page types are: the project root index, feature/Reference pages, ADRs, How-to pages, learnings/gotchas, a tech-stack reference, and (only if the project is shareable) a Getting Started tutorial. Don't author a Stakeholder Register for a hobby project. The full applicability discussion lives in `page_template.md` (loaded in Step 6).
- **Filename and title.** Project root index uses the basename verbatim (no Title-Casing, dashes stay); sub-pages use descriptive Title Case with spaces; ADRs follow `ADR - YYYY-MM-DD - <decision>.md`. See `${CLAUDE_PLUGIN_ROOT}/skills/handoff/references/page_template.md` for the full conventions and write-call routing — load it in Step 6.

## Step 6 — Write each page

Read `${CLAUDE_PLUGIN_ROOT}/skills/handoff/references/page_template.md` via the `Read` tool now, before writing any page. It contains the page shape, the filename conventions per page kind (index / sub-page / ADR), the write-call routing (new / overwrite / append / merge / ADR), and the per-call Obsidian-failure handling. Apply the rules there to every page in this step.

## Step 7 — Update the project root index page

Path: `claude/<basename>/<basename>.md` (e.g. `claude/pgatzka-skills/pgatzka-skills.md`). The filename matches the project basename exactly so `pickup` can resolve it. Overwrite on every handoff — this is the snapshot, not a log.

**Before overwriting, sanity-check that the existing file at that path is actually a prior handoff index.** Call `obsidian_get_note` on the path. Distinguish three outcomes the same way pickup Step 3 does:

- **404 / not-found** (first handoff): proceed with the write.
- **Non-404 error** (MCP threw, permission denied, transient failure): stop and surface the error. Do *not* treat the error as "missing" and overwrite — a real index would be silently destroyed.
- **Succeeded**: continue to the content sanity-check below.

Content sanity-check (call succeeded, file exists): treat the file as a valid prior index if it contains **(`Current state` heading OR `Open tasks` heading) AND a `Pages in this project` (or equivalent links) section** — this is the exact same check pickup Step 3 runs, so a single file can't be classified differently on the two sides of the round-trip. If those markers are present, proceed with the overwrite. If they are missing, a same-named non-index note may be sitting there — ask the user via an `AskUserQuestion` call that complies with the `structured-questions` sister plugin. Compliant payload shape:

```jsonc
{
  "questions": [{
    "question": "A file already exists at the index path but doesn't look like a handoff index. What should I do?",
    "header": "Index collision",
    "options": [
      { "label": "Replace it (Recommended)",
        "description": "Pros: the index lands where pickup expects it; one canonical entry point for this project. Cons: the existing content at that path is overwritten — if it was something else you wanted to keep, it's gone." },
      { "label": "Write alongside under a new name",
        "description": "Pros: preserves the existing file. Cons: pickup looks at the basename path; the new index won't be found unless you rename one of them later." },
      { "label": "Abort the handoff",
        "description": "Pros: nothing is written; you can inspect the situation manually. Cons: the session's state isn't captured anywhere — running handoff later may have the same collision." }
    ]
  }]
}
```

This mirrors the defense `pickup` does on the read side and prevents silently destroying unrelated content.

Required sections (this is the **handoff↔pickup contract** — `pickup` Step 3 sanity-checks the file by looking for at least "Current state" or "Open tasks", plus "Pages in this project". If you rename or drop these section headings here, also update the matching check in `pickup/SKILL.md` Step 3 to keep the round-trip intact):

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
- Any per-page Obsidian errors hit (which page, which call, what to do next time).
- Anything flagged as a possible CLAUDE.md addition, with a recommended one-liner the user can paste in.

Then **stop**. Do not start new implementation work — the session is wrapping up.

## When in doubt

Re-read the relevant section of the manual or the skill references at `${CLAUDE_PLUGIN_ROOT}/skills/handoff/references/`. Default to splitting over merging; default to descriptive titles over short ones; default to writing the page over skipping — if it's not in Obsidian, the next session can't find it.
