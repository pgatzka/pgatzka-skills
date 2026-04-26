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
| [`java-development`](plugins/java-development) | Java engineering skills. Currently: `java-logging` (structured SLF4J logging conventions, sensible log levels, no sensitive data, no stack traces at ERROR). |

## Repo layout

```
.
├── .claude-plugin/
│   └── marketplace.json          # marketplace manifest — lists plugins
├── plugins/
│   └── java-development/
│       ├── .claude-plugin/
│       │   └── plugin.json       # plugin metadata
│       └── skills/
│           └── java-logging/
│               └── SKILL.md
├── README.md
└── .gitignore
```

Each plugin under `plugins/<name>/` is a self-contained directory with its own `.claude-plugin/plugin.json` and any skills, slash commands, agents, or hooks it needs.

## Adding a new plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json`.
2. Add skills under `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` (or `commands/`, `agents/`, `hooks/` as needed).
3. Append an entry to `plugins` in `.claude-plugin/marketplace.json`.
4. Bump versions, commit, push.

## Adding a new skill to an existing plugin

Drop it under `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`. Bump the plugin's `version` in its `plugin.json`.
