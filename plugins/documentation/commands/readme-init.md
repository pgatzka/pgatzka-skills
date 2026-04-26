---
description: Bootstrap a minimal README.md (title, description, Prerequisites / Install / Run). Refuses to overwrite an existing README; asks when detection is ambiguous.
argument-hint: [optional path]
---

# /readme-init

Create a new minimal README at the target location, following the `readme` skill's rules. This command is the explicit way to bootstrap a README — outside this command, the `readme` skill stops and asks before creating one.

## Scope

- If the user passed an argument, treat it as the target file or directory (default file name: `README.md`).
- Otherwise create `README.md` at the **repo root** — the directory containing `.git`, or the current working directory if no `.git` is present.

## Pre-flight check

If a `README.md` already exists at the target path, **stop**. Show the user what's already there (a short excerpt is fine) and ask:

1. *Edit the existing one* (defer to the `readme` skill — recommended)
2. *Overwrite with a fresh minimal scaffold*
3. *Cancel*

Default to (1). Never silently overwrite an existing README.

## Content

Produce exactly the three required sections from the `readme` skill — and nothing else.

### 1. Title

`# <project name>` as the first line. Use:

- the value from `package.json` `name`, `pyproject.toml` `[project] name`, `Cargo.toml` `[package] name`, or the equivalent for the detected toolchain, OR
- the directory name if no manifest is found.

If multiple manifests exist (polyglot repo) or the detected name looks generated/wrong, ASK using the `ask-user-questions` skill.

### 2. Description

One paragraph, 2–4 sentences. What this is, what problem it solves, who would use it.

If the user hasn't given a description and there isn't an obvious one in the manifest (`package.json` `description`, `pyproject.toml` `description`, etc.), **ASK** for it via `ask-user-questions` before generating placeholder text. Don't invent.

### 3. Developer setup

Three sub-sections in this order:

- `### Prerequisites` — tooling and versions
- `### Install` — the dependency-fetch command
- `### Run` — the one command to start the app or run the tests

Detect the toolchain from manifest files in the repo:

| Manifest | Toolchain | Likely Install / Run |
|---|---|---|
| `package.json` | Node | `npm install` (or `pnpm install` / `yarn install` based on `packageManager` field or lockfile) / `npm run dev` (or whatever script `start`/`dev` resolves to) |
| `pom.xml` | Maven | `mvn install` / `mvn spring-boot:run` (or the project's run command — verify) |
| `build.gradle` / `build.gradle.kts` | Gradle | `./gradlew build` / `./gradlew bootRun` (or the project's main task) |
| `Cargo.toml` | Rust | `cargo build` / `cargo run` |
| `pyproject.toml` (poetry) | Python / Poetry | `poetry install` / `poetry run <entry>` |
| `pyproject.toml` (uv) | Python / uv | `uv sync` / `uv run <entry>` |
| `requirements.txt` (only) | Python / pip | `pip install -r requirements.txt` / `python <entry>` |
| `Gemfile` | Ruby | `bundle install` / `bundle exec <entry>` |
| `go.mod` | Go | `go mod download` / `go run .` |
| `Makefile` (with `install` / `run` / `dev` targets) | Make-orchestrated | `make install` / `make run` |

When detection is ambiguous (multiple manifests with no clear primary, exotic toolchain, or the run command isn't obvious), **ASK** rather than guess.

For Prerequisites, infer versions from constraints in the manifest where possible — `engines.node` in `package.json`, `<java.version>` in `pom.xml`, `rust-version` in `Cargo.toml`, `[tool.poetry.dependencies] python` in `pyproject.toml`, etc. If no version is pinned anywhere, leave a TODO and tell the user.

When you can't fill a value with confidence, write `<!-- TODO: ... -->` in place of the missing piece and surface every TODO in the post-write report.

## Don't include

Per the `readme` skill, the initial scaffold contains **only** the three required sections. Do not add:

- License section
- Usage / quick-start examples
- CI / version badges
- "Built with" / tech-stack list
- Architecture / package structure
- Roadmap / TODO sections
- Claude / agent instructions
- Anything else "while we're here"

If the user wants any of those, that's a follow-up via the regular `readme` skill flow with an explicit ask.

## After writing

Tell the user:

1. **Where the file landed** (full path).
2. **Which sections were filled from detection vs. left as `<!-- TODO: ... -->`** — list each TODO so they're visible.
3. **A short reminder** that anything beyond the three sections is opt-in and the `readme` skill will ask before adding.

Don't commit the file. The user reviews and commits when ready.
