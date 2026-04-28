---
name: definition-of-done
description: "Use this skill BEFORE claiming a coding task is done — before phrases like 'done', 'finished', 'complete', 'ready', 'that should do it', 'let me know if anything else', 'all set', 'good to go' — and before every commit, before opening a PR, and before /session-handoff. Walks through a 9-item checklist: original requirement met, code correct, code working, linter/formatter/type-check passes, no leftover TODOs/debug/commented-out code, new code covered by tests, tests actually run and pass, logging framework conventions followed if one is present, docs (README/wiki) updated when appropriate. When any item is uncertain or missing, the default is to close the gap (run the linter, run the tests, scan the diff) before claiming done — not to outsource the gap-closing back to the user. Only escalate to the user when the gap requires their input (e.g. ambiguous requirement). Do NOT use for purely conversational replies that produce no code changes."
---

# Definition of done

## Overview

Before claiming a coding task is finished, walk this 9-item checklist. Each item is a question to answer concretely — "yes, because <evidence>" — not a vibe-check. When an answer is "no" or "uncertain", the default is to **close the gap** (run the missing verification, fix the leftover, update the docs) and *then* claim done. Don't surface gaps to the user for them to close — that's outsourcing your job.

**Items 2 and 3 are deliberately separate.** Item 2 ("correct") is reasoning about whether the code *should* work — walking the logic, edge cases, error paths. Item 3 ("working") is exercising the code and observing that it *does* work. A change can be correct in your head but broken in practice, or working today but wrong about the edge case that hits next quarter. Both checks have to pass.

**Relation to `superpowers:verification-before-completion`:** if both skills are loaded, this one supersedes. The 9-item checklist is a strict superset of verification-before-completion's "evidence before assertions" rule — items 3, 4, and 7 cover the same ground with more specificity. Don't run both checklists; run this one.

## When the skill fires

- Before saying "done", "finished", "complete", "ready", "all set", "that should do it", "let me know if anything else", "good to go", or any equivalent.
- Before every `git commit`.
- Before opening or updating a pull request.
- Before invoking `/session-handoff`.

If the work in the turn produced no code changes (a question, a code reading, a discussion), the skill does not apply — there's nothing to verify.

## The checklist

### 1. Did I do what I was supposed to do?

**Re-read the original message** that initiated the task. Compare it to what was actually built. Specifically:

