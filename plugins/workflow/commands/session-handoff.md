---
description: Capture session state into HANDOFF.md, CLAUDE.md (via the persist-project-preferences skill), and the project memory file before ending the session. Overwrites HANDOFF.md on each invocation; gitignores it the first time per project.
---

# /session-handoff

We're wrapping up this session. Capture everything the next session will need to continue this work effectively.

Do these four steps, in this order. Each step is independent — if there's nothing meaningful to record at a given step, skip it and say so in the final report.

## 1. Write `HANDOFF.md` at the repo root (overwrite)

Always overwrite. This file is a snapshot of the *current* session state, not an append log; the latest handoff supersedes the previous one.

Include:

- **Current state** — what's implemented and working, what's implemented but untested, what's stubbed or incomplete.
- **Architecture decisions** made in this session and the reasoning behind them, including alternatives considered and rejected.
- **Bugs, gotchas, and dead ends** hit during the session — with enough detail that a fresh session won't re-hit them. Include specific error messages, root causes, and fixes.
- **Key file paths, function names, API contracts** that matter for the next steps.
- **Next tasks** in priority order, with acceptance criteria for each.
- **Open questions or decisions** the user still needs to make.

Be specific and concrete. Prefer code references over prose. The job of this document is to make the next session productive from turn one — not to be readable as a narrative.

### Gitignore on first creation

If `/HANDOFF.md` is not yet listed in the repo's `.gitignore`, add it. Follow the `gitignore` skill's rules: leading `/`, no comment, alphabetical placement in the files block. Tell the user what you added and confirm before writing. HANDOFF.md is personal session state and shouldn't be committed by default.

## 2. Update `CLAUDE.md` — via the `persist-project-preferences` skill

Anything *durable* learned this session — facts true about the project regardless of which task is active (stack, conventions, where things live, testing approach, commands to run common tasks, rules the codebase follows) — belongs in `CLAUDE.md`.

**Use the `persist-project-preferences` skill** for the actual edit. That skill handles section matching, append-to-bottom ordering, bullet style, and replace-on-conflict. Don't reinvent any of that here. The handoff command's job at this step is only to identify *what* in this session warrants persisting and hand it off.

Do not put session-specific state in `CLAUDE.md` — that's HANDOFF.md's job.

If nothing durable was learned this session, skip this step and say so in the final report.

## 3. Update the project memory file

Path: `~/.claude/projects/<slug>/memory/MEMORY.md`, where `<slug>` is the current working directory with each `/` replaced by `-` (e.g. cwd `/home/philg/projects/skills` → slug `-home-philg-projects-skills` → full path `~/.claude/projects/-home-philg-projects-skills/memory/MEMORY.md`).

**Compute the slug from the actual `cwd`** — do not hardcode a path. If the directory doesn't exist yet, create it.

Append the **highest-signal, most-durable learnings** from this session — the kind of thing worth injecting into every future session on this project. Keep entries short, factual, one-line each. Merge with existing content; don't overwrite.

If nothing this session warrants a memory entry, skip.

## 4. Report

List the files you changed (or skipped, with the reason) and give the user a one-line summary of each. Then **stop** — don't start new work.
