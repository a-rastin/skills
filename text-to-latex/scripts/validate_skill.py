#!/usr/bin/env python3
"""Static validation for the text-to-latex skill package."""

from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    ROOT / "SKILL.md",
    ROOT / "references" / "command-reference.md",
    ROOT / "references" / "conversion-rules.md",
    ROOT / "references" / "persian-xelatex.md",
    ROOT / "references" / "examples.md",
    ROOT / "tests" / "test-cases.md",
]
COMMANDS = [
    "@commandlist",
    "@onepar",
    "@persian",
    "@percent",
    "@itemize",
    "@enumerate",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    for path in REQUIRED_FILES:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")
        if path.stat().st_size == 0:
            fail(f"empty required file: {path.relative_to(ROOT)}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    command_ref = (ROOT / "references" / "command-reference.md").read_text(encoding="utf-8")
    combined = skill + "\n" + command_ref

    if not skill.startswith("---\n"):
        fail("SKILL.md must begin with YAML front matter")
    if "name: text-to-latex" not in skill:
        fail("SKILL.md has an incorrect or missing name")
    if "exactly one fenced code block" not in skill.lower():
        fail("output contract is missing")

    for command in COMMANDS:
        if command not in combined:
            fail(f"missing command documentation: {command}")

    required_phrases = [
        "Do not fabricate",
        "XeLaTeX",
        "xepersian",
        "\\begin{itemize}",
        "\\begin{enumerate}",
        "درصد",
    ]
    for phrase in required_phrases:
        if phrase not in combined:
            fail(f"missing required phrase or rule: {phrase}")

    # Validate that Markdown links in SKILL.md resolve locally.
    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", skill):
        if "://" in target or target.startswith("#"):
            continue
        if not (ROOT / target).resolve().is_file():
            fail(f"broken local link in SKILL.md: {target}")

    print("OK: text-to-latex skill package passed static validation.")


if __name__ == "__main__":
    main()
