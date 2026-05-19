# structured-questions

A Claude Code plugin that forces every user-facing question to use the `AskUserQuestion` tool with neutral, structured options. Adds a `Recommended` option, leaves `Other` available, and requires explicit `Pros:`/`Cons:` per option. A PreToolUse hook blocks `AskUserQuestion` calls that don't comply.

## Why

Defaults that hide behind "reasonable choices" cause drift — the user ends up with a stack they didn't pick, only ratified. This plugin makes every decision visible:

- Multiple tappable options, never a yes/no smuggled into prose.
- One option flagged `(Recommended)` with the rationale spelled out.
- Literal `Pros:` and `Cons:` per option so the trade-offs are explicit, not implied through word choice.
- `Other` is always implicitly available — option lists are never treated as exhaustive.
- Questions in one batch are independent — no follow-up question whose options would change based on a sibling answer.

The skill teaches the rules; the hook enforces the structural ones at the tool boundary.

## Components

- `skills/structured-questions/SKILL.md` — soft enforcement; loads when Claude is about to ask a question and explains the six rules.
- `hooks/hooks.json` + `hooks/scripts/validate_ask_user_question.py` — PreToolUse hook on `AskUserQuestion`. Blocks calls missing `(Recommended)` or `Pros:`/`Cons:` lines, with an exemption for whitelisted yes/no pairs.
- `tests/test_validate_ask_user_question.py` — smoke tests for the hook, runnable post-install via `python3 -B plugins/structured-questions/tests/test_validate_ask_user_question.py`. Ships with the plugin so a fresh clone can verify the validator without external test infra.

## Requirements

- `python3` on `PATH` (the hook invokes `python3 -B`). On Windows where only `python` is available, install Python 3 in a way that registers `python3` (the official python.org installer registers both; the Microsoft Store shim does not). The hook uses stdlib only.
- Claude Code with plugin support.

## Install

From this marketplace:

```
/plugin marketplace add pgatzka/skills
/plugin install structured-questions@pgatzka-marketplace
```

Reload plugins (or restart Claude Code) so the hook configuration is picked up — hooks only load at session start.

## Disable

```
/plugin disable structured-questions
```

This is the only off-switch. There is no per-project setting; the plugin is on or off.

## Example: what a compliant question looks like

When Claude is about to ask a binary technical choice, the resulting `AskUserQuestion` call looks like:

```jsonc
{
  "questions": [
    {
      "question": "Which test runner should the project standardize on? Affects CI config and what skills will assume going forward.",
      "header": "Test runner",
      "options": [
        {
          "label": "Vitest (Recommended)",
          "description": "Pros: faster cold start, native ESM, drop-in for Vite projects. Cons: smaller ecosystem of plugins than Jest, occasionally drifts behind Jest on new matchers."
        },
        {
          "label": "Jest",
          "description": "Pros: largest ecosystem, mature mocks/snapshots, most StackOverflow answers target it. Cons: slower in big monorepos, ESM story is still rough."
        }
      ]
    }
  ]
}
```

If Claude instead omits `(Recommended)` or skips the `Pros:`/`Cons:` lines, the hook blocks the call and returns a `systemMessage` naming the rule violated and the suggested fix.

## What the hook can and can't check

Can:

- Each question has ≥2 options.
- Exactly one option per question carries `(Recommended)`.
- Each option description contains literal `Pros:` and `Cons:`.
- Exempts pairs whose labels match `Yes`/`No`, `Confirm`/`Cancel`, `Proceed`/`Abort`, `Keep`/`Discard`, `Accept`/`Reject`, `Allow`/`Deny`, `Enable`/`Disable`, `OK`/`Cancel`.

Can't (lives in the skill):

- Whether option wording is genuinely neutral or quietly biased.
- Whether the `question` text explains *why* the question is being asked.
- Whether two questions in the same batch are semantically independent.

## License

MIT — see `LICENSE`.
