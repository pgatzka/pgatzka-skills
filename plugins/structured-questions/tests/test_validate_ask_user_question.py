"""Smoke tests for validate_ask_user_question.py. Run from plugin root.

Pipes sample PreToolUse payloads through the hook script and asserts the
expected permission decision and violation references.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
HOOK = HERE.parent / "hooks" / "scripts" / "validate_ask_user_question.py"


def run_raw(stdin_text: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin_text,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    return json.loads(proc.stdout)


def run(payload: dict) -> dict:
    return run_raw(json.dumps(payload))


def case(name: str, payload: dict, expected_decision: str, must_mention: list[str] | None = None) -> None:
    result = run(payload)
    actual = result["hookSpecificOutput"]["permissionDecision"]
    assert actual == expected_decision, (
        f"[{name}] expected {expected_decision}, got {actual}. Full output: {result}"
    )
    if must_mention:
        message = result.get("systemMessage") or ""
        for needle in must_mention:
            assert needle in message, f"[{name}] systemMessage missing {needle!r}: {message}"
    print(f"  PASS  {name}")


def case_raw(name: str, stdin_text: str, expected_decision: str) -> None:
    result = run_raw(stdin_text)
    actual = result["hookSpecificOutput"]["permissionDecision"]
    assert actual == expected_decision, (
        f"[{name}] expected {expected_decision}, got {actual}. Full output: {result}"
    )
    print(f"  PASS  {name}")


def ask(question: str, options: list[dict]) -> dict:
    return {
        "tool_name": "AskUserQuestion",
        "tool_input": {"questions": [{"question": question, "header": "h", "options": options}]},
    }


def main() -> None:
    print("structured-questions hook smoke tests:")

    case(
        "compliant 2-option question",
        ask("Pick a framework?", [
            {"label": "Spring (Recommended)", "description": "Pros: ecosystem. Cons: startup."},
            {"label": "Quarkus", "description": "Pros: fast. Cons: smaller community."},
        ]),
        expected_decision="allow",
    )

    case(
        "missing Recommended",
        ask("Pick a framework?", [
            {"label": "Spring", "description": "Pros: a. Cons: b."},
            {"label": "Quarkus", "description": "Pros: c. Cons: d."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 3", "(Recommended)"],
    )

    case(
        "two Recommended",
        ask("Pick a framework?", [
            {"label": "Spring (Recommended)", "description": "Pros: a. Cons: b."},
            {"label": "Quarkus (Recommended)", "description": "Pros: c. Cons: d."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 3", "must be exactly one"],
    )

    case(
        "missing Pros on one option",
        ask("Pick a framework?", [
            {"label": "Spring (Recommended)", "description": "It's great. Cons: startup."},
            {"label": "Quarkus", "description": "Pros: fast. Cons: less mature."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 5", "'Pros:'"],
    )

    case(
        "missing Cons on Recommended option",
        ask("Pick a framework?", [
            {"label": "Spring (Recommended)", "description": "Pros: ecosystem and stability."},
            {"label": "Quarkus", "description": "Pros: fast. Cons: less mature."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 5", "'Cons:'"],
    )

    case(
        "y/n exempt (Yes/No)",
        ask("Proceed with destructive op?", [
            {"label": "Yes", "description": "Go ahead."},
            {"label": "No", "description": "Abort."},
        ]),
        expected_decision="allow",
    )

    case(
        "y/n exempt (Confirm/Cancel, mixed case)",
        ask("Confirm push?", [
            {"label": "Confirm", "description": "Push to origin."},
            {"label": "Cancel", "description": "Don't push."},
        ]),
        expected_decision="allow",
    )

    case(
        "y/n exempt (OK/Cancel)",
        ask("Save the file?", [
            {"label": "OK", "description": "Save it."},
            {"label": "Cancel", "description": "Don't save."},
        ]),
        expected_decision="allow",
    )

    case(
        "2 options but NOT in whitelist still enforced",
        ask("Spring or Quarkus?", [
            {"label": "Spring", "description": "Just pick this."},
            {"label": "Quarkus", "description": "Or this."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 3"],
    )

    case(
        "multi-question batch with one violation",
        {
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [
                {"question": "Q1?", "header": "h", "options": [
                    {"label": "A (Recommended)", "description": "Pros: x. Cons: y."},
                    {"label": "B", "description": "Pros: z. Cons: w."},
                ]},
                {"question": "Q2?", "header": "h", "options": [
                    {"label": "X", "description": "Pros: x. Cons: y."},
                    {"label": "Y", "description": "Pros: z. Cons: w."},
                ]},
            ]},
        },
        expected_decision="deny",
        must_mention=["question[1]", "Rule 3"],
    )

    case(
        "non-AskUserQuestion tool ignored",
        {"tool_name": "Bash", "tool_input": {"command": "ls"}},
        expected_decision="allow",
    )

    case(
        "(Recommended) at start of label is not a valid suffix",
        ask("Pick a framework?", [
            {"label": "(Recommended) Spring", "description": "Pros: ecosystem. Cons: startup."},
            {"label": "Quarkus", "description": "Pros: fast. Cons: smaller community."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 3", "end with"],
    )

    case(
        "trailing text after (Recommended) is not a valid suffix",
        ask("Pick a framework?", [
            {"label": "Spring (Recommended) for v2", "description": "Pros: ecosystem. Cons: startup."},
            {"label": "Quarkus", "description": "Pros: fast. Cons: smaller community."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 3", "end with"],
    )

    case(
        "label that is only the marker (no option text) is not valid",
        ask("Pick a framework?", [
            {"label": "(Recommended)", "description": "Pros: nothing. Cons: nothing."},
            {"label": "Quarkus", "description": "Pros: fast. Cons: smaller community."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 3", "option text"],
    )

    case(
        "y/n loophole blocked: Yes (Recommended)/No no longer exempt",
        ask("Proceed?", [
            {"label": "Yes (Recommended)", "description": "Go ahead."},
            {"label": "No", "description": "Abort."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 5"],
    )

    case(
        "empty questions array passes through (tool surfaces its own error)",
        {"tool_name": "AskUserQuestion", "tool_input": {"questions": []}},
        expected_decision="allow",
    )

    case(
        "lowercase (recommended) marker is accepted",
        ask("Pick a framework?", [
            {"label": "Spring (recommended)", "description": "Pros: ecosystem. Cons: startup."},
            {"label": "Quarkus", "description": "Pros: fast. Cons: smaller community."},
        ]),
        expected_decision="allow",
    )

    case(
        "lowercase (recommended) still blocks y/n loophole",
        ask("Proceed?", [
            {"label": "yes (recommended)", "description": "Go ahead."},
            {"label": "no", "description": "Abort."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 5"],
    )

    case(
        "compliant 4-option question",
        ask("Which database engine?", [
            {"label": "Postgres (Recommended)", "description": "Pros: mature; great defaults. Cons: ops overhead."},
            {"label": "SQLite", "description": "Pros: zero ops. Cons: single-writer."},
            {"label": "MySQL", "description": "Pros: very familiar. Cons: weaker JSON support."},
            {"label": "DuckDB", "description": "Pros: fast analytics. Cons: less mature."},
        ]),
        expected_decision="allow",
    )

    case(
        "missing Pros in one option among many is still caught",
        ask("Which database engine?", [
            {"label": "Postgres (Recommended)", "description": "Pros: mature. Cons: ops overhead."},
            {"label": "SQLite", "description": "Pros: zero ops. Cons: single-writer."},
            {"label": "MySQL", "description": "It's familiar. Cons: weaker JSON."},
            {"label": "DuckDB", "description": "Pros: fast. Cons: less mature."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 5", "option[2]"],
    )

    case(
        "non-dict question entry recorded as violation",
        {
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": ["this is not a question object"]},
        },
        expected_decision="deny",
        must_mention=["question[0]", "not an object"],
    )

    case(
        "non-dict option entry doesn't crash the hook",
        {
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [
                {"question": "Pick one?", "header": "h", "options": [
                    "not a dict",
                    {"label": "B (Recommended)", "description": "Pros: a. Cons: b."},
                ]},
            ]},
        },
        expected_decision="deny",
        must_mention=["Rule 2", "must be an object"],
    )

    case(
        "options not a list reports type, not 'found 0'",
        {
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [
                {"question": "Q?", "header": "h", "options": "should be a list"},
            ]},
        },
        expected_decision="deny",
        must_mention=["Rule 2", "must be a list", "str"],
    )

    case(
        "null label tolerated, treated as empty",
        {
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [
                {"question": "Q?", "header": "h", "options": [
                    {"label": None, "description": "Pros: a. Cons: b."},
                    {"label": "X (Recommended)", "description": "Pros: c. Cons: d."},
                ]},
            ]},
        },
        expected_decision="allow",
    )

    case_raw(
        "malformed JSON on stdin allows pass-through",
        "not json at all {{{",
        expected_decision="allow",
    )

    case_raw(
        "non-object JSON (null) doesn't crash the hook",
        "null",
        expected_decision="allow",
    )

    case_raw(
        "non-object JSON (array) doesn't crash the hook",
        "[1, 2, 3]",
        expected_decision="allow",
    )

    case(
        "partial-whitelist Y/N (Yes/Nope) is enforced as a real choice",
        ask("Proceed?", [
            {"label": "Yes", "description": "Go ahead."},
            {"label": "Nope", "description": "Stop."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 3"],
    )

    case(
        "non-string question field doesn't crash the hook",
        {
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [
                {"question": 42, "header": "h", "options": [
                    {"label": "A", "description": "Pros: a. Cons: b."},
                    {"label": "B", "description": "Pros: c. Cons: d."},
                ]},
            ]},
        },
        expected_decision="deny",
        must_mention=["Rule 3"],
    )

    case(
        "question key absent entirely still validates options",
        {
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [
                {"header": "h", "options": [
                    {"label": "A", "description": "Pros: a. Cons: b."},
                    {"label": "B", "description": "Pros: c. Cons: d."},
                ]},
            ]},
        },
        expected_decision="deny",
        must_mention=["Rule 3", "no question text"],
    )

    case(
        "options=null treated as Rule 2 type violation",
        {
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [
                {"question": "Q?", "header": "h", "options": None},
            ]},
        },
        expected_decision="deny",
        must_mention=["Rule 2", "must be a list", "NoneType"],
    )

    case(
        "missing tool_input allows pass-through",
        {"tool_name": "AskUserQuestion"},
        expected_decision="allow",
    )

    case(
        "3-option pseudo-Y/N (Yes/No/Maybe) is enforced as real choice, not Y/N exempt",
        ask("Proceed?", [
            {"label": "Yes", "description": "Go."},
            {"label": "No", "description": "Stop."},
            {"label": "Maybe", "description": "Defer."},
        ]),
        expected_decision="deny",
        must_mention=["Rule 3"],
    )

    # Verify that a mid-word marker produces exactly one Rule 3 violation,
    # not both "midword" AND "no Recommended at all".
    midword_result = run(ask("Pick a framework?", [
        {"label": "(Recommended) Spring", "description": "Pros: a. Cons: b."},
        {"label": "Quarkus", "description": "Pros: c. Cons: d."},
    ]))
    midword_msg = midword_result.get("systemMessage") or ""
    rule3_hits = midword_msg.count("Rule 3 violated")
    assert rule3_hits == 1, (
        f"[double-violation suppression] expected exactly 1 'Rule 3 violated' in deny message, got {rule3_hits}. Full message: {midword_msg}"
    )
    print("  PASS  mid-word marker reports exactly one Rule 3 violation, not two")

    # Verify a multi-question batch with two non-compliant questions reports both.
    batch_result = run({
        "tool_name": "AskUserQuestion",
        "tool_input": {"questions": [
            {"question": "Q1?", "header": "h", "options": [
                {"label": "A", "description": "Pros: a. Cons: b."},
                {"label": "B", "description": "Pros: c. Cons: d."},
            ]},
            {"question": "Q2?", "header": "h", "options": [
                {"label": "X", "description": "Pros: x. Cons: y."},
                {"label": "Y", "description": "Pros: z. Cons: w."},
            ]},
        ]},
    })
    batch_msg = batch_result.get("systemMessage") or ""
    assert "question[0]" in batch_msg and "question[1]" in batch_msg, (
        f"[both-questions violation] expected both question[0] and question[1] in deny message: {batch_msg}"
    )
    print("  PASS  multi-question batch reports violations from both questions")

    print("\nAll smoke tests passed.")


if __name__ == "__main__":
    main()
