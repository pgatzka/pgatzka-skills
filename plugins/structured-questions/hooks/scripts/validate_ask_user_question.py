#!/usr/bin/env python3
"""PreToolUse hook for AskUserQuestion.

Enforces the structural rules from the structured-questions skill:

- Rule 2: every question has at least 2 options.
- Rule 3: exactly one option label contains "(Recommended)".
- Rule 5: every option description contains literal "Pros:" and "Cons:".

Yes/no questions (exactly 2 options whose labels match a whitelisted pair) are
exempt from rules 3 and 5.

Rule 6 (batch independence) is semantic and cannot be checked here; it lives
in the skill body.

Communication contract:
- Reads PreToolUse payload from stdin (JSON).
- Writes a hookSpecificOutput JSON to stdout with permissionDecision "allow"
  or "deny", plus a systemMessage explaining any violations.
- Exits 0 in both allow and deny cases; the JSON carries the decision.
"""

from __future__ import annotations

import json
import sys

YN_PAIRS: list[frozenset[str]] = [
    frozenset({"yes", "no"}),
    frozenset({"confirm", "cancel"}),
    frozenset({"proceed", "abort"}),
    frozenset({"keep", "discard"}),
    frozenset({"accept", "reject"}),
    frozenset({"allow", "deny"}),
    frozenset({"enable", "disable"}),
    frozenset({"ok", "cancel"}),
]

RECOMMENDED_MARKER = "(Recommended)"


def normalize_label(label: str) -> str:
    return label.replace(RECOMMENDED_MARKER, "").strip().lower()


def is_yn_pair(options: list) -> bool:
    if len(options) != 2:
        return False
    labels = frozenset(normalize_label(o.get("label", "")) for o in options)
    return labels in YN_PAIRS


def check_question(q_idx: int, q: dict) -> list[str]:
    violations: list[str] = []
    options = q.get("options") or []
    q_text = q.get("question") or "<no question text>"
    q_label = f"question[{q_idx}] ({q_text[:60]!r})"

    if not isinstance(options, list) or len(options) < 2:
        violations.append(
            f"{q_label}: Rule 2 violated — needs at least 2 options, found {len(options) if isinstance(options, list) else 0}. "
            "Fix: provide a real choice, or take the action without asking."
        )
        return violations

    if is_yn_pair(options):
        return []

    recommended_idxs = [
        i for i, o in enumerate(options)
        if RECOMMENDED_MARKER in (o.get("label") or "")
    ]
    if len(recommended_idxs) == 0:
        violations.append(
            f"{q_label}: Rule 3 violated — no option marked '(Recommended)'. "
            "Fix: append '(Recommended)' to the label of the best default and explain the recommendation in its description."
        )
    elif len(recommended_idxs) > 1:
        marked = ", ".join(str(i) for i in recommended_idxs)
        violations.append(
            f"{q_label}: Rule 3 violated — {len(recommended_idxs)} options marked '(Recommended)' (at indices {marked}); must be exactly one. "
            "Fix: keep '(Recommended)' on only the strongest default."
        )

    for o_idx, o in enumerate(options):
        desc = o.get("description") or ""
        label = o.get("label") or "<no label>"
        missing: list[str] = []
        if "Pros:" not in desc:
            missing.append("'Pros:'")
        if "Cons:" not in desc:
            missing.append("'Cons:'")
        if missing:
            violations.append(
                f"{q_label} option[{o_idx}] ({label!r}): Rule 5 violated — description missing literal {', '.join(missing)} line(s). "
                "Fix: rewrite the description in the form 'Pros: <upsides>. Cons: <downsides>.' so structure is visible and the choice is neutral."
            )

    return violations


def allow(message: str | None = None) -> dict:
    out: dict = {"hookSpecificOutput": {"permissionDecision": "allow"}}
    if message:
        out["systemMessage"] = message
    return out


def deny(message: str) -> dict:
    return {
        "hookSpecificOutput": {"permissionDecision": "deny"},
        "systemMessage": message,
    }


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        print(json.dumps(allow(f"structured-questions: could not parse stdin as JSON ({e}); allowing.")))
        return 0

    if payload.get("tool_name") != "AskUserQuestion":
        print(json.dumps(allow()))
        return 0

    tool_input = payload.get("tool_input") or {}
    questions = tool_input.get("questions")
    if not isinstance(questions, list) or not questions:
        print(json.dumps(deny(
            "structured-questions: tool_input.questions is missing or empty; nothing to validate but also nothing to ask."
        )))
        return 0

    violations: list[str] = []
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            violations.append(f"question[{i}]: not an object; cannot validate.")
            continue
        violations.extend(check_question(i, q))

    if violations:
        message = (
            "structured-questions blocked AskUserQuestion. Rules violated:\n  - "
            + "\n  - ".join(violations)
        )
        print(json.dumps(deny(message)))
        return 0

    print(json.dumps(allow()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
