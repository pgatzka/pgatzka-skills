---
name: structured-questions
description: This skill should be used whenever Claude Code is about to ask the user a clarifying question, request a decision, present a choice between approaches, seek permission, defer a decision to the user, scope a task at its start, disambiguate a target (e.g. "which `User` class did you mean?"), or pause for input mid-task. Triggers when Claude would otherwise write a clarifying question in prose ("Should I X or Y?", "Do you want A or B?", "Want me to…", "Should I go ahead and…", "Let me know if you'd prefer X or Y", "I can either X or Y — which would you like?", "Up to you", "Your call", "Which would you prefer", "Either way works", "I'll let you decide", "Want me to pick", "thoughts?", "WDYT", "sound good?", "okay?", "any preference?", "feel free to…", "if you want I can…", "I'll go with X unless you'd prefer Y", "whatever you think", "whatever works for you", "should this include tests?", "Here's my plan — does this look right?", "before I start, want me to…", "want me to proceed?", "shall I proceed?", "ready for me to start?", "green light?"), when ambiguous requirements need disambiguation, when multiple valid approaches exist, when confirming assumptions before destructive actions, when seeking permission before a risky operation, when offering a choice of what to work on next, when reacting to an error or tool failure with options ("the test failed — should I retry or investigate?", "file not found — create it?", "the migration would drop a column — proceed?"), or any time a user choice would prevent guessing. Statement-shaped questions ("I can do A or B."), permission-seeking phrasings, fake-declaratives ("I'll just X then."), auto-decisions ("I'll assume X", "I'm going to assume…"), and hedge-style deferrals count — they are still questions in disguise. Enforces six rules: use AskUserQuestion (not prose), present multiple options, mark exactly one as Recommended with the rationale, leave Other available, give each option explicit Pros and Cons in neutral language, and never put dependent questions in the same batch.
---

# Structured Questions

Constrain how Claude Code asks the user for input. Every user-facing question goes through `AskUserQuestion` with neutral options, an explicit Recommended choice, an Other affordance, and literal Pros/Cons per option. Dependent questions go in separate batches — see Rule 6 for the reasoning.

A PreToolUse hook on `AskUserQuestion` enforces the structural rules at the tool boundary; this skill exists so the structure is right the first time and the hook rarely fires.

## When this skill applies

In scope whenever Claude is about to ask the user something. Concretely:

- Choosing between technical approaches (framework, library, architecture, language).
- Resolving ambiguous requirements.
- Confirming before a destructive or hard-to-reverse action.
- Asking for missing details where the answer space is open-ended (names, paths, identifiers).
- Picking a default when several defaults are equally reasonable.
- Sequencing follow-up questions whose options depend on a prior answer (use a *new* batch — see Rule 6).

Out of scope:

- Factual questions Claude can answer from current context.
- Venting/emotional turns where prose is appropriate.
- Cases where the user has already supplied enough detail to proceed.

## The six rules

### Rule 1 — Use AskUserQuestion, not prose

When about to write a question mark in chat followed by an implicit list of options ("Would you like A, B, or C?"), stop and call `AskUserQuestion` instead. The interactive component renders tappable options, captures structured input, and provides "Other" without retyping the question. Prose questions waste a turn and lose structure downstream.

Example — a prose hedge becoming a structured call:

```
PROSE (don't do this):
"I can use Vitest or Jest for the new test suite. Up to you — happy
either way. Let me know if you'd prefer one."

STRUCTURED CALL (do this):
AskUserQuestion({
  questions: [{
    question: "Which test runner should the new suite use? Affects CI config and what mocking style fits.",
    header: "Test runner",
    options: [
      { label: "Vitest (Recommended)",
        description: "Pros: faster cold start; native ESM; drop-in for Vite. Cons: smaller plugin ecosystem than Jest." },
      { label: "Jest",
        description: "Pros: largest ecosystem; mature mocks/snapshots. Cons: slower in monorepos; ESM story is rough." }
    ]
  }]
})
```

The prose version hides the trade-offs and asks the user to do the comparison from scratch. The structured call lays them out side-by-side so the answer is one tap.

### Rule 2 — At least two options

Every question carries at least two options. A single-option "question" is a statement; if there is only one path forward, take it without asking.

Binary yes/no is acceptable *only* when the decision is genuinely two-state and confirmation is the point ("Confirm destructive action?", "Proceed with the push?"). Use whitelisted labels for those: `Yes`/`No`, `Confirm`/`Cancel`, `Proceed`/`Abort`, `Keep`/`Discard`, `Accept`/`Reject`, `Allow`/`Deny`, `Enable`/`Disable`, `OK`/`Cancel`. Any other two-option choice (e.g. "Spring vs Quarkus") is not a yes/no — apply the full Recommended + Pros/Cons rules.

