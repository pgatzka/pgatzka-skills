# Hook behavior

What the structured-questions PreToolUse hook on `AskUserQuestion` enforces, what it can't, and how to recover from a deny.

## What the hook enforces

Structural rules visible in the `AskUserQuestion` payload:

- **Rule 2.** Each question has at least two options. If `options` is not a list at all (e.g. `null`, a string, an object), the deny message names the actual type so the caller can see what was sent.
- **Rule 3.** Exactly one option's label ends with `(Recommended)` (case-insensitive), and the label has real option text in front of the marker. The hook rejects three failure shapes: the marker at the start (`(Recommended) Spring`), trailing text after the marker (`Spring (Recommended) for v2`), and a label that is *only* the marker with no option name (`(Recommended)`).
- **Rule 5.** Every option's `description` contains the literal, case-sensitive substrings `Pros:` and `Cons:` (capital `P`, capital `C`).

Y/N pairs (exactly two options whose labels normalize to one of the whitelisted pairs in Rule 2) are exempt from Rules 3 and 5. The full Y/N exemption rules — whitelist contents, and the fact that adding `(Recommended)` to a Y/N option revokes the exemption — live in Rule 2 of the parent `SKILL.md` to keep one canonical location.

## What the hook can't enforce

- **Rule 1** (use the tool, not prose) is unenforceable from *inside* a tool call — the hook only sees calls that already happened.
- **Rule 4** (Other always available) is auto-provided by the tool itself; the hook can't catch option lists that *behave* as exhaustive even though Other technically exists. That's a wording concern, not a structural one.
- **Rule 6** (batch independence) is semantic — whether two questions depend on each other requires reading the questions, not their JSON shape.

Rules 1, 4, and 6 rely on this skill's guidance, not the hook.

## If the hook denies the call

The hook returns a `systemMessage` naming the rule violated, the question/option index, and a suggested fix. When that happens:

1. Read the `systemMessage` and locate the named violation.
2. Apply the suggested fix to the offending question(s) — add `(Recommended)`, add literal `Pros:`/`Cons:` lines, split or merge options as called for.
3. Re-call `AskUserQuestion` with the corrected JSON.

Do not retreat to prose to bypass a deny — that violates Rule 1 and loses structure. Do not disable the plugin to push through; that's the escape hatch for free-form sessions, not for working around a single failed call.
