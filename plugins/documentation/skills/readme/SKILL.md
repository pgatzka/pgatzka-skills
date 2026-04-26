---
name: readme
description: "Use whenever creating, updating, or considering adding content to a README.md file. Triggers on phrases like 'add to readme', 'update the readme', 'document this', 'what should the readme say', and on any edit to a README.md. Enforces a strict minimalism: a README has a title, a short description, and developer setup (Prerequisites / Install / Run) — nothing else by default. Claude/agent instructions, package structure, generated API docs, roadmaps, and tech-stack lists do NOT belong in a README. If Claude is about to update a README and none exists, the skill stops and asks the user before bootstrapping one."
---

# README

The job of a README is to help a developer who has *never seen this repo* get oriented and running on day one. Anything that doesn't serve that goal doesn't belong in the README — even if it's true, even if it's interesting, even if it's relevant to *some* reader.

The default answer to "should I add X to the README?" is **no**. Add only when the test passes (see the principle below).

## What belongs in a README

Three required sections, in this order:

### 1. Title

`# <project name>` as an H1. Match the directory name unless the user specifies otherwise.

### 2. Description

One paragraph (2–4 sentences). What this is, what problem it solves, who would use it. Plain prose, no marketing, no aspirations.

### 3. Developer setup

Three sub-sections, in this order:

- **Prerequisites** — tooling and versions a developer needs installed (e.g. *Node 20+, Postgres 16, JDK 21*). Be specific about versions; vague "Node" doesn't help anyone debug an incompatibility.
- **Install** — the one command that fetches dependencies. `npm install`, `mvn install`, `cargo build`, `make install` — whatever the project uses. Verify the command actually exists in the project before writing it.
- **Run** — the one command that starts the app or runs the tests. Verify it works.

If any of these has setup quirks (env vars to set, services to start before the first run, OS-specific steps), document them here — but only the *minimum* needed to get running. Save deeper config for when it's needed.

## What does NOT belong in a README

The principle: **does a developer who has never seen this repo need this on day one to get running?** If no, it's not for the README.

Concrete categories that fail that test:

- **Claude / agent instructions.** Belongs in `CLAUDE.md` (project-scoped) or `~/.claude/CLAUDE.md` (machine-scoped) — see the `persist-project-preferences` skill. The README is for humans onboarding, not for AI assistants.
- **Package structure / module layout / "where things live".** Changes too often. Anyone who needs to know where a file is reads the file tree, not the README.
- **Generated API documentation.** Belongs in the generated docs site or the source itself (Javadoc, JSDoc, rustdoc). Stale the moment you regenerate.
- **Roadmap / TODO / "coming soon".** Aspirational content that ages badly and adds noise without solving a day-one problem.
- **Tech stack / "built with" lists.** The manifest (`package.json`, `pom.xml`, `Cargo.toml`) is the source of truth; restating it in prose just creates two places that can disagree.
- **Internal incidents / postmortems / decision logs.** Not for the README.
- **Anything that lives elsewhere.** Contributing → `CONTRIBUTING.md`. Code style → `.editorconfig` or `STYLE.md`. Architecture diagrams → `docs/`. Changelog → `CHANGELOG.md`. Don't duplicate.

## What MIGHT belong (ASK before adding)

For some sections there's a real case. The default is still no, but they're not categorically out — ASK the user before adding any of these:

- **Usage / quick-start example** — only when the project has a public surface (a library someone calls, a CLI someone runs). Internal services don't need this.
- **License section** — only when the project is public *and* a one-line "Licensed under X — see LICENSE" actually adds something the LICENSE file alone doesn't.
- **CI / version badges** — only when meaningfully informative, never as decoration.

Don't volunteer these. Ask.

## Updating an existing README

When the user asks for an update:

1. **Read the existing README first.** Match its structure and voice.
2. **For the change being made, apply the principle.** "Does a day-one developer need this to get running?" If no, push back: "this looks like it belongs in CLAUDE.md / docs/ / nowhere — want me to skip it?"
3. **While you're in the file, scan for stale content** — but never delete silently:
   - Commands that reference files that don't exist (`make build` mentioned, no `Makefile` in the repo)
   - Paths that have moved
   - Sections describing removed features or changed APIs
   - Version numbers that have advanced
   For each suspected staleness, surface it: *"the README mentions `make build` but there's no Makefile here — suggest removing the line or updating to `npm run build`?"* and **ask** before deleting. No silent cleanup.
4. **Don't proactively add new sections** unless the user asks. If they're updating one specific thing, do that one thing.

## Creating a new README — ASK FIRST

If there is no `README.md` in the relevant directory and Claude is about to create one (because the task seems to require it, e.g. "document this" / "add a readme"), **stop and ask the user before creating it**.

The user might intentionally not have a README in that directory (subdirectories often don't need one; some private/internal projects deliberately don't ship a README). Don't auto-bootstrap.

If the user confirms — or invokes the `/readme-init` slash command — produce the minimum: title, description, Prerequisites/Install/Run. Nothing else, even if other content seems "nice to have."

## Quick reference

| Content | Where it goes |
|---|---|
| Project title, description, dev setup | `README.md` |
| Claude / agent rules and conventions | `CLAUDE.md` (use `persist-project-preferences`) |
| Package / module structure | Nowhere — read the file tree |
| API documentation | Generated docs site / source comments |
| Architecture diagrams, deeper docs | `docs/` |
| Changelog | `CHANGELOG.md` |
| Contributing guide | `CONTRIBUTING.md` |
| Code style | `.editorconfig`, linter config, or `STYLE.md` |
| Aspirational / roadmap content | Nowhere in the repo (use issues / a project board) |
