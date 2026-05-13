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
HOOK = HERE / "validate_ask_user_question.py"


def run(payload: dict) -> dict:
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    return json.loads(proc.stdout)


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

    print("\nAll smoke tests passed.")


if __name__ == "__main__":
    main()
