---
name: structured-questions
description: This skill should be used whenever Claude Code is about to ask the user a clarifying question, request a decision, present a choice between approaches, or pause for input mid-task. Triggers when Claude would otherwise write a clarifying question in prose ("Should I X or Y?", "Do you want A or B?"), when ambiguous requirements need disambiguation, when multiple valid approaches exist, when confirming assumptions before destructive actions, or any time a user choice would prevent guessing. Enforces six rules: use AskUserQuestion (not prose), present multiple options, mark exactly one as Recommended with the rationale, leave Other available, give each option explicit Pros and Cons in neutral language, and never put dependent questions in the same batch.
---

# Structured Questions

Constrain how Claude Code asks the user for input. Every user-facing question goes through `AskUserQuestion` with neutral options, an explicit Recommended choice, an Other affordance, and literal Pros/Cons per option. Never put questions whose answers depend on each other in the same batch.

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

### Rule 2 — Always multiple options

Every question carries at least two options. A single-option "question" is a statement; if there is only one path forward, take it without asking.

Binary yes/no is acceptable *only* when the decision is genuinely two-state and confirmation is the point ("Confirm destructive action?", "Proceed with the push?"). Use whitelisted labels for those: `Yes`/`No`, `Confirm`/`Cancel`, `Proceed`/`Abort`, `Keep`/`Discard`, `Accept`/`Reject`, `Allow`/`Deny`, `Enable`/`Disable`. Any other two-option choice (e.g. "Spring vs Quarkus") is NOT a yes/no — apply the full Recommended + Pros/Cons rules.

### Rule 3 — Mark one option Recommended

Append `(Recommended)` to exactly one option's label. Put the rationale in that option's description, not in the question text. The user is free to ignore the recommendation; the marker exists so the recommendation is explicit instead of smuggled through word choice or option order.

If no option is genuinely better than the others, the question is probably underspecified — narrow it until a recommendation emerges, or merge the indistinguishable options.

The Y/N whitelist from Rule 2 is the only exception to Rule 3.

### Rule 4 — Other is always available

The `AskUserQuestion` tool provides an "Other" affordance automatically. Do not write questions whose option set is *exhaustive by assumption* — leave room for the user to type a path Claude didn't consider. If three options seem to cover the space but the space is open-ended (a name, a number, a custom path), Other is the safety valve. Wording questions as if the listed options were complete misleads the user about their choices.

### Rule 5 — Each option lists literal Pros and Cons in neutral language

Every option's `description` field contains the literal substrings `Pros:` and `Cons:`. Write both sides factually and in roughly equal weight. The Recommended option still gets Cons; non-recommended options still get Pros. The goal: the user decides on a level playing field, with the Recommended marker acting as a tie-breaker rather than a thumb on the scale.

The hook checks for these substrings literally. Loose prose like "this option is great because…" is rejected.

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

Before invoking `AskUserQuestion`, verify each item. Stop and fix anything that fails — the hook will reject calls that violate Rules 2, 3, or 5 anyway.

- Tool, not prose.
- Every question has ≥2 options.
- Each question has exactly one option whose label ends with `(Recommended)` — unless the question is a whitelisted Y/N pair.
- Every option's description contains the literal substrings `Pros:` and `Cons:` — unless whitelisted Y/N.
- Option wording is neutral; the Recommended option earns its mark through its Pros/Cons content, not via leading or loaded wording elsewhere.
- The question text states *why* the answer matters.
- No question's options or answer-space depends on another question in the same array.
- Where the answer space is open-ended, the option set does not pretend to be exhaustive.

## Why these rules exist

The user's standing preference is to be asked rather than steered. Defaults that hide behind "reasonable choices" cause drift: the user ends up with a stack they didn't pick, only ratified. Forcing every question through a structured component with explicit Pros/Cons keeps each decision visible and reversible at decision time.

Batch independence matters because parallel questions create false coherence — the user picks an option for Q1 expecting it to narrow Q2, only to find Q2 was already locked to the wrong frame. Splitting dependent questions across calls preserves the user's ability to redirect.

Disable the plugin (`/plugin disable structured-questions`) to bypass all rules for a free-form session; otherwise the hook will block non-compliant `AskUserQuestion` calls and surface the specific rule violated.
