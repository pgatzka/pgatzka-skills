# documentation

Maintenance sweeps over the project's Obsidian documentation, following the Diátaxis manual bundled with the `session-management` plugin.

Single skill, single command:

- `/documentation:documentation` — on a user ask like *"update the docs for the new flag"*, *"the auth notes are out of date"*, or *"delete the obsolete OAuth ADR"*, this skill inventories the project's docs, classifies each affected page as create / update / delete / supersede / leave, and applies the operations in one pass. It confirms before deleting anything the user didn't explicitly name.

## Relationship to session-management

| Plugin | When it fires | What it writes |
| --- | --- | --- |
| `session-management:handoff` | At session end | Bulk capture of session state; overwrites the project root index wholesale |
| `session-management:pickup` | At session start | Nothing — reads only |
| `documentation:documentation` | On any user ask to maintain docs | Mixed create / update / delete across the project's doc set; merges the index, never overwrites it |

All three share:

- The same Obsidian vault folder convention (`claude/<cwd-basename>`).
- The same documentation manual (`documentation_tutorial_manual.md`, bundled in the `session-management` plugin and loaded via cross-plugin path).
- The same filename and write-routing conventions (the `page_template.md` reference bundled with `session-management/skills/handoff`).

## Requirements

- The Obsidian Local REST API plugin + the `obsidian` MCP server connected to it.
- The `session-management` plugin installed in the same marketplace — this skill loads its bundled manual and page-template references via `${CLAUDE_PLUGIN_ROOT}/../session-management/...`.

## Not for

- Capturing session state. Use `/session-management:handoff`.
- Reading existing docs at session start. Use `/session-management:pickup`.
- In-code comments or docstrings. Those belong with the code, not in Obsidian.