**Y/N exemption from Rules 3 and 5.** A true Y/N pair is exempt from both the `(Recommended)` marker (Rule 3) and the literal `Pros:`/`Cons:` lines (Rule 5), because the choice is already as constrained as it can get. **Adding `(Recommended)` to a Y/N option revokes the exemption** — the hook treats it as a non-binary choice and re-applies Rules 3 and 5 fully. Either go all-in (real Y/N, no marker, no Pros/Cons needed) or build a structured choice with the marker and full Pros/Cons.

### Rule 3 — Mark one option Recommended

Append `(Recommended)` to exactly one option's label — at the end, not embedded mid-string, and with real option text in front of it. The hook checks that `(Recommended)` is the suffix of the label *and* that the label has actual option content before the marker, so all three of these forms are rejected: `(Recommended) Spring` (marker at start), `Spring (Recommended) for v2` (trailing text after marker), and `(Recommended)` alone (no option text at all). Put the rationale in that option's description, not in the question text. The user is free to ignore the recommendation; the marker exists so the recommendation is explicit instead of smuggled through word choice or option order.

Smuggling example to avoid — the marker is missing, but the wording and ordering quietly steer the user toward option A:

```
Option A: "The clean, modern, well-supported approach."
Option B: "Older alternative. Still functional but less actively maintained."
```

Both descriptions are loaded; A is listed first; neither is tagged `(Recommended)`. The user reads this as "you want me to pick A" without the explicit recommendation that lets them push back. Fix: drop the loaded adjectives, give each option real Pros/Cons, and put `(Recommended)` on whichever you actually recommend (the user can still pick the other).

Write `(Recommended)` with a capital R as the canonical form — every example in this skill uses it. The hook accepts case variants (`(recommended)`, `(RECOMMENDED)`) as a safety net, but stick to canonical when authoring. See `${CLAUDE_PLUGIN_ROOT}/skills/structured-questions/references/hook_behavior.md` for the exact match rule.

If no option is genuinely better than the others, the question is probably underspecified — narrow it until a recommendation emerges, or merge the indistinguishable options.

For the Y/N exemption from this rule, see Rule 2.

### Rule 4 — Other is always available

The `AskUserQuestion` tool provides an "Other" affordance automatically. Do not write questions whose option set is *exhaustive by assumption* — leave room for the user to type a path Claude didn't consider. If three options seem to cover the space but the space is open-ended (a name, a number, a custom path), Other is the safety valve. Wording questions as if the listed options were complete misleads the user about their choices.

### Rule 5 — Each option lists literal Pros and Cons in neutral language

Every option's `description` field contains the literal, case-sensitive substrings `Pros:` and `Cons:` — the hook checks for these exact tokens with capital `P` and capital `C`. Loose prose like "this option is great because…" or lowercase `pros:` will be rejected.

Write both sides factually and in roughly equal weight. The Recommended option still gets Cons; non-recommended options still get Pros. The goal: the user decides on a level playing field, with the Recommended marker acting as a tie-breaker rather than a thumb on the scale.

Example option description:

```
Pros: simplest setup; no extra dependencies; works out of the box.
Cons: harder to extend later; locks the project into a single backend.
```

The question's main `question` field briefly states *why* the question is being asked — what decision rides on the answer, what changes downstream depending on the choice. Don't bury the rationale in option descriptions only.

### Rule 6 — Questions in one batch must be independent

`AskUserQuestion` accepts an array of questions answered in parallel by the user. Every question in that array must be answerable without knowing the answer to any other question in the same array.

Bad batch — Q2 depends on Q1:

```
Q1: Framework? Spring / Quarkus / Plain Java
Q2: Spring dependencies? Web / Data / Security
```

If the user picks Quarkus or Plain Java, Q2 is nonsense.

Good split: ask Q1 alone. When the answer arrives, decide whether Q2 is still relevant; if it is, ask it in a *new* `AskUserQuestion` call with options tailored to the actual answer.

Two questions CAN sit in the same batch if neither answer would change the other's option set or wording — e.g. "framework" + "license" + "README depth" can all coexist. The test: if rewording any option in question B based on the answer to question A would make sense, B does not belong in this batch.

## Pre-send checklist

Before invoking `AskUserQuestion`, re-verify the six rules. Two prompts to flag specifically because the hook can't catch them:

- Option wording is genuinely neutral — the Recommended option earns its mark through its Pros/Cons content, not through leading wording elsewhere.
- The question text states *why* the answer matters — what decision rides on it.

For the full enforcement contract (which rules the hook checks, which are judgment-only, and how to recover from a deny), see `${CLAUDE_PLUGIN_ROOT}/skills/structured-questions/references/hook_behavior.md`.

## Why these rules exist

The user's standing preference is to be asked rather than steered. Defaults that hide behind "reasonable choices" cause drift over time. The six rules above each carry their own rationale; the closing point is just that every decision should be visible and reversible at the moment it's made.

Disable the plugin (`/plugin disable structured-questions`) to bypass all rules for a free-form session; otherwise the hook will block non-compliant `AskUserQuestion` calls and surface the specific rule violated.
