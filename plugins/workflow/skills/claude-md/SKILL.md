---
name: claude-md
description: "Use whenever creating, editing, or evaluating content for a CLAUDE.md file — at the repo root or in any subdirectory. Triggers on phrases like 'add to CLAUDE.md', 'put this in CLAUDE.md', 'update CLAUDE.md', 'CLAUDE.md is getting long', 'should this go in CLAUDE.md', 'set up CLAUDE.md', 'split CLAUDE.md', 'subdirectory CLAUDE.md', and on any edit to a file named CLAUDE.md anywhere in the repo. Enforces four core disciplines: keep CLAUDE.md short (target under ~200 lines, split overflow into `.claude/docs/*.md` pointers); exclude content the model already knows or can find (LLM-common-knowledge, codebase-discoverable info, premature reading directives); layer per-subdirectory CLAUDE.md files at subdirectory roots (e.g. `apps/billing/CLAUDE.md`) when subtrees have divergent conventions instead of inflating the root file; place split-out section files under `.claude/docs/` (Claude Code's project-level config root), not under the project's human-facing `docs/` tree. Boundary with `persist-project-preferences`: that skill governs *what* gets persisted; this skill governs *how* CLAUDE.md is structured."
---

# CLAUDE.md

## Overview

CLAUDE.md is read into Claude Code's context at the start of every session in a project. That makes it the most expensive piece of documentation the project owns — every line costs tokens on every conversation, whether the line is relevant to that conversation or not. The discipline below keeps the file useful without bloating context.

**The audience of CLAUDE.md is Claude (and other agents), not humans.** Don't write it like a README — its job is not to onboard a new contributor or explain the project's purpose. Its job is to give the agent the project-specific facts it cannot derive from the code itself.

**Boundary with `persist-project-preferences`:** that skill decides *what* facts get persisted to CLAUDE.md (versus machine-local memory). This skill decides *how* the resulting file is structured — length, content boundaries, when to split, when to layer per-subdirectory. Both apply when editing CLAUDE.md; consult both.

## What belongs in CLAUDE.md

### Include — content the agent cannot derive on its own

- **Project-specific knowledge** that's not in the LLM's training data: domain vocabulary, internal naming conventions, why a certain unconventional choice was made, who owns what, what's "done" in this codebase.
- **Recurring-error guards** — concrete rules to prevent mistakes the agent has actually made (or is likely to make) in this codebase. These are the highest-leverage entries. Update them periodically as the agent's failure modes evolve.
- **Preferred patterns** — when there are multiple reasonable ways to do something and the project has chosen one, state the choice and (briefly) why. *"We use constructor injection over field injection — see `docs/agent/style.md` for examples."*
- **Pointers to `.claude/docs/` files** with a one-line description of each pointer. This is the main mechanism for keeping CLAUDE.md short — see "Point to files, don't inline" below.

### Don't include — content the agent already has or can find

- **Common stack knowledge.** "We use Spring Boot, which is a Java framework for…" is bloat — the agent knows what Spring Boot is.
- **Standard framework / library usage.** Don't restate the React docs, the Postgres syntax, the Maven build phases. The agent knows.
- **Codebase-discoverable facts.** Anything the agent can find via `find`, `grep`, or reading a file: directory structure, what tests exist, what classes are in `src/`, the names of npm scripts. The agent will look when needed.
- **Premature reading directives.** *"Always read `docs/architecture.md` before starting any task"* forces the file into context even when irrelevant. Instead: *"For architecture context, see `docs/architecture.md`."* The agent reads when the task calls for it.
- **Generic best practices.** "Write tests" / "Document your code" / "Use meaningful variable names" — the agent already knows. Only include guidance that's specific to *this project's* deviation from common practice.

The test for inclusion: *if I delete this line, will Claude make a mistake it wouldn't have made otherwise?* If the answer is no, it's bloat.

## Length discipline

**Target under ~200 lines.** Above that, the file is loading content most conversations don't need.

**When CLAUDE.md grows past the target:**

1. Identify logical sections — coding style, testing approach, deploy procedure, domain concepts, etc.
2. Move each section to a separate file under `.claude/docs/`. The `.claude/` directory is Claude Code's project-level config root, so agent-facing supporting documentation lives there alongside settings and hooks rather than in the project's human-facing `docs/` tree (which has its own audience and discipline — see the `wiki` and `readme` skills).
3. Replace the section in CLAUDE.md with a single-line pointer:

   ```markdown
   - **Coding style** — see `.claude/docs/style.md` for indentation, naming, and import conventions.
   - **Testing** — see `.claude/docs/testing.md` for test layout, fixture conventions, and the integration-test database setup.
   - **Domain glossary** — see `.claude/docs/glossary.md` for terms specific to this project (e.g. "tenant", "policy", "entitlement").
   ```

