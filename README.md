# pgatzka-plugins

A personal [Claude Code](https://docs.claude.com/en/docs/claude-code) plugin marketplace — skills and tools I use across my own projects, packaged so I can install them on any machine with one command and so anyone else can grab them too.

## Install the marketplace

In Claude Code:

```
/plugin marketplace add pgatzka/skills
```

(Replace with the actual GitHub `owner/repo` once published. Local path also works: `/plugin marketplace add /absolute/path/to/this/repo`.)

Then install whichever plugins you want:

```
/plugin install java-development@pgatzka-plugins
```

## Plugins

| Plugin | What it does |
|---|---|
| [`build-tools`](plugins/build-tools) | Build-tool conventions: don't build unless required, never check in generated code, run the minimum invocation the goal needs. Tool-agnostic core with per-tool notes for Maven, Gradle, npm/pnpm/yarn, Cargo, Go. |
| [`ci-cd`](plugins/ci-cd) | CI/CD pipeline conventions. Core principle: DRTT — Don't Run Things Twice. Build once, consume the artifact in downstream jobs. Plus pinning, least-privilege permissions, secrets discipline, fail-fast parallelism, every-step-has-a-verdict, concurrency, timeouts, OIDC, reproducibility. Per-platform notes for GitHub Actions, GitLab CI, Jenkins, CircleCI. |
| [`logging`](plugins/logging) | Language-agnostic logging conventions: real logger over stdout, parameterized messages, sensible levels, expensive-computation guards, no sensitive data, structured output in production, correlation/trace IDs, audit vs. operational separation, sampling. Per-language notes for Java/Kotlin (defers to `java-logging`), Python, JS/TS, Go. |
| [`git`](plugins/git) | Git workflow skills. Currently: `gitignore` (minimal, anchored, alphabetically-sorted entries — no speculative bulk-adds). |
| [`java-development`](plugins/java-development) | Java engineering skills: `java-logging` (structured SLF4J, sensible levels, no sensitive data, no stack traces at ERROR), `javadoc` (don't state the obvious, all-or-nothing, ask before renaming bad params), `lombok` (use it if the project does, ask before adopting it if it doesn't), `spring-boot` (`@Bean` methods are package-private). |
| [`sql-development`](plugins/sql-development) | SQL / relational database skills. Currently: `database-design` (schema conventions, audit columns, dialect-aware rules across Postgres / MySQL / SQL Server / Oracle / SQLite, online migration safety, ASK-first on every undecided detail). |
| [`workflow`](plugins/workflow) | Skills governing how Claude interacts with me, plus session-lifecycle commands. Skills: `ask-user-questions` (one-topic-per-question discipline), `persist-project-preferences` (durable preferences land in `CLAUDE.md`, not local memory), `definition-of-done` (9-item self-check before claiming a coding task is finished). Commands: `/session-handoff` (capture session state at end), `/session-pickup` (read it on the next session). |
| [`documentation`](plugins/documentation) | Documentation skills. `readme` (strict-minimum README — title, description, dev setup) and `wiki` (GitHub Wiki via submodule, five-category Tutorials/How-to/Reference/Explanations/Development taxonomy, pattern-detection prompt, post-task update check). Commands: `/readme-init`, `/wiki-init`. |

## Repo layout

```
.
├── .claude-plugin/
│   └── marketplace.json          # marketplace manifest — lists plugins
├── plugins/
│   ├── build-tools/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       └── build-tools/
│   │           └── SKILL.md
│   ├── ci-cd/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       └── ci-cd/
│   │           └── SKILL.md
│   ├── logging/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       └── logging/
│   │           └── SKILL.md
│   ├── git/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       └── gitignore/
│   │           └── SKILL.md
│   ├── java-development/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       ├── java-logging/
│   │       │   └── SKILL.md
│   │       ├── javadoc/
│   │       │   └── SKILL.md
│   │       ├── lombok/
│   │       │   └── SKILL.md
│   │       └── spring-boot/
│   │           └── SKILL.md
│   ├── sql-development/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       └── database-design/
│   │           └── SKILL.md
│   ├── workflow/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   ├── commands/
│   │   │   ├── session-handoff.md
│   │   │   └── session-pickup.md
│   │   └── skills/
│   │       ├── ask-user-questions/
│   │       │   └── SKILL.md
│   │       ├── definition-of-done/
│   │       │   └── SKILL.md
│   │       └── persist-project-preferences/
│   │           └── SKILL.md
│   └── documentation/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── commands/
│       │   ├── readme-init.md
│       │   └── wiki-init.md
│       └── skills/
│           ├── readme/
│           │   └── SKILL.md
│           └── wiki/
│               └── SKILL.md
├── README.md
└── .gitignore
```

Each plugin under `plugins/<name>/` is a self-contained directory with its own `.claude-plugin/plugin.json` and any skills, slash commands, agents, or hooks it needs.

## Adding a new plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json`.
2. Add skills under `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` (or `commands/`, `agents/`, `hooks/` as needed).
3. Append an entry to `plugins` in `.claude-plugin/marketplace.json`.
4. Commit and push.

## Adding a new skill to an existing plugin

Drop it under `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` and commit. The plugin's git commit SHA is the version — no `version` field to bump in the manifests.
