#!/usr/bin/env python3
"""Inventory a LaTeX source tree for a fidelity-first DOCX conversion."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

INCLUDE_RE = re.compile(r"\\(?P<cmd>input|include|subfile)\s*(?:\[[^\]]*\]\s*)?\{(?P<path>[^{}]+)\}")
GRAPHIC_RE = re.compile(r"\\includegraphics\s*(?:\[(?P<opts>[^\]]*)\]\s*)?\{(?P<path>[^{}]+)\}")
BIB_RE = re.compile(r"\\(?:bibliography|addbibresource)\s*(?:\[[^\]]*\]\s*)?\{(?P<path>[^{}]+)\}")
GRAPHICSPATH_RE = re.compile(r"\\graphicspath\s*\{(?P<body>(?:\{[^{}]*\}\s*)+)\}")
ENV_BEGIN_RE = re.compile(r"\\begin\s*\{([^{}]+)\}")
ENV_END_RE = re.compile(r"\\end\s*\{([^{}]+)\}")
COMMAND_RE = re.compile(r"\\([A-Za-z@]+|.)")
MACRO_DEF_RE = re.compile(r"\\(?:newcommand|renewcommand|providecommand|DeclareMathOperator)\*?\s*\{?\\([A-Za-z@]+)")
ENV_DEF_RE = re.compile(r"\\(?:newenvironment|renewenvironment)\*?\s*\{([^{}]+)\}")
DOCUMENTCLASS_RE = re.compile(r"\\documentclass\s*(?:\[([^\]]*)\])?\s*\{([^{}]+)\}")
PACKAGE_RE = re.compile(r"\\usepackage\s*(?:\[([^\]]*)\])?\s*\{([^{}]+)\}")
LABEL_RE = re.compile(r"\\label\s*\{([^{}]+)\}")
REF_RE = re.compile(r"\\(ref|pageref|eqref|autoref|cref|Cref)\s*\{([^{}]+)\}")
CITE_RE = re.compile(r"\\(?:cite|citep|citet|parencite|textcite|autocite|footcite)\w*\s*(?:\[[^\]]*\]\s*){0,2}\{([^{}]+)\}")
VERBATIM_ENVS = ("verbatim", "Verbatim", "lstlisting", "minted", "comment")
GRAPHIC_EXTS = (".svg", ".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".eps", ".ps", ".emf", ".wmf")
ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
PERSIAN_SPECIFIC_RE = re.compile(r"[پچژگکی]")
STANDARD_COMMANDS = {
    "documentclass", "usepackage", "begin", "end", "input", "include", "subfile", "includeonly",
    "title", "author", "date", "maketitle", "section", "subsection", "subsubsection", "paragraph", "subparagraph",
    "chapter", "part", "textbf", "textit", "emph", "underline", "footnote", "marginpar", "item", "label", "ref",
    "pageref", "eqref", "autoref", "cref", "Cref", "cite", "citep", "citet", "parencite", "textcite", "autocite",
    "includegraphics", "caption", "centering", "hline", "cline", "multicolumn", "multirow", "toprule", "midrule",
    "bottomrule", "url", "href", "verb", "newline", "linebreak", "pagebreak", "newpage", "clearpage", "tableofcontents",
    "listoffigures", "listoftables", "bibliography", "bibliographystyle", "addbibresource", "printbibliography", "graphicspath",
    "setlength", "renewcommand", "newcommand", "providecommand", "newenvironment", "renewenvironment", "DeclareMathOperator",
    "settextfont", "setlatintextfont", "setmainfont", "setsansfont", "setmonofont", "lr", "rl", "textLR", "textRL", "LTR", "RTL",
}


@dataclass(frozen=True)
class FileRecord:
    path: str
    sha256: str
    size: int
    line_count: int
    encoding: str
    arabic_chars: int
    persian_specific_chars: int
    zwnj_count: int
    replacement_chars: int


@dataclass(frozen=True)
class Dependency:
    kind: str
    command: str
    source_file: str
    line: int
    raw_path: str
    resolved_path: str | None
    exists: bool


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig"), "utf-8-sig"
    try:
        return data.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace"), "utf-8-with-replacement"


def strip_comments_preserve(text: str) -> str:
    """Replace comments with spaces while preserving offsets and newlines."""
    chars = list(text)
    i = 0
    while i < len(chars):
        if chars[i] == "%":
            backslashes = 0
            j = i - 1
            while j >= 0 and chars[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2 == 0:
                while i < len(chars) and chars[i] not in "\r\n":
                    chars[i] = " "
                    i += 1
                continue
        i += 1
    return "".join(chars)


def mask_verbatim_preserve(text: str) -> str:
    masked = list(text)
    for env in VERBATIM_ENVS:
        pattern = re.compile(rf"\\begin\s*\{{{re.escape(env)}\}}.*?\\end\s*\{{{re.escape(env)}\}}", re.S)
        for m in pattern.finditer(text):
            for i in range(m.start(), m.end()):
                if masked[i] not in "\r\n":
                    masked[i] = " "
    verb_pattern = re.compile(r"\\verb(?P<d>[^A-Za-z0-9\s]).*?(?P=d)")
    for m in verb_pattern.finditer(text):
        for i in range(m.start(), m.end()):
            if masked[i] not in "\r\n":
                masked[i] = " "
    return "".join(masked)


def lexical_view(text: str) -> str:
    return mask_verbatim_preserve(strip_comments_preserve(text))


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def resolve_tex(raw: str, source_dir: Path) -> Path:
    raw = raw.strip()
    candidate = (source_dir / raw).expanduser()
    if candidate.suffix:
        return candidate.resolve()
    return candidate.with_suffix(".tex").resolve()


def parse_graphic_paths(view: str, source_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for m in GRAPHICSPATH_RE.finditer(view):
        for item in re.findall(r"\{([^{}]*)\}", m.group("body")):
            paths.append((source_dir / item).resolve())
    return paths


def resolve_graphic(raw: str, source_dir: Path, graphic_paths: Iterable[Path]) -> Path | None:
    raw = raw.strip()
    bases = [source_dir, *graphic_paths]
    raw_path = Path(raw)
    for base in bases:
        candidate = (base / raw_path).resolve()
        if candidate.suffix and candidate.exists():
            return candidate
        if not candidate.suffix:
            for ext in GRAPHIC_EXTS:
                p = candidate.with_suffix(ext)
                if p.exists():
                    return p.resolve()
    return None


def count_math(view: str) -> dict[str, int]:
    escaped = re.sub(r"\\\$", "", view)
    dollars = len(re.findall(r"(?<!\$)\$(?!\$)", escaped)) // 2
    display_dollars = len(re.findall(r"\$\$", escaped)) // 2
    inline_paren = len(re.findall(r"\\\(", view))
    display_bracket = len(re.findall(r"\\\[", view))
    math_envs = Counter(ENV_BEGIN_RE.findall(view))
    named = sum(math_envs[e] for e in ("equation", "equation*", "align", "align*", "gather", "gather*", "multline", "multline*", "displaymath"))
    return {
        "inline_estimate": dollars + inline_paren,
        "display_estimate": display_dollars + display_bracket + named,
        "named_math_environments": named,
    }


def inventory(entry: Path) -> dict:
    entry = entry.resolve()
    if not entry.exists():
        raise FileNotFoundError(entry)
    project_root = entry.parent
    queue = [entry]
    visited: set[Path] = set()
    files: list[FileRecord] = []
    dependencies: list[Dependency] = []
    aggregate_envs: Counter[str] = Counter()
    aggregate_commands: Counter[str] = Counter()
    macro_defs: set[str] = set()
    env_defs: set[str] = set()
    packages: Counter[str] = Counter()
    documentclasses: list[dict] = []
    labels: list[dict] = []
    references: list[dict] = []
    citations: list[dict] = []
    math_totals = Counter()
    graphic_count = 0
    table_count = 0
    figure_count = 0

    while queue:
        path = queue.pop(0).resolve()
        if path in visited:
            continue
        visited.add(path)
        text, encoding = read_text(path)
        view = lexical_view(text)
        rel = path.relative_to(project_root).as_posix() if path.is_relative_to(project_root) else str(path)
        files.append(FileRecord(
            path=rel,
            sha256=sha256_file(path),
            size=path.stat().st_size,
            line_count=text.count("\n") + 1,
            encoding=encoding,
            arabic_chars=len(ARABIC_RE.findall(text)),
            persian_specific_chars=len(PERSIAN_SPECIFIC_RE.findall(text)),
            zwnj_count=text.count("\u200c"),
            replacement_chars=text.count("\ufffd"),
        ))

        envs = ENV_BEGIN_RE.findall(view)
        aggregate_envs.update(envs)
        aggregate_commands.update(COMMAND_RE.findall(view))
        macro_defs.update(MACRO_DEF_RE.findall(view))
        env_defs.update(ENV_DEF_RE.findall(view))
        for opts, cls in DOCUMENTCLASS_RE.findall(view):
            documentclasses.append({"file": rel, "class": cls, "options": opts})
        for opts, pkg_group in PACKAGE_RE.findall(view):
            for pkg in pkg_group.split(","):
                packages[pkg.strip()] += 1
        for k, v in count_math(view).items():
            math_totals[k] += v
        table_count += sum(1 for e in envs if e in {"tabular", "tabularx", "longtable", "array", "supertabular"})
        figure_count += sum(1 for e in envs if e in {"figure", "figure*", "wrapfigure", "subfigure"})

        for m in LABEL_RE.finditer(view):
            labels.append({"file": rel, "line": line_number(view, m.start()), "label": m.group(1)})
        for m in REF_RE.finditer(view):
            references.append({"file": rel, "line": line_number(view, m.start()), "command": m.group(1), "label": m.group(2)})
        for m in CITE_RE.finditer(view):
            for key in m.group(1).split(","):
                citations.append({"file": rel, "line": line_number(view, m.start()), "key": key.strip()})

        for m in INCLUDE_RE.finditer(view):
            child = resolve_tex(m.group("path"), path.parent)
            exists = child.exists()
            dependencies.append(Dependency("tex", m.group("cmd"), rel, line_number(view, m.start()), m.group("path"), str(child), exists))
            if exists and child not in visited:
                queue.append(child)

        graphic_paths = parse_graphic_paths(view, path.parent)
        for m in GRAPHIC_RE.finditer(view):
            resolved = resolve_graphic(m.group("path"), path.parent, graphic_paths)
            dependencies.append(Dependency("graphic", "includegraphics", rel, line_number(view, m.start()), m.group("path"), str(resolved) if resolved else None, bool(resolved)))
            graphic_count += 1

        for m in BIB_RE.finditer(view):
            for raw in m.group("path").split(","):
                raw = raw.strip()
                candidate = (path.parent / raw).resolve()
                if not candidate.suffix:
                    candidate = candidate.with_suffix(".bib")
                dependencies.append(Dependency("bibliography", "bibliography", rel, line_number(view, m.start()), raw, str(candidate), candidate.exists()))

    used_commands = set(aggregate_commands)
    unknown = sorted(c for c in used_commands if c not in STANDARD_COMMANDS and c not in macro_defs and len(c) > 1)
    missing = [asdict(d) for d in dependencies if not d.exists]
    duplicate_labels = sorted(k for k, v in Counter(x["label"] for x in labels).items() if v > 1)
    unresolved_refs = sorted({x["label"] for x in references} - {x["label"] for x in labels})
    persian_signals = {
        "xepersian": "xepersian" in packages,
        "bidi": "bidi" in packages,
        "polyglossia": "polyglossia" in packages,
        "arabic_character_count": sum(f.arabic_chars for f in files),
        "persian_specific_character_count": sum(f.persian_specific_chars for f in files),
        "zwnj_count": sum(f.zwnj_count for f in files),
        "direction_commands": {k: aggregate_commands[k] for k in ("lr", "rl", "textLR", "textRL", "LTR", "RTL") if aggregate_commands[k]},
    }
    return {
        "schema_version": 1,
        "entry": str(entry),
        "project_root": str(project_root),
        "files": [asdict(f) for f in sorted(files, key=lambda x: x.path)],
        "dependencies": [asdict(d) for d in dependencies],
        "missing_dependencies": missing,
        "documentclasses": documentclasses,
        "packages": dict(sorted(packages.items())),
        "custom_macros": sorted(macro_defs),
        "custom_environments": sorted(env_defs),
        "unknown_commands_review": unknown,
        "environment_counts": dict(sorted(aggregate_envs.items())),
        "command_counts": dict(aggregate_commands.most_common()),
        "labels": labels,
        "duplicate_labels": duplicate_labels,
        "references": references,
        "unresolved_references": unresolved_refs,
        "citations": citations,
        "persian_signals": persian_signals,
        "counts": {
            "source_files": len(files),
            "figures": max(figure_count, graphic_count),
            "graphics_commands": graphic_count,
            "tables": table_count,
            "math_inline_estimate": math_totals["inline_estimate"],
            "math_display_estimate": math_totals["display_estimate"],
            "labels": len(labels),
            "references": len(references),
            "citations": len(citations),
        },
        "normalization": {"recommended": "NFC", "entry_is_nfc": unicodedata.normalize("NFC", read_text(entry)[0]) == read_text(entry)[0]},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = inventory(args.entry)
    except Exception as exc:
        print(f"inspect_latex: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