4. The pointer's one-line description tells Claude *when to read it*. Vague descriptions ("more details in X.md") defeat the purpose — the agent doesn't know whether the current task warrants reading it.

The split is not bureaucratic — it's load shedding. CLAUDE.md is read every session; `.claude/docs/*.md` is read when the task needs it.

## Point to files, don't inline

The single most important rule. Inline content lives in context forever; pointed-at content loads on demand.

**Anti-pattern (inline):**

```markdown
## Coding style
- 4-space indentation, never tabs
- No semicolons in TypeScript files
- Imports grouped: stdlib, third-party, local
- Sort imports alphabetically within each group
- ... (50 more lines)
```

**Pattern (pointer):**

```markdown
- **Coding style** — see `docs/agent/style.md`. Indentation, semicolons, import grouping.
```

**Why:** the inline version costs ~50 lines on every conversation, even when the conversation has nothing to do with style. The pointer costs one line; the agent reads `style.md` when the task involves writing or reviewing code.

The same applies to: hook configurations, environment setup, deploy procedures, schema reference, API conventions, glossary entries beyond a handful, anything else that's more than 3–4 lines of detail.

**Exception:** content that's genuinely needed on every turn (e.g. a single-line warning like "this codebase uses `database_id` not `db_id` in column names — getting this wrong breaks tests") stays inline. The line is cheap; the recurring mistake is expensive.

## Layered CLAUDE.md per subdirectory

For projects where different subdirectories follow genuinely different conventions, **add a CLAUDE.md inside that subdirectory** rather than inflating the root file with conditionals.

The root CLAUDE.md stays short and generic — facts true for the whole repo. Each subdirectory's CLAUDE.md adds the deltas specific to that subtree. Claude Code loads the appropriate file based on `cwd`.

**When to add a sub-CLAUDE.md:**

- A legacy module follows older patterns the rest of the repo has moved past, and you want different behavior there.
- An experimental subdirectory has stricter (or looser) rules — a research playground, a vendored fork, a generated-code area.
- A subtree has its own toolchain — e.g. a Python ML pipeline inside an otherwise-Java repo.
- A subdirectory has domain conventions the parent doesn't (e.g. `apps/billing/` deals with money and the rules around money handling don't apply elsewhere).

**When *not* to add one:**

- One-off scripts.
- Single-file modules where there's nothing to say beyond what the root CLAUDE.md already covers.
- "Same as root, but slightly emphasized" — duplication, not specialization. Add to root, or use a comment in the relevant code.
- Subdirectories that follow the root conventions exactly. The absence of a sub-CLAUDE.md *means* "root rules apply."

**Same length discipline applies to sub-CLAUDE.md files.** A sub-CLAUDE.md that grows past ~200 lines has the same problem as a bloated root file — split into pointers to `.claude/docs/` (the same location the root uses; one shared section-file directory across the repo, not per-subdirectory).

**Why the layered files stay at subdirectory roots, not under `.claude/docs/`:** Claude Code auto-loads `CLAUDE.md` based on the current working directory, walking up parent directories until it finds one. A file at `.claude/docs/billing/CLAUDE.md` would not auto-load when `cwd` is `apps/billing/`. The layered pattern relies on the file living at `apps/billing/CLAUDE.md` directly; split-out *section* files don't need auto-loading (they're loaded on demand via the pointer), so they belong under `.claude/docs/`.

**Don't repeat what the root says.** A sub-CLAUDE.md adds; it doesn't restate. If the root says "we use 4-space indentation" and the subdirectory uses 2-space, the sub-CLAUDE.md says only *"Indentation: 2-space (overrides root)."* Anything else creates drift between the two when the root changes.

## Periodic maintenance

CLAUDE.md decays. Three things to check periodically:

- **Stale pointers** — `docs/agent/*.md` files that have moved or been deleted. A broken pointer is worse than no pointer; the agent reads "see `docs/agent/old-style.md`" and loses trust in the rest of the file.
- **Outdated recurring-error guards** — entries written for failure modes the agent no longer hits, or for patterns the codebase has moved on from. These accumulate; prune them.
- **Lines that have become common knowledge** — what was project-specific six months ago may now be standard practice the model knows. Drop the entry if so.

Major refactors are a natural prompt for this maintenance — re-read CLAUDE.md after a significant codebase change and remove anything no longer true.

## A note on style

CLAUDE.md is read by an agent, not graded by a teacher. Use bullet points and short sentences. Skip the prose; skip the headings that say obvious things ("# Project Overview" at the top of a file named CLAUDE.md is bloat). Every line should pull its weight.
