---
description: Start a new session by reading the project's Obsidian vault notes (handoff.md + memory.md) plus the repo's CLAUDE.md, then verify understanding before doing any work. Falls back to a fresh-start orientation when no handoff note exists.
---

# /session-pickup

## Step 1 — locate the vault folder

Read the repo's `CLAUDE.md` for the project's vault folder path. By convention it's a one-line entry, for example:

> Claude vault folder: `claude/pgatzka-skills`

**If the entry is missing** → fresh-start mode. The vault may not have been set up for this project yet. Continue to step 2 with no vault data, and surface this in the orientation so the user knows the next `/session-handoff` will ask for a folder path.

**If the `obsidian` MCP isn't available** → tell the user and stop. Don't guess at file locations and don't fall back to local files; the vault is the source of truth.

## Step 2 — read what exists

Read these in order. Don't error on missing notes — note them and continue:

1. `<vault-folder>/handoff.md` via `obsidian_get_note`.
2. `<vault-folder>/memory.md` via `obsidian_get_note`.
3. The repo's `CLAUDE.md`.

## Step 3 — pick the right mode

**If `handoff.md` exists in the vault** → continuing-session mode. Go to step 4.

**If `handoff.md` does not exist** → fresh-start orientation:

- Tell the user explicitly: *"No handoff note found at `<vault-folder>/handoff.md`. Either this is the first session in this repo, or no one has run `/session-handoff` yet."* (If the vault folder entry was missing from `CLAUDE.md`, say that instead.)
- Summarize anything found in `memory.md` and `CLAUDE.md`. If both are also missing or empty, say so.
- Ask the user what they want to work on.
- **Stop here.** Don't go to step 4.

## Step 4 — verify understanding (continuing-session mode only)

Before doing anything else, tell the user, in your own words:

1. What this project is and what state it's in.
2. What the next task is and what "done" looks like for it.
3. Any open questions or decisions that are blocking progress.
4. Anything in the handoff that's unclear, looks stale, or seems contradictory.

**Then stop.** Do not read any other files. Do not start working. Wait for the user's confirmation before any further action.

The point of this gate is catching misalignment between what's in the handoff and what's actually true. Skipping it defeats the purpose. Don't ask *"shall I proceed?"* — wait for the user to say *"yes, that matches"* (or to correct the misunderstandings). Their confirmation is the trigger to start work.