- Does the change cover the full scope the user asked for?
- Did scope drift sneak in (extras the user didn't ask for)? Either remove them or call them out.
- Is there an ambiguity in the original ask that you silently resolved? Surface it now.

The check is "what the user asked for", not "what I think they asked for after 30 turns of context." Re-read the literal message.

### 2. Is the code correct?

Walk the logic for the cases the change is supposed to handle:

- Typical / golden-path inputs.
- Edge cases (empty, null, zero, max, boundary values).
- Error paths (what happens when the dependency throws, the network fails, the input is malformed).

If you can't articulate a specific reason the code is correct for each of those, the answer is "uncertain", not "yes" — go run the code or write a test.

### 3. Is the code working?

The code compiles, the program starts, the change does what it's supposed to when exercised.

- **For backend changes**: build / compile, then run the entry point or the affected test.
- **For frontend / UI changes**: start the dev server and use the feature in a browser. Type-checking and tests verify code correctness, not feature correctness — if you can't actually test the UI, say so explicitly rather than claiming success.
- **For library / config changes**: exercise the path the change affects.

"It compiles" alone is not "working".

### 4. Does the linter / formatter / type-check pass?

If the project has any of these — `eslint`, `prettier`, `ktlint`, `spotless`, `mypy`, `tsc`, `clippy`, `golangci-lint`, etc. — they pass on the changed files (and ideally the whole project).

- Detect what the project uses (`package.json#scripts`, `pom.xml` plugins, `pyproject.toml`, README, CI config).
- Run them. Don't assume they'll pass; verify.
- If they fail, fix the findings or surface them as deliberate exceptions.

"The code working" includes static checks, not just one successful run.

### 5. Are there leftover TODOs, debug prints, or commented-out code?

Scan the diff before claiming done. Common leftovers:

- `console.log(...)`, `System.out.println(...)`, `print(...)`, `dbg!(...)`, `fmt.Println(...)`, `eprintln!(...)`.
- `// TODO: fix later`, `// FIXME`, `// XXX`, `// hack`.
- Blocks of code commented out "just in case".
- `debugger;`, `breakpoint()`, `binding.pry`.

These are noise that survived past the moment they were useful. Remove them or, if they need to stay, explain why in a real comment.

### 6. Is the new code covered by tests?

Every behavior change either has a test that exercises it or a stated reason it doesn't.

- New functions / methods: has at least one test that calls them with non-trivial inputs.
- Bug fixes: has a regression test that fails before the fix and passes after.
- Refactors with no behavior change: existing tests still cover the affected code (verify by running them and seeing them pass — see check 7).

Stated reasons for skipping a test are rare and need to be specific: "this is a one-off migration script that runs once and is then deleted", "this is a typo fix in a string literal", "this is generated code". Vague justifications ("it's trivial") don't count.

### 7. Did I actually run the tests?

Not "the tests exist", not "the tests should pass" — **did I run them and watch them pass**?

- Run the relevant suite. For a focused change, that's the affected module's tests; for a cross-cutting change, that's everything.
- Watch the output. A "Tests passed" line that scrolls by isn't enough; verify the count of tests run is sane (no 0-tests-run false-pass).
- Include the existing test suite, not just the new tests — a new feature can break old behavior.

If you can't run the tests in this environment (missing infra, missing creds, sandbox), say so explicitly. "I couldn't run the tests because X" is a real status; "the tests should pass" is not.

### 8. If a logging framework is present, is the new code covered by logs and following the logging conventions?

Detect-then-use, mirroring the `lombok` skill's pattern. If the project uses SLF4J / Log4j2 / Logback / Python `logging` / Go `log/slog` / etc., the change fits the existing logging conventions:

- **Coverage** — the new code emits logs at the right granularity. Significant operations log; trivial getters don't. New error paths have an error log. Long-running operations have an info-level start/finish.
- **Best practices** — for Java specifically, this hooks the `java-logging` skill: parameterized messages (no string concatenation), structured arguments, sensible levels (no stack traces at ERROR — split to ERROR-message + DEBUG-stack), `isXxxEnabled()` guards whenever an argument is computed only for the log line, no sensitive data, `@Slf4j` if Lombok is present.
- **Other languages** — apply the equivalent conventions for the project's logging library. If the language-specific skill doesn't exist yet, ASK the user whether this project has a logging style guide before guessing.

If no logging framework is detected (small CLI tool, library where logging is the consumer's responsibility, etc.), state that explicitly: "no logging framework — N/A". Don't introduce one as part of an unrelated change.

### 9. Are the docs (README / wiki) updated when appropriate?

Hooks into the existing `readme` and `wiki` skills' post-task doc-check.

- README: did the change add a new prerequisite, change the install steps, or change how to run the project? If yes, update README.
- Wiki: did the change establish a pattern other contributors should follow, change a documented architecture decision, or affect a documented user-facing feature? If yes, surface a wiki update suggestion (and ASK before writing, per the wiki skill).

If neither, state that explicitly: "no doc update needed — change is internal".

## When a check is "no" or "uncertain"

The default is to **close the gap yourself**, not to surface it back to the user.

| Gap | Default action |
|---|---|
| Linter not run | Run it. If it fails, fix or call out the findings. |
| Tests not run | Run them. |
| Coverage uncertain | Find the relevant test file (or absence), state coverage. |
| Docs status uncertain | Run the post-task doc-check from `readme` / `wiki`. |
| Leftover TODOs / debug | Remove them. |
| Build untested | Build it. |

Escalate to the user only when the gap genuinely requires their input:

- The original requirement is ambiguous and needs clarification.
- A test failure reveals a design question the user has to answer.
- The doc update is non-trivial and needs the user's framing.

The point: "the user pays for the result, not the gap-closing." If a check answer was "I didn't run the linter", the right response is to run it, not to write "you should run the linter to confirm".

## Output discipline at task completion

When the checklist is clean, the wrap-up reply states the outcome and any remaining caveats. Keep it short:

- What changed (one or two sentences, not a diff recap).
- What was verified (compiled, linter passed, tests run with N passing).
- Anything that *can't* be verified in this environment, with the reason.
- Any open question that survived the checklist (a deliberate scope cut, a follow-up suggestion).

Do not pad the wrap-up with checklist headers or self-congratulation. The user's signal that the work is done is the absence of gaps, not a long success report.
