---
name: pickup
description: This skill should be used at the start of a fresh Claude Code session, after a context reset, on the first message of a new conversation in a project with prior handoffs, after `/compact` or `/clear`, on a new machine or fresh clone, after a long gap returning to a project with a populated `claude/<basename>/` folder, or whenever the user says things like "where were we", "catch me up", "pick up where we left off", "what's the status", "what was I working on", "what was I stuck on", "where did I leave off", "what's next", "what's the plan", "what's the todo", "what's on the docket", "what's left", "any blockers", "what's blocking me", "remind me", "fill me in", "continue from yesterday", "resume", "continue", "back to it", "back at it", "let's keep going", "ok, continuing", "recap", "refresh me", "status update", "any context", "summary please", "what did we do last time", "what's new", "what changed since last time", "did we finish X?", or invokes `/session-management:pickup` directly. Also fire on bare greetings ("hi", "hey", "morning", "back", "I'm back") when a prior handoff exists in the project's Obsidian folder — the greeting is most likely a resume signal. Also fire when the user references a prior conversation or decision implying continuity ("yesterday we decided…", "last time you said…"). It reads the project's Obsidian folder, briefs the user on current state, open tasks, open questions, and recent decisions, then waits for direction.
allowed-tools: Read, Bash, AskUserQuestion, mcp__obsidian__obsidian_list_notes, mcp__obsidian__obsidian_get_note, mcp__obsidian__obsidian_search_notes
---

# /session-management:pickup

Load the project's Obsidian knowledge base and brief the user on where the work stands, then stand by for direction.

## Step 0 — Hold these conventions

Pickup is read-only orientation; it does not author new pages. The five conventions below are everything pickup needs from the documentation manual:

- Diátaxis categorizes every page as Tutorial / How-to / Reference / Explanation (ADRs are Explanation).
- Index pages exist at each level of the hierarchy; the project root index lives at the path stated in Step 3 and is overwritten on each handoff.
- ADRs follow `ADR - YYYY-MM-DD - <decision>.md`, sortable by the embedded date.
- Page filenames are descriptive Title Case with spaces (except the project root index, which is the basename verbatim).
- Pages carry an `updated`/`owner` frontmatter and a one-or-two-sentence purpose statement at the top of the body.

The full manual lives at `${CLAUDE_PLUGIN_ROOT}/references/documentation_tutorial_manual.md` if deeper detail is needed — e.g. for an unusual page-shape question during the brief. Don't load it as a routine step; the conventions above cover the read path.

## Step 1 — Verify the Obsidian MCP is connected

Look for `mcp__obsidian__*` tools. If they are absent, stop and tell the user — there is nothing to pick up from without Obsidian access. Do not fabricate context from CLAUDE.md or guesses, because a fabricated handoff brief is worse than admitting there isn't one: the user acts on it as if it were true.

## Step 2 — Determine the project's vault folder

Convention: `claude/<cwd-basename>`. Get the basename via `Bash` (e.g. `basename "$PWD"`) and use that.

## Step 3 — Read the project root index page

Call `obsidian_get_note` on `claude/<basename>/<basename>.md` — the project root index, overwritten on every handoff to reflect current state.

Distinguish three error shapes:

- **Index file legitimately does not exist (404 / not-found).** Continue to the recovery branch below.
- **`obsidian_get_note` errors for a non-404 reason (MCP threw, permission denied, etc.).** Stop and surface the error. Do *not* assume the index is missing — a transient MCP error would cascade into the recovery branch and risk overwriting real state.
- **Call succeeded.** Sanity-check the returned content: it should contain the index sections that handoff writes (looks like an index — at minimum a "Current state" or "Open tasks" heading, plus a "Pages in this project" or similar links section). These markers are the **handoff↔pickup contract** — see `handoff/SKILL.md` Step 7 for the full required-sections list. If you change this check, also update handoff to keep the round-trip intact. If the page is missing these markers, a same-named non-index note may be sitting at that path. Tell the user the file exists but doesn't look like a handoff index, and route to the recovery branch to ask what to do. Otherwise proceed to Step 4.

Recovery branch (index legitimately not found):

