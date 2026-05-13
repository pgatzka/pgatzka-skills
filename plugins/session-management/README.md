# session-management

Slash commands to hand off / pick up Claude Code sessions through Obsidian.

- `/session-management:handoff` — writes every load-bearing piece of session knowledge into the project's Obsidian folder, structured per the repo's `documentation_tutorial_manual.md` (Diátaxis categories, descriptive titles, split/merge rules).
- `/session-management:pickup` — reads the project's Obsidian folder, briefs you on current state, and stands by for direction.

## Why

Project state is too big and too fast-moving for CLAUDE.md, and it shouldn't live in the working tree (where it bloats the repo and doesn't sync across machines). Obsidian is the right home: cross-machine via sync, queryable, with first-class wiki linking. This plugin makes the round-trip — handoff at session end, pickup at the next session start — a single command on each side.

## Requirements

- The **Obsidian MCP** server (`mcp__obsidian__*`) must be connected. If not, both commands stop loud rather than fall back to local files (cross-machine sync would silently break otherwise).
- The **documentation manual** bundled with this plugin at `references/documentation_tutorial_manual.md` (resolved via `${CLAUDE_PLUGIN_ROOT}`). The skills follow it as the contract for page shape. If missing, the skills fall back to the principles summarized in their bodies, and tell you.

## Vault convention

Per-project folder is `claude/<cwd-basename>` — no configuration. Example: cwd `G:/projects/pgatzka-skills` → Obsidian folder `claude/pgatzka-skills/`. The folder is created implicitly on the first write.

Inside the folder, layout is flat by default:

- A **project root index** named after the project (`pgatzka-skills.md`) — one-screen orientation, links to all sub-pages.
- **Sub-pages**, each in exactly one Diátaxis category, with descriptive titles: feature pages, technical reference, how-tos, explanations.
- **ADRs** as one-page-per-decision: `ADR - YYYY-MM-DD - <decision>.md`.

The skills pick the right Diátaxis category and decide new-page-vs-extend per the manual's split/merge rules. No fixed filenames.

## Install

From this marketplace:

```
/plugin marketplace add pgatzka/skills
/plugin install session-management@pgatzka-marketplace
```

## Example: handoff round-trip

End of session:

```
/session-management:handoff
```

The skill walks the completeness checklist, classifies each item, writes pages, updates the index, then reports what it wrote.

Start of next session (different machine, same repo cloned and synced):

```
/session-management:pickup
```

The skill reads the index, briefs you in under 30 seconds, and waits for your next move.

## What this plugin does NOT touch

- **CLAUDE.md.** If session-derived content is universally applicable to every session in this project, the handoff *flags* it for the user but does not edit CLAUDE.md. Run another tool (`/claude-md-management:revise-claude-md`, or edit by hand) for CLAUDE.md changes.
- **The working tree.** No files are written into the repo. State that needs to persist goes to Obsidian.

## License

MIT — see `LICENSE`.
