---
name: persist-project-preferences
description: This skill should be used whenever the user states a durable project-level preference, constraint, convention, or rule — phrases like "don't use X", "we don't use X in this project", "always use Y", "prefer Z over W", "we use <library/pattern/style>", "stick to <convention>", or any time the user agrees to "remember this" / "add this to memory" for the current codebase. The skill ensures the preference is written to the project's CLAUDE.md (which is committed to the repo and travels across machines) instead of only being saved to machine-local memory, so the constraint is preserved when the user works from a different machine, a new clone, or a teammate joins. Trigger this even when Claude Code's default reaction would be "okay, I'll remember that" — that default is insufficient because local memory does not sync. Do NOT trigger for one-off requests scoped to the current task ("rename this variable", "skip tests this time"), for personal/global preferences unrelated to the project (those belong in ~/.claude/CLAUDE.md), or for ephemeral chat-only context.
---

# Persist Project Preferences to CLAUDE.md

## Why this skill exists

Claude Code's default response to "I don't want to use JPA in this project" or similar is often "Got it, I'll remember that" — saved to local memory only. That memory does not travel: a different machine, a fresh clone, or a teammate gets none of it. The fix is to write durable project preferences into the repo's `CLAUDE.md`, which **is** committed and **does** travel.

This skill makes that the default behavior for project-level preferences.

## When to apply

Trigger when the user expresses a **durable, project-scoped** rule. Signals include:

- Negative constraints: "don't use JPA", "no Lombok", "avoid Mockito", "we're not using Redux here"
- Positive conventions: "always use constructor injection", "prefer Result types over exceptions", "use kotlinx.serialization, not Jackson"
- Stack/tooling decisions: "this project uses pnpm, not npm", "we deploy with Fly.io", "Postgres only, no ORM"
- Style/architecture rules: "hexagonal architecture", "no static utility classes", "tests go next to source files"
- Explicit memory cues: "remember this for this project", "add this to memory", "don't forget"

Do **not** trigger for:

- Single-task requests ("for this PR, skip the tests")
- Personal global preferences not tied to the project (those go in `~/.claude/CLAUDE.md`, not the repo's `CLAUDE.md`)
- Information that's already obvious from the codebase (e.g. the language) unless the user is explicitly stating it as a rule

## What to do

### 1. Locate or create CLAUDE.md

Look for `CLAUDE.md` at the repository root (the directory containing `.git`, or the working directory if git is not present). If it exists, read it. If it does not exist, create it with a minimal header:

```markdown
# Project Instructions for Claude

This file is read by Claude Code at session start. It captures durable project conventions, constraints, and preferences. Edit freely; commit changes so they travel across machines and teammates.
```

### 2. Choose or add the right section

**Match the existing structure first.** If the file already has a section the new entry fits — `## Database`, `## API style`, `## Testing`, whatever the user has organized — use it. Don't impose new headings on a file the user has already shaped.

Only when the file is new, or no existing section is a clean match, use this default set (creating any that don't yet exist):

- `## Tech Stack` — languages, frameworks, package managers, databases that are in use
- `## Conventions` — positive rules ("always do X", "prefer Y")
- `## Constraints` — negative rules ("don't use X", "no Z")
- `## Architecture` — structural decisions (layering, module boundaries)
- `## Workflow` — how to build, test, run, deploy

If the new preference doesn't fit any existing section cleanly *and* none of the defaults fit either, prefer `## Constraints` for "don't" rules and `## Conventions` for "do" rules — but a one-off custom heading is also fine when the topic is genuinely its own thing.

### 3. Write the entry

**Style:** one line, imperative phrasing or a clear factual statement. No multi-line entries; if the rule is too big for one line, split it into multiple atomic entries.

**Reason in parens:** include a short rationale in parentheses when the user gave one. Reasons aren't required, but they help future-you (and future Claude sessions) judge whether the rule still applies — when the original incident or constraint is forgotten, a bare rule is harder to maintain than one that says *why*.

**Position in the section:** append to the **bottom** of the section. Don't re-sort or re-cluster existing entries — diff churn for no value, and it makes `git blame` lie about when each rule was added. Newest at the bottom is fine.

Good:
- `- Do not use Spring Data JPA. Use JDBC + jOOQ instead. (Avoiding hidden N+1 queries and lazy-loading surprises.)`
- `- Package manager: pnpm. Do not use npm or yarn.`
- `- Tests live next to source files as \`*.test.ts\`, not in a separate \`tests/\` tree.`

Avoid:
- Vague entries: "be careful with the database"
- Restating obvious code facts: "this project uses TypeScript" (when `tsconfig.json` is right there) — unless the user explicitly stated it as a rule
- Multi-paragraph entries — split into multiple bullets instead

### 4. Confirm with the user

After editing, briefly tell the user what was added and where, so they can review and commit. Example:

> Added to `CLAUDE.md` under **Constraints**:
> - Do not use Spring Data JPA. Use JDBC + jOOQ instead.
>
> Commit this so it persists across machines.

Do not commit the change yourself unless the user asks — they may want to review or batch it with other work.

### 5. If local memory was also updated

If you also wrote the preference to local memory (via the standard memory mechanism), that's fine — local memory provides faster recall within the session. But `CLAUDE.md` is the source of truth, and if the two ever disagree, `CLAUDE.md` wins.

## Edge cases

- **User contradicts an earlier rule.** Don't silently overwrite. Show the existing entry and ask: "replace this with the new rule, or remove the old one entirely?" The default action is **replace** — most contradictions mean the user has changed their mind and the new rule supersedes the old. Removal (no replacement) is a separate decision worth asking about explicitly. Don't keep both with strikethrough or "deprecated" notes — the file is for current rules, not history.
- **Monorepo with multiple `CLAUDE.md` files.** Place the rule in the most specific `CLAUDE.md` that applies (e.g. `services/api/CLAUDE.md` for an API-only rule, root `CLAUDE.md` for a repo-wide rule). Ask if it's ambiguous.
- **No git repo.** Still create `CLAUDE.md` in the working directory and mention to the user that the file lives with whatever they sync (Dropbox, etc.) — the persistence guarantee comes from version control, not from the file itself.
- **User says "actually, just remember this for me, not the project."** Honor that — write to local memory or `~/.claude/CLAUDE.md`, not the project `CLAUDE.md`.

## Quick reference

| User says | Where it goes |
|---|---|
| "Don't use JPA in this project" | Project `CLAUDE.md` → Constraints |
| "We use pnpm here" | Project `CLAUDE.md` → Tech Stack |
| "I always prefer tabs over spaces" (general) | `~/.claude/CLAUDE.md` |
| "For this PR, skip the integration tests" | Neither — task-scoped |