- Call `obsidian_list_notes` on the project folder.
- Use `AskUserQuestion` to ask how to proceed. The call must satisfy the `structured-questions` sister plugin's rules (one option ending with `(Recommended)`, literal `Pros:`/`Cons:` per option); otherwise its PreToolUse hook will deny. Compliant payload shape for the empty-folder case:

```jsonc
{
  "questions": [{
    "question": "This project has no prior handoff in Obsidian. How should the session start?",
    "header": "First-run",
    "options": [
      { "label": "Start fresh (Recommended)",
        "description": "Pros: zero assumptions; user drives the next move directly. Cons: any prior context that lives outside Obsidian gets ignored." },
      { "label": "Build a first index from spoken intent",
        "description": "Pros: captures whatever the user describes right now as the new project baseline. Cons: spends a turn on setup before any real work happens." }
    ]
  }]
}
```

For the **folder-has-notes-but-no-index** sub-case, use the same payload shape: exactly one option ending with `(Recommended)`, and each option's `description` containing literal `Pros:` and `Cons:` lines (the structured-questions hook applies here too — copy the empty-folder example's format, not just its option labels). Options like `Treat folder as orphan and start fresh (Recommended)` / `Describe the existing pages so I can summarize them (no writes)` / `Switch to /session-management:handoff to build an index`. Pickup is read-only — it cannot construct the index itself; if the user wants one built, the recommended path is `/session-management:handoff`.

## Step 4 — Brief the user

Summarize from the index page, in this order, in under 250 words total:

1. **What this project is** — purpose + tech-stack one-liner.
2. **Where the work stands right now** — current-state paragraph from the index.
3. **Open tasks** — priority-ordered list.
4. **Open questions** — what the user needs to decide before progress unblocks.
5. **Most recent decisions** — top 3 ADRs by date, with a one-line context each. The index links ADRs under "Decisions". If the index summaries are too brief, fall through this chain:
    1. **Preferred:** call `obsidian_list_notes` with `nameRegex: "^ADR - "` if the MCP supports it.
    2. **Fallback:** call `obsidian_list_notes` without a filter and select entries whose names start with `ADR - ` in code.
    3. Sort the returned entries by the YYYY-MM-DD substring embedded in the filename to find the latest, then read the top entries with `obsidian_get_note`.

    If no ADRs exist for this project (the "Decisions" section is empty or absent), omit this bullet from the brief rather than printing an empty heading.
6. **Suggested next move** — usually the top open task or the highest-priority open question.

The user should be able to scan the brief in under thirty seconds. Lead with the highest-impact items; do not pad.

Example brief shape:

```
**Project:** pgatzka-skills — personal Claude Code plugin marketplace (Node/Python tooling, plugin manifests).
**Current state:** Two plugins shipped (structured-questions, session-management). Last handoff added the hook deny-recovery section.
**Open tasks:**
- Add SessionEnd hook to auto-suggest handoff (high)
- Wire `_smoketest.py` out of the shipped tree (medium)
**Open questions for you:**
- Should the doc manual move to a global cross-project location?
**Recent decisions:**
- 2026-05-13 — Use Python (not bash) for the AskUserQuestion validator hook.
- 2026-05-12 — Bootstrap fresh marketplace; prior content lives in `backup/`.
**Suggested next move:** the top open task — `Add SessionEnd hook to auto-suggest handoff`. Want to start there?
```

Match this shape but adapt the content to what the index actually says.

## Step 5 — Stand by

After the brief, **stop and wait** for the user to direct the session. Do not start the top task autonomously — confirm intent first. The handoff captured what *was*; the user decides what happens *next*.

When asking the user what to start with, route the question through `AskUserQuestion` — the `structured-questions` sister plugin will enforce the structural rules (see its hook contract; same rules as Step 3's recovery branch above).

## When the user wants deeper context

If the user picks a topic that needs more than the index summarizes:

- Drill into the relevant sub-page: `obsidian_get_note` on the descriptive-titled page from the index's "Pages in this project" section.
- Search across the folder for a term: `obsidian_search_notes` with the topic as the query.
- Look at ADRs for the reasoning behind a particular shape: `obsidian_list_notes` filtered to `ADR - *.md`.

Stay read-only during pickup. Any new writes belong in a `/session-management:handoff` at the end of the session, not now.
