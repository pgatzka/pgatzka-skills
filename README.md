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
| [`git`](plugins/git) | Git workflow skills. Currently: `gitignore` (minimal, anchored, alphabetically-sorted entries — no speculative bulk-adds). |
| [`java-development`](plugins/java-development) | Java engineering skills: `java-logging` (structured SLF4J, sensible levels, no sensitive data, no stack traces at ERROR), `javadoc` (don't state the obvious, all-or-nothing, ask before renaming bad params), `lombok` (use it if the project does, ask before adopting it if it doesn't). |

## Repo layout

```
.
├── .claude-plugin/
│   └── marketplace.json          # marketplace manifest — lists plugins
├── plugins/
│   ├── git/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/
│   │       └── gitignore/
│   │           └── SKILL.md
│   └── java-development/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           ├── java-logging/
│           │   └── SKILL.md
│           ├── javadoc/
│           │   └── SKILL.md
│           └── lombok/
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
