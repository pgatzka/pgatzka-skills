---
description: Capture session state into the project's Obsidian vault folder — handoff.md (overwrite) and memory.md (merge) — plus durable rules into the repo's CLAUDE.md via the persist-project-preferences skill. Reads the vault folder from CLAUDE.md; asks once and persists if not yet set.
---

# /session-handoff

We're wrapping up this session. Capture everything the next session will need to continue this work effectively.

The project's persistent Claude-facing notes live in the user's Obsidian vault, accessed via the `obsidian` MCP server. The repo's `CLAUDE.md` still holds durable instructions to Claude — it auto-loads at session start, which the vault can't replace — but session state and learnings go to the vault so they sync across machines.

Do these steps in order. If there's nothing meaningful at a step, skip it and say so in the final report.

## 1. Locate the project's vault folder

Read the repo's `CLAUDE.md` for the project's vault folder path. By convention it's recorded as a one-line entry, for example:

> Claude vault folder: `claude/pgatzka-skills`

**If the entry exists** → use that path for the rest of the steps.

**If the entry does not exist** → ASK the user once for the folder path. Suggest `claude/<repo-basename>` as the default (e.g. cwd `G:\projects\pgatzka-skills` → `claude/pgatzka-skills`). Once they confirm, persist the value to the repo's `CLAUDE.md` via the `persist-project-preferences` skill **before** writing any vault notes. Do not invent a path silently — the user owns the vault and decides where Claude's notes live.

**If the `obsidian` MCP is not available** in this session → stop and tell the user. Don't fall back to writing local files; the whole point of the vault is cross-machine sync, and a local fallback would silently defeat that.

## 2. Write `handoff.md` in the vault folder (overwrite)

Use `obsidian_write_note` to write `<vault-folder>/handoff.md`. Always overwrite — this note is a snapshot of the *current* session state, not an append log; the latest handoff supersedes the previous one.

Frontmatter for retrieval:

```yaml
---
project: <repo-basename>
type: claude-handoff
updated: <YYYY-MM-DD>
---
```

Body should include:

- **Current state** — what's implemented and working, what's implemented but untested, what's stubbed or incomplete.
- **Architecture decisions** made in this session and the reasoning behind them, including alternatives considered and rejected.
- **Bugs, gotchas, and dead ends** hit during the session — with enough detail that a fresh session won't re-hit them. Include specific error messages, root causes, and fixes.
- **Key file paths, function names, API contracts** that matter for the next steps.
- **Next tasks** in priority order, with acceptance criteria for each.
- **Open questions or decisions** the user still needs to make.

Be specific and concrete. Prefer code references over prose. The job of this note is to make the next session productive from turn one — not to be readable as a narrative.

## 3. Update `CLAUDE.md` — via the `persist-project-preferences` skill

Anything *durable* learned this session — facts true about the project regardless of which task is active (stack, conventions, where things live, testing approach, commands to run common tasks, rules the codebase follows) — belongs in the repo's `CLAUDE.md`.

**Use the `persist-project-preferences` skill** for the actual edit. That skill handles section matching, append-to-bottom ordering, bullet style, and replace-on-conflict. Don't reinvent any of that here. The handoff command's job at this step is only to identify *what* in this session warrants persisting and hand it off.

Do not put session-specific state in `CLAUDE.md` — that's `handoff.md`'s job.

If nothing durable was learned this session, skip this step and say so in the final report.

## 4. Update `memory.md` in the vault folder (merge)

Path: `<vault-folder>/memory.md`. This note holds the **highest-signal, most-durable learnings** about the project — the kind of thing worth injecting into every future session.

Use `obsidian_append_to_note` to add new entries. If a merge or de-duplication is needed (the new entry contradicts or supersedes an existing one), use `obsidian_get_note` to read first, then `obsidian_write_note` to rewrite.

Keep entries short, factual, one line each. A dated subsection (`## 2026-05-07`) is fine when entries are time-bounded; raw bullets under a single heading are fine when they're timeless.

If nothing this session warrants a memory entry, skip.

## 5. Report

List the notes you wrote (or skipped, with the reason) and give the user a one-line summary of each. Then **stop** — don't start new work.
