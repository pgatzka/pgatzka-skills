# pgatzka-marketplace

Philipp Gatzka's personal Claude Code plugin marketplace.

## Layout

- `.claude-plugin/marketplace.json` — marketplace manifest (lists plugins)
- `plugins/<name>/` — each plugin in its own directory, with `.claude-plugin/plugin.json`

## Install

```
/plugin marketplace add <github-org>/<repo>
/plugin install <plugin-name>@pgatzka-marketplace
```
