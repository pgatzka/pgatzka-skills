---
description: Start a new session by reading handoff docs and verifying understanding before doing any work. Falls back to a fresh-start orientation when no HANDOFF.md exists.
---

# /session-pickup

## Step 1 — read what exists

Attempt to read each of these files in order. Don't error on missing files — note them and continue:

1. `HANDOFF.md` at the repo root.
2. `CLAUDE.md` at the repo root.
3. The project memory file at `~/.claude/projects/<slug>/memory/MEMORY.md`, where `<slug>` is the current working directory with each `/` replaced by `-` (e.g. cwd `/home/philg/projects/skills` → slug `-home-philg-projects-skills`). Compute from the actual `cwd`; do not hardcode.

## Step 2 — pick the right mode

**If `HANDOFF.md` exists** → continuing-session mode. Go to step 3.

**If `HANDOFF.md` does not exist** → fresh-start orientation:

- Tell the user explicitly: *"No HANDOFF.md found at the repo root. Either this is the first session in this repo, or no one has run `/session-handoff` yet."*
- Summarize anything found in `CLAUDE.md` and the project memory file. If both are also missing or empty, say so.
- Ask the user what they want to work on.
- **Stop here.** Don't go to step 3.

## Step 3 — verify understanding (continuing-session mode only)

Before doing anything else, tell the user, in your own words:

1. What this project is and what state it's in.
2. What the next task is and what "done" looks like for it.
3. Any open questions or decisions that are blocking progress.
4. Anything in the handoff that's unclear, looks stale, or seems contradictory.

**Then stop.** Do not read any other files. Do not start working. Wait for the user's confirmation before any further action.

The point of this gate is catching misalignment between what's in the handoff and what's actually true. Skipping it defeats the purpose. Don't ask *"shall I proceed?"* — wait for the user to say *"yes, that matches"* (or to correct the misunderstandings). Their confirmation is the trigger to start work.
