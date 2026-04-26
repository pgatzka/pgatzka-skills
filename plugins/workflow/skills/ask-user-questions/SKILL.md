---
name: ask-user-questions
description: "Use this skill whenever you need to gather information, clarification, preferences, or feedback from the user during any task. Triggers include: ambiguous requirements, missing technical details, multiple valid approaches to choose from, confirming assumptions before proceeding, design/architecture decisions, tech stack choices, scope clarification, or any moment you would otherwise write clarifying questions as prose. Instead of asking questions inline in chat, always use the AskUserQuestion tool so the user gets interactive, tappable options. Do NOT use this skill for venting/emotional conversations, factual questions you should answer directly, or when the user has already provided sufficient detail to proceed."
---

# Ask User Questions

## Overview

Whenever you need input from the user — clarification, a decision, a preference, feedback on a plan, confirmation of an assumption — use the **AskUserQuestion** tool instead of writing questions as prose in chat. Interactive questions with tappable options are faster for the user to answer, easier to scan, and produce cleaner, more structured responses than free-form prose.

## Core rules

### 1. Each question covers exactly one atomic topic

Each question should resolve exactly **one decision**. Bundled questions force the user into a compromise answer that doesn't actually resolve either decision cleanly — and the next reply has to disambiguate, which defeats the point of using interactive choices in the first place. If a question is bundling multiple decisions, split it.

**Bad (bundled topics):**

> What tech stack do you want to use?

This bundles frontend, backend, database, and probably more. The user can't answer cleanly with a single option.

**Good (one topic per question):**

- What frontend framework do you want to use?
- What backend language do you want to use?
- What database do you want to use?

Each question is one decision. Each has its own clean set of options.

**How to tell if a question is atomic:** ask yourself, *"Could a reasonable user's answer to this require two different selections?"* If yes, split it.

- "What deployment setup?" → split into hosting provider, CI/CD tool, containerization approach
- "How should we handle auth?" → split into auth provider, session strategy, password requirements
- "What styling approach?" → usually atomic (one choice: Tailwind vs CSS Modules vs styled-components)

### 2. Always include a recommended option, with the reason

Every question should present a recommendation. Mark it `(Recommended)` in the **label** and explain *why* it's recommended in the **description** — the safer default, the industry-standard choice, the more reversible path, whatever the actual reason is. Don't present neutral menus that hide which option is the sensible default.

The user can still pick something else; the recommendation exists so they pick *knowingly*. If you don't surface one, you've offloaded the work of figuring out which option is the default to the user — and they're using AskUserQuestion in the first place because they want a structured, opinionated prompt.

When there's genuinely no recommendation (the answer is purely a matter of taste, or the tradeoffs are equal), say so explicitly — but most of the time there is a sensible default, and naming it is the helpful thing.

Put the recommended option **first** in the list.

## You can ask up to 4 questions at once

Batching is encouraged when multiple atomic decisions are needed to move forward. Asking 2–4 related-but-distinct questions in a single AskUserQuestion call is much better than a back-and-forth over several turns.

When starting a new project or major feature, it's normal to batch 3–4 questions covering different facets (frontend, backend, database, auth) in one call — just make sure each one is atomic. If you genuinely need 5+ decisions to proceed, do them in two consecutive AskUserQuestion calls rather than trying to cram.

The tool's hard cap is 4 questions per call.

## When to use AskUserQuestion

Use it whenever you would otherwise:

- Write "Before I start, a few questions:" followed by a prose list
- Ask "Should I do X or Y?" inline
- Say "Let me know if you'd prefer..."
- Make an assumption you're not confident about and want to confirm
- Need to choose between multiple valid technical approaches
- Need feedback on a proposed plan or design

## When NOT to use AskUserQuestion

- **The answer is already in context.** If the user's code, project files, or earlier messages answer the question, don't ask. Read first.
- **The user gave a detailed spec.** They've already narrowed things; asking more second-guesses them. Proceed and state assumptions inline.
- **Factual questions you can answer.** If the user asks "A or B?", give your analysis — don't bounce it back as a question.
- **Trivial/obvious decisions.** Don't ask about variable names, file structure minutiae, or things a reasonable default covers.
- **Emotional or open-ended discussion.** If the user is thinking out loud or venting, respond conversationally.

## Writing good questions and options

**Question text:** short, specific, names the one topic. "What database do you want to use?" not "How should we handle data?"

**Options:** 2–4 short, mutually exclusive choices. Use real names (PostgreSQL, MySQL, SQLite), not vague labels (relational DB, simple DB).

**Don't add an "Other" / "Let me specify" option yourself** — the tool always provides a free-text fallback automatically. Adding one manually wastes a slot and duplicates a built-in capability.

**Each option's `description`** explains what it means or what happens if chosen. The user reads label + description together; both should be specific. "Recommended" lives in the label (per rule 2), the *why* lives in the description.

## Tool fields beyond label and description

The tool exposes more than just question text and options. Use them deliberately:

**`header`** (required, ≤12 characters) — a short chip label shown alongside the question in the UI. A noun phrase, not a sentence: `"Frontend"`, `"Auth method"`, `"Approach"`. Helps the user scan a batch of questions at a glance.

**`multiSelect`** (default `false`) — set `true` only when the choices are not mutually exclusive. Single-select fits "*What* database do you want?" Multi-select fits "*Which* features should the dashboard include?" Default to single-select; bundling features into one multi-select question is fine, but bundling unrelated decisions still violates rule 1.

**`preview`** (optional, single-select only) — a concrete artifact rendered in monospace alongside each option. Use for ASCII mockups of UI layouts, code-snippet variants, configuration examples — anywhere the choice is *visual* and labels alone don't carry the difference. Don't use previews for plain preference questions where short labels and descriptions suffice.

## Examples

### Starting a new web app (good batching)

Four atomic questions in one call, each with a recommended option:

1. **What frontend framework?** → [React (Recommended — broad ecosystem, hiring pool), Vue, Svelte, Plain HTML]
2. **What backend language?** → [TypeScript / Node.js (Recommended — shares types with the frontend), Python, Go, Rust]
3. **What database?** → [PostgreSQL (Recommended — durable default, JSONB if you need flexibility), SQLite, MongoDB, None needed]
4. **What styling approach?** → [Tailwind (Recommended — colocated styles, no naming overhead), CSS Modules, styled-components, Plain CSS]

### Clarifying an ambiguous bug report

Single focused question:

1. **Where is the bug happening?** → [Login flow, Dashboard, API response, Somewhere else]

(Pure clarification — no recommendation makes sense; the user knows where the bug is, you don't.)

### Confirming before a destructive action

Single focused question with an explicit safer default:

1. **This will delete 47 files in `/old/`. Proceed?** → [No, show me the list first (Recommended — verify before destruction), Yes delete them, Cancel]

## Anti-patterns to avoid

- **Bundling:** "What framework and database?" → split into two questions.
- **Leading:** "You want PostgreSQL, right?" → ask neutrally and let the recommendation do the work.
- **Neutral menus:** four equally-weighted options with no recommendation when there's a clear default — see rule 2.
- **Manual "Other" option:** the tool auto-provides this; don't waste a slot.
- **Too many options:** 7 choices overwhelms — pick the top 3–4 and let the auto-"Other" handle the rest.
- **Vague options:** "Modern" vs "Traditional" — use concrete names.
- **Asking when you shouldn't:** if a sensible default exists and the user said "just build it," build it.
- **Prose questions after tool questions:** don't use AskUserQuestion and *also* ask more things in prose in the same turn. Put everything in the tool.
