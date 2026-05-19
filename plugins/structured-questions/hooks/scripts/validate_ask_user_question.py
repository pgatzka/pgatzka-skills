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
RECOMMENDED_MARKER_LOWER = RECOMMENDED_MARKER.lower()


def has_recommended_marker(label: str) -> bool:
    """Case-insensitive marker presence check."""
    return RECOMMENDED_MARKER_LOWER in label.lower()


def strip_recommended_marker(label: str) -> str:
    """Case-insensitive removal of the marker, preserving the rest of the label."""
    idx = label.lower().find(RECOMMENDED_MARKER_LOWER)
    if idx == -1:
        return label
    return (label[:idx] + label[idx + len(RECOMMENDED_MARKER):]).strip()


def normalize_label(label: str) -> str:
    """Strip the marker (any case) and lowercase the rest for whitelist comparison."""
    return strip_recommended_marker(label).strip().lower()


def label_has_recommended_suffix(label: str) -> bool:
    """Rule 3 says append (Recommended) to the label of an option, so the
    marker must be the suffix AND there must be option text in front of it.
    A label that is *only* the marker (e.g. `(Recommended)`) is not a valid
    appended-marker label — there's no option to recommend."""
    stripped = label.rstrip()
    if not stripped.lower().endswith(RECOMMENDED_MARKER_LOWER):
        return False
    prefix = stripped[: -len(RECOMMENDED_MARKER)]
    return bool(prefix.strip())


def is_yn_pair(options: list) -> bool:
    if len(options) != 2:
        return False
    raw_labels = [(o.get("label", "") or "") if isinstance(o, dict) else "" for o in options]
    # A pure Y/N pair has no (Recommended) marker on either option — Rule 3 doesn't
    # apply, so the marker shouldn't be there. Refuse the exemption if it is, so a
    # writer can't slip past Rules 3+5 by mislabelling a real choice as Y/N.
    if any(has_recommended_marker(label) for label in raw_labels):
        return False
    labels = frozenset(normalize_label(label) for label in raw_labels)
    return labels in YN_PAIRS


def check_question(q_idx: int, q: dict) -> list[str]:
    violations: list[str] = []
    raw_options = q.get("options")
    options = raw_options if isinstance(raw_options, list) else []
    # Cast to str defensively so non-string question values (number, dict, None)
    # don't crash the slice or the !r repr below.
    q_text = str(q.get("question") or "<no question text>")
    q_label = f"question[{q_idx}] ({q_text[:60]!r})"

    if not isinstance(raw_options, list):
        violations.append(
            f"{q_label}: Rule 2 violated — `options` must be a list, got {type(raw_options).__name__}. "
            "Fix: pass options as a JSON array of objects, each with `label` and `description`."
        )
        return violations

    if len(options) < 2:
        violations.append(
            f"{q_label}: Rule 2 violated — needs at least 2 options, found {len(options)}. "
            "Fix: provide a real choice, or take the action without asking."
        )
        return violations

    # Guard against non-dict entries in the options array — a string or other
    # scalar would crash on .get() calls below. Coerce non-dicts to empty dicts
    # and record a violation per offending index.
    non_dict_idxs = [i for i, o in enumerate(options) if not isinstance(o, dict)]
    if non_dict_idxs:
        marked = ", ".join(str(i) for i in non_dict_idxs)
        violations.append(
            f"{q_label} option(s) at index {marked}: Rule 2 violated — each option must be an object with `label` and `description` fields; got non-object value(s). "
            "Fix: each option must be a JSON object like {\"label\": \"…\", \"description\": \"Pros: … Cons: …\"}."
        )
        options = [o if isinstance(o, dict) else {} for o in options]

    if is_yn_pair(options):
        return []

    recommended_suffix_idxs = [
        i for i, o in enumerate(options)
        if label_has_recommended_suffix(o.get("label") or "")
    ]
    midword_idxs = [
        i for i, o in enumerate(options)
        if has_recommended_marker(o.get("label") or "")
        and not label_has_recommended_suffix(o.get("label") or "")
    ]
    if midword_idxs:
        marked = ", ".join(str(i) for i in midword_idxs)
        violations.append(
            f"{q_label} option(s) at index {marked}: Rule 3 violated — the label must end with '(Recommended)' and have actual option text in front of it. "
            "Failure cases: the marker is at the start (e.g. '(Recommended) Spring'), there is text after it (e.g. 'Spring (Recommended) for v2'), or the label is only the marker with no option name. "
            "Fix: write the option label first, then append '(Recommended)' as the final token."
        )

    # Only emit the "no Recommended at all" violation when there are no midword markers either —
    # otherwise a single mid-string marker triggers two violations for one root cause, which
    # is noisier than helpful.
    if len(recommended_suffix_idxs) == 0 and not midword_idxs:
        violations.append(
            f"{q_label}: Rule 3 violated — no option whose label ends with '(Recommended)'. "
            "Fix: append '(Recommended)' to the label of the best default and explain the recommendation in its description."
        )
    elif len(recommended_suffix_idxs) > 1:
        marked = ", ".join(str(i) for i in recommended_suffix_idxs)
        violations.append(
            f"{q_label}: Rule 3 violated — {len(recommended_suffix_idxs)} options marked '(Recommended)' (at indices {marked}); must be exactly one. "
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

    # Coerce non-object JSON (null, number, list, string) to an empty dict so
    # the .get() calls below don't crash. The harness should always send an
    # object, but a malformed caller shouldn't take the hook out.
    if not isinstance(payload, dict):
        payload = {}

    if payload.get("tool_name") != "AskUserQuestion":
        print(json.dumps(allow()))
        return 0

    tool_input = payload.get("tool_input") or {}
    questions = tool_input.get("questions")
    if not isinstance(questions, list) or not questions:
        # Let the AskUserQuestion tool itself surface this as an input error —
        # blocking with a hook deny would frame it as a structured-questions rule
        # violation, which it isn't.
        print(json.dumps(allow(
            "structured-questions: tool_input.questions is missing or empty; passing through so the tool can return its own error."
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
