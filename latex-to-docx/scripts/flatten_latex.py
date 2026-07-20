#!/usr/bin/env python3
r"""Flatten \input/\include/\subfile recursively while producing a source map."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

from inspect_latex import INCLUDE_RE, lexical_view, read_text, resolve_tex


@dataclass(frozen=True)
class MapEntry:
    source_file: str
    source_line_start: int
    source_line_end: int
    output_line_start: int
    output_line_end: int


class FlattenError(RuntimeError):
    pass


def flatten_file(path: Path, project_root: Path, stack: tuple[Path, ...], source_map: list[MapEntry]) -> str:
    path = path.resolve()
    if path in stack:
        chain = " -> ".join(str(p) for p in (*stack, path))
        raise FlattenError(f"include cycle: {chain}")
    text, _ = read_text(path)
    view = lexical_view(text)
    matches = list(INCLUDE_RE.finditer(view))
    output_parts: list[str] = []
    cursor = 0
    current_output_lines = 1 + sum(part.count("\n") for part in output_parts)
    rel = path.relative_to(project_root).as_posix() if path.is_relative_to(project_root) else str(path)

    for m in matches:
        prefix = text[cursor:m.start()]
        if prefix:
            out_start = current_output_lines
            output_parts.append(prefix)
            current_output_lines += prefix.count("\n")
            src_start = text.count("\n", 0, cursor) + 1
            src_end = text.count("\n", 0, m.start()) + 1
            source_map.append(MapEntry(rel, src_start, src_end, out_start, current_output_lines))
        child = resolve_tex(m.group("path"), path.parent)
        if not child.exists():
            raise FlattenError(f"missing include {m.group('path')!r} at {rel}:{text.count(chr(10), 0, m.start()) + 1}")
        marker_start = f"\n% LATEX-TO-DOCX BEGIN {child}\n"
        marker_end = f"\n% LATEX-TO-DOCX END {child}\n"
        output_parts.append(marker_start)
        current_output_lines += marker_start.count("\n")
        child_text = flatten_file(child, project_root, (*stack, path), source_map)
        output_parts.append(child_text)
        current_output_lines += child_text.count("\n")
        output_parts.append(marker_end)
        current_output_lines += marker_end.count("\n")
        cursor = m.end()

    suffix = text[cursor:]
    if suffix:
        out_start = current_output_lines
        output_parts.append(suffix)
        current_output_lines += suffix.count("\n")
        src_start = text.count("\n", 0, cursor) + 1
        source_map.append(MapEntry(rel, src_start, text.count("\n") + 1, out_start, current_output_lines))
    return "".join(output_parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--map", dest="map_path", type=Path)
    parser.add_argument("--normalization", choices=["NFC", "none"], default="NFC")
    args = parser.parse_args()
    entry = args.entry.resolve()
    source_map: list[MapEntry] = []
    try:
        flattened = flatten_file(entry, entry.parent, tuple(), source_map)
        if args.normalization == "NFC":
            flattened = unicodedata.normalize("NFC", flattened)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(flattened, encoding="utf-8", newline="\n")
        if args.map_path:
            args.map_path.parent.mkdir(parents=True, exist_ok=True)
            args.map_path.write_text(json.dumps([asdict(x) for x in source_map], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except Exception as exc:
        print(f"flatten_latex: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
