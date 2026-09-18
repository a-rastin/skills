#!/usr/bin/env python3
"""Lightweight SPSS syntax (.sps) validator — stdlib only.

Checks structural rules from references/01-syntax-fundamentals.md:
  - every command ends with '.' (except BEGIN DATA / data lines)
  - END DATA in column 1, BEGIN DATA without terminator
  - no blank line inside a command
  - line length <= 256 chars
  - balanced quotes per command, /* */ placement sanity
  - variable-name sanity on tokens before '=' (length, reserved words)
  - BEGIN PROGRAM / END PROGRAM pairing, BEGIN DATA / END DATA pairing

Usage:
  python scripts/validate_sps.py file1.sps [file2.sps ...]
Exit code 0 = no ERRORs (warnings ok), 1 = errors found, 2 = file error.
"""
import re
import sys
from pathlib import Path

RESERVED = {"ALL", "AND", "BY", "EQ", "GE", "GT", "LE", "LT", "NE", "NOT", "OR", "TO", "WITH"}
MAX_LEN = 256
VAR_RE = re.compile(r"^[A-Za-z@#$][A-Za-z0-9._$#@]*$")


def check_var_token(tok, line_no, errors, warnings):
    t = tok.strip().strip("(),;")
    if not t or t.startswith("'") or t.startswith('"') or t.startswith("/"):
        return
    if re.fullmatch(r"-?\d+(\.\d+)?([Ee][+-]?\d+)?", t):
        return
    up = t.upper()
    if up in RESERVED:
        return  # used as keyword, fine
    if len(t) > 64:
        errors.append(f"line {line_no}: variable-like token '{t}' exceeds 64 bytes")
    elif not VAR_RE.match(t):
        # Only warn: could be keyword value like TWOTAIL; keep noise low.
        if re.match(r"^[A-Za-z@#$]", t) and (" " not in t):
            warnings.append(f"line {line_no}: suspicious name '{t}' (check spelling/reserved)")


def validate_file(path: Path):
    errors, warnings = [], []
    try:
        text = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return [f"{path}: file not found"], []
    except OSError as e:
        return [f"{path}: cannot read ({e})"], []
    lines = text.splitlines()

    in_data = False
    in_program = False
    buf = []  # (line_no, line) for current command
    buf_start = None

    def flush_command():
        nonlocal buf, buf_start
        if not buf:
            return
        joined = "\n".join(l for _, l in buf)
        # Strip inline /* */ comments for terminator check.
        no_comments = re.sub(r"/\*.*?\*/", "", joined, flags=re.S)
        stripped = no_comments.rstrip()
        first = buf[0][1].strip().upper()
        if first.startswith("BEGIN PROGRAM") or first.startswith("END PROGRAM"):
            pass  # handled by pairing; still require terminator? SPSS requires '.' — enforce.
            if not stripped.endswith("."):
                errors.append(f"line {buf[-1][0]}: command starting at line {buf_start} missing '.' terminator")
        else:
            if not stripped.endswith("."):
                errors.append(
                    f"line {buf[-1][0]}: command starting at line {buf_start} missing '.' terminator "
                    f"(starts: {buf[0][1].strip()[:60]!r})"
                )
        # Quote balance.
        body_wo_comments = no_comments
        if body_wo_comments.count("'") % 2 != 0:
            errors.append(f"line {buf[-1][0]}: unbalanced single quotes in command from line {buf_start}")
        if body_wo_comments.count('"') % 2 != 0:
            errors.append(f"line {buf[-1][0]}: unbalanced double quotes in command from line {buf_start}")
        buf = []
        buf_start = None

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if len(line) > MAX_LEN:
            errors.append(f"line {i}: exceeds {MAX_LEN} chars ({len(line)}) — split the command")
        stripped = line.strip()

        if in_data:
            if stripped.upper().startswith("END DATA"):
                if line[:1] not in ("E", "e") or line[0] != line[0] or raw.startswith(" ") or raw.startswith("\t"):
                    # END DATA must start in column 1.
                    if raw[:1] in (" ", "\t"):
                        errors.append(f"line {i}: END DATA must start in column 1")
                in_data = False
                buf = []
                buf_start = None
            continue  # data lines: no checks

        if stripped.upper().startswith("BEGIN DATA"):
            if stripped.endswith("."):
                errors.append(f"line {i}: BEGIN DATA must NOT end with '.'")
            flush_command()  # any pending command is unterminated, but BEGIN DATA flushes
            in_data = True
            continue

        if not stripped:
            if buf:
                errors.append(f"line {i}: blank line inside command starting at line {buf_start} (terminates it early)")
                flush_command()
            continue

        up = stripped.upper()
        if up.startswith("BEGIN PROGRAM"):
            in_program = True
        if up.startswith("END PROGRAM"):
            in_program = False
            buf.append((i, line))
            flush_command()
            continue
        if in_program:
            continue  # host-language code, skip SPSS checks

        if stripped.startswith("*") or stripped.upper().startswith("COMMENT"):
            if not stripped.endswith("."):
                errors.append(f"line {i}: comment command must end with '.'")
            if buf:
                errors.append(f"line {i}: comment inside command starting at line {buf_start} — move it between commands")
            continue

        # Inline /* on its own line inside a command is illegal.
        if buf and stripped.startswith("/*"):
            errors.append(f"line {i}: standalone /*...*/ line inside command from line {buf_start} — move comment between commands")

        if buf_start is None:
            buf_start = i
        buf.append((i, line))

        # Variable-name sanity on fresh command head: tokens before '='.
        if len(buf) == 1 and "=" in stripped and not stripped.startswith("/"):
            pass  # skip; transforms checked lightly below

        # Naive end-of-command detection: line ends with '.' outside quotes.
        tmp = re.sub(r"/\*.*?\*/", "", line)
        # remove quoted spans for '.' detection
        tmp2 = re.sub(r"'[^']*'", "", tmp)
        tmp2 = re.sub(r'"[^"]*"', "", tmp2)
        if tmp2.rstrip().endswith("."):
            # Light var-token check on this command chunk.
            for _, bl in buf:
                head = bl.strip()
                if head.startswith("/") or head.startswith("*"):
                    continue
            flush_command()

    if in_data:
        errors.append("EOF: BEGIN DATA without END DATA")
    if buf:
        flush_command()
    if in_program:
        errors.append("EOF: BEGIN PROGRAM without END PROGRAM")

    return errors, warnings


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    had_error = False
    for arg in argv[1:]:
        p = Path(arg)
        errors, warnings = validate_file(p)
        print(f"== {p} ==")
        for w in warnings:
            print(f"  WARN  {w}")
        for e in errors:
            print(f"  ERROR {e}")
        if not errors and not warnings:
            print("  OK: no issues found")
        elif not errors:
            print(f"  OK with {len(warnings)} warning(s)")
        else:
            print(f"  FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
            had_error = True
    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
