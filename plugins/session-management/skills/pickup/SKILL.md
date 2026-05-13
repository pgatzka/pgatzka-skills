---
description: Slash command `/session-management:pickup`. Bootstrap a fresh Claude Code session by reading the project's Obsidian folder, briefing the user on current state, open tasks, open questions, and recent decisions, then waiting for direction. Use at session start, after a context reset, or whenever the user invokes the command.
argument-hint: "[optional focus area]"
allowed-tools: Read, Bash, mcp__obsidian__obsidian_list_notes, mcp__obsidian__obsidian_get_note, mcp__obsidian__obsidian_search_notes
---

# /session-management:pickup

Load the project's Obsidian knowledge base and brief the user on where the work stands. Do not start any implementation work until the user confirms the next move.

## Step 0 — Skim the documentation manual (if not already loaded)

Read `${CLAUDE_PLUGIN_ROOT}/references/documentation_tutorial_manual.md` (bundled with this plugin) if it has not already been loaded this session. The manual defines what shape the Obsidian pages are in (Diátaxis categories, index conventions, ADR format) so navigation makes sense. If the manual is already in context, skip this step.

## Step 1 — Verify the Obsidian MCP is connected

Look for `mcp__obsidian__*` tools. If they are absent, stop and tell the user — there is nothing to pick up from without Obsidian access. Do not fabricate context from CLAUDE.md or guesses.

## Step 2 — Determine the project's vault folder

Convention: `claude/<cwd-basename>`. Get the basename via `Bash` (e.g. `basename "$PWD"`) and use that.

## Step 3 — Read the project root index page

Call `obsidian_get_note` on `claude/<basename>/<basename>.md` — the project root index, overwritten on every handoff to reflect current state.

If the index page does not exist:

- Call `obsidian_list_notes` on the project folder.
- If the folder is empty, tell the user this project has never been handed off and offer to either start fresh (proceed with no prior context) or build a first index from the user's spoken intent.
- If the folder has notes but no index, offer to construct one by reading the existing pages.

## Step 4 — Brief the user

Summarize from the index page, in this order, in under 250 words total:

1. **What this project is** — purpose + tech-stack one-liner.
2. **Where the work stands right now** — current-state paragraph from the index.
3. **Open tasks** — priority-ordered list.
4. **Open questions** — what the user needs to decide before progress unblocks.
5. **Most recent decisions** — top 3 ADRs by date, with a one-line context each (read the ADR pages via `obsidian_get_note` if the index summarizes them too briefly).
6. **Suggested next move** — usually the top open task or the highest-priority open question.

The user should be able to scan the brief in under thirty seconds. Lead with the highest-impact items; do not pad.

## Step 5 — Stand by

After the brief, **stop and wait** for the user to direct the session. Do not start the top task autonomously — confirm intent first. The handoff captured what *was*; the user decides what happens *next*.

When asking the user what to start with, route the question through the `structured-questions` skill if available (multiple options with Pros/Cons, a Recommended choice, Other always available).

## When the user wants deeper context

If the user picks a topic that needs more than the index summarizes:

- Drill into the relevant sub-page: `obsidian_get_note` on the descriptive-titled page from the index's "Pages in this project" section.
- Search across the folder for a term: `obsidian_search_notes` with the topic as the query.
- Look at ADRs for the reasoning behind a particular shape: `obsidian_list_notes` filtered to `ADR - *.md`.

Stay read-only during pickup. Any new writes belong in a `/session-management:handoff` at the end of the session, not now.
