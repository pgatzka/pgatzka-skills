# Project Instructions for Claude

This file is read by Claude Code at session start. It captures durable project conventions, constraints, and preferences. Edit freely; commit changes so they travel across machines and teammates.

This repo is a personal Claude Code plugin marketplace. Layout follows the standard marketplace convention: `.claude-plugin/marketplace.json` at the root listing plugins; each plugin in `plugins/<name>/` with its own `.claude-plugin/plugin.json`, `skills/<name>/SKILL.md`, optional `commands/<name>.md`. Marketplace name is `pgatzka-plugins`; GitHub repo is `pgatzka/skills`.

## Conventions

- Skill writing style is "should + reasoning", not "MUST". Heavy MUSTs are a yellow flag — explain the *why* so the model can apply judgment to edge cases.
- Always include a "Recommended" option (with the *why* in the description) when calling AskUserQuestion. Don't present neutral menus that hide which option is the sensible default.
- Plugins group skills by domain (`java-development`, `sql-development`, `documentation`, etc.), not one-skill-per-plugin.
- Bullet style in CLAUDE.md and other authored docs: imperative or factual one-liner per bullet, optional reason in parentheses.

## Constraints

- Manifests (`marketplace.json`, `plugin.json`) do **not** carry `version` fields. Git commit SHA is the version of record.
- Skill files are non-executable (mode 100644). If a file gets dropped at the repo root with `mv` from an executable source, fix the mode before committing.
- Don't decide things on the user's behalf — when something isn't fully specified, ASK via the `ask-user-questions` skill convention. The user prefers being asked rather than getting "reasonable defaults", even on small details.

## Workflow

- Don't commit unless the user explicitly asks ("add and commit", "commit it", etc.). Show staged changes and wait for explicit approval.
- Don't push to `origin` without explicit ask either. The user runs `git push`.
- Commit messages: imperative title (under ~70 chars). Optional body with bullet points wrapped to ~72 chars. Body explains *why* and *what changed*, not just file lists.
- After non-trivial work, run the post-task doc-check from the `readme` and `wiki` skills: surface specific README/wiki edits the change implies and ask before writing.
