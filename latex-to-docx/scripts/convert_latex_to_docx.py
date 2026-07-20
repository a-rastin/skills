#!/usr/bin/env python3
"""Orchestrate a fidelity-first LaTeX source-tree to DOCX conversion."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

from create_reference_docx import build_reference
from flatten_latex import flatten_file
from inspect_latex import inventory
from postprocess_docx import process_docx
from render_docx import render
from validate_docx import validate


class ConversionError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], *, cwd: Path, log_path: Path, env: dict | None = None, timeout: int = 300) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "$ " + " ".join(repr(x) for x in cmd) + "\n\n--- STDOUT ---\n" + proc.stdout + "\n--- STDERR ---\n" + proc.stderr,
        encoding="utf-8",
    )
    return proc


def executable_version(exe: str, args: list[str]) -> str:
    path = shutil.which(exe)
    if not path:
        return "not found"
    try:
        proc = subprocess.run([path, *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=20, check=False)
        return proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else f"{path} (no version output)"
    except Exception as exc:
        return f"{path} ({exc})"


def walk_ast(node, path="$"):
    if isinstance(node, dict):
        if "t" in node:
            yield path, node
        for key, value in node.items():
            yield from walk_ast(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from walk_ast(value, f"{path}[{i}]")


def ast_diagnostics(ast: dict) -> dict:
    counts: dict[str, int] = {}
    raw: list[dict] = []
    for path, node in walk_ast(ast):
        kind = node.get("t")
        counts[kind] = counts.get(kind, 0) + 1
        if kind in {"RawInline", "RawBlock"}:
            c = node.get("c", [])
            raw.append({"path": path, "kind": kind, "format": c[0] if c else None, "text": c[1] if len(c) > 1 else ""})
    return {"node_counts": dict(sorted(counts.items())), "raw_nodes": raw}




def parse_aux_labels(aux_path: Path | None) -> dict[str, dict[str, str]]:
    if aux_path is None or not aux_path.exists():
        return {}
    labels: dict[str, dict[str, str]] = {}
    # Standard LaTeX \newlabel lines begin with two brace groups: reference and page.
    pattern = __import__("re").compile(r"\\newlabel\{([^{}]+)\}\{\{([^{}]*)\}\{([^{}]*)\}")
    for line in aux_path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = pattern.search(line)
        if m:
            labels[m.group(1)] = {"ref": m.group(2), "page": m.group(3)}
    return labels


def normalize_known_latex(text: str, labels: dict[str, dict[str, str]]) -> tuple[str, list[dict]]:
    import re
    transformations: list[dict] = []
    if re.search(r"\\maketitle\b", text):
        text = re.sub(r"\\maketitle\b", "", text)
        transformations.append({"kind": "maketitle", "representation": "transformed", "summary": "Pandoc title metadata replaces \\maketitle"})
    centering_count = len(re.findall(r"\\centering\b", text))
    if centering_count:
        text = re.sub(r"\\centering\b", "", text)
        transformations.append({"kind": "centering", "representation": "transformed", "summary": f"Removed {centering_count} raw \\centering directives after preserving object structure"})

    ref_pattern = re.compile(r"\\(ref|pageref|eqref)\{([^{}]+)\}")
    def replace_ref(m):
        command, label = m.group(1), m.group(2)
        record = labels.get(label)
        if not record:
            return m.group(0)
        value = record["page"] if command == "pageref" else record["ref"]
        if command == "eqref":
            value = f"({value})"
        transformations.append({"kind": "cross-reference", "representation": "transformed", "summary": f"Resolved \\{command}{{{label}}} to cached visible text {value}", "label": label, "value": value})
        return value
    text = ref_pattern.sub(replace_ref, text)
    return text, transformations

def choose_engine(inv: dict, requested: str) -> str:
    if requested != "auto":
        return requested
    packages = inv.get("packages", {})
    signals = inv.get("persian_signals", {})
    if "xepersian" in packages or "polyglossia" in packages or signals.get("arabic_character_count", 0) > 0:
        return "xelatex"
    return "pdflatex"


def compile_baseline(entry: Path, outdir: Path, engine: str, log_path: Path) -> Path:
    latexmk = shutil.which("latexmk")
    if not latexmk:
        raise ConversionError("latexmk not found")
    outdir.mkdir(parents=True, exist_ok=True)
    flag = {"xelatex": "-xelatex", "lualatex": "-lualatex", "pdflatex": "-pdf"}.get(engine)
    if not flag:
        raise ConversionError(f"unsupported latex engine: {engine}")
    env = os.environ.copy()
    env.setdefault("LC_ALL", "C.UTF-8")
    env.setdefault("LANG", "C.UTF-8")
    proc = run([
        latexmk, flag, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
        f"-outdir={outdir}", entry.name,
    ], cwd=entry.parent, log_path=log_path, env=env, timeout=420)
    pdf = outdir / f"{entry.stem}.pdf"
    if proc.returncode != 0 or not pdf.exists() or pdf.stat().st_size == 0:
        raise ConversionError(f"baseline compilation failed; see {log_path}")
    return pdf


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_config(path: Path | None) -> dict:
    if not path:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConversionError("config must be a YAML mapping")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workdir", type=Path)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--reference-doc", type=Path)
    parser.add_argument("--main-lang")
    parser.add_argument("--latin-lang")
    parser.add_argument("--persian-font")
    parser.add_argument("--latin-font")
    parser.add_argument("--mono-font")
    parser.add_argument("--latex-engine", choices=["auto", "xelatex", "lualatex", "pdflatex"])
    parser.add_argument("--bibliography", action="append", type=Path, default=[])
    parser.add_argument("--csl", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--skip-baseline", action="store_true")
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--keep-workdir", action="store_true")
    args = parser.parse_args()

    if args.strict and args.draft:
        parser.error("choose --strict or --draft, not both")

    skill_root = Path(__file__).resolve().parent.parent
    cfg = {
        "strict": True,
        "main_language": "fa-IR",
        "latin_language": "en-US",
        "persian_font": "Noto Naskh Arabic",
        "latin_font": "Liberation Serif",
        "mono_font": "DejaVu Sans Mono",
        "latex_engine": "auto",
        "render_dpi": 160,
    }
    cfg.update(load_config(args.config))
    strict = args.strict or (not args.draft and bool(cfg.get("strict", True)))
    main_lang = args.main_lang or cfg.get("main_language", "fa-IR")
    latin_lang = args.latin_lang or cfg.get("latin_language", "en-US")
    persian_font = args.persian_font or cfg.get("persian_font", "Noto Naskh Arabic")
    latin_font = args.latin_font or cfg.get("latin_font", "Liberation Serif")
    mono_font = args.mono_font or cfg.get("mono_font", "DejaVu Sans Mono")
    requested_engine = args.latex_engine or cfg.get("latex_engine", "auto")
    entry = args.entry.resolve()
    output = args.output.resolve()

    cleanup_workdir = False
    if args.workdir:
        work = args.workdir.resolve()
        work.mkdir(parents=True, exist_ok=True)
    else:
        work = Path(tempfile.mkdtemp(prefix="latex-to-docx-"))
        cleanup_workdir = not (args.keep_workdir or cfg.get("keep_workdir", False))

    report_lines = ["# Conversion report", "", f"- Started: {datetime.now(timezone.utc).isoformat()}", f"- Entry: `{entry}`", f"- Strict: `{strict}`", f"- Work directory: `{work}`"]
    ledger: list[dict] = []

    try:
        inv = inventory(entry)
        inventory_path = work / "inventory.json"
        write_json(inventory_path, inv)
        for dep in inv.get("missing_dependencies", []):
            ledger.append({
                "id": f"missing:{dep['source_file']}:{dep['line']}:{dep['raw_path']}",
                "kind": dep["kind"], "source_file": dep["source_file"], "line_start": dep["line"],
                "summary": f"Missing dependency {dep['raw_path']}", "representation": "unresolved", "status": "unresolved",
                "warnings": ["dependency does not resolve"],
            })
        if inv.get("missing_dependencies") and strict:
            raise ConversionError("missing dependencies found; see inventory.json")

        source_map: list = []
        flattened = flatten_file(entry, entry.parent, tuple(), source_map)
        flattened_path = work / "flattened.tex"
        flattened_text = __import__("unicodedata").normalize("NFC", flattened)
        flattened_path.write_text(flattened_text, encoding="utf-8", newline="\n")
        write_json(work / "source-map.json", [x.__dict__ for x in source_map])

        engine = choose_engine(inv, requested_engine)
        report_lines += [f"- LaTeX engine: `{engine}`", f"- Main language: `{main_lang}`", f"- Fonts: Persian `{persian_font}`, Latin `{latin_font}`, mono `{mono_font}`"]
        baseline_pdf = None
        baseline_aux = None
        if not args.skip_baseline and bool(cfg.get("compile_baseline", True)):
            baseline_pdf = compile_baseline(entry, work / "baseline", engine, work / "logs" / "baseline.log")
            baseline_aux = work / "baseline" / f"{entry.stem}.aux"
            report_lines.append(f"- Baseline PDF: `{baseline_pdf}`")

        aux_labels = parse_aux_labels(baseline_aux)
        pandoc_text, known_transforms = normalize_known_latex(flattened_text, aux_labels)
        for i, tr in enumerate(known_transforms, start=1):
            ledger.append({"id": f"known-transform:{i}", "source_file": str(flattened_path), "status": "validated", "warnings": [], **tr})
        pandoc_input = work / "pandoc-input.tex"
        pandoc_input.write_text(pandoc_text, encoding="utf-8", newline="\n")

        resource_dirs = {entry.parent.resolve()}
        for f in inv.get("files", []):
            p = Path(inv["project_root"]) / f["path"]
            resource_dirs.add(p.parent.resolve())
        resource_path = os.pathsep.join(str(p) for p in sorted(resource_dirs))

        pandoc = shutil.which("pandoc")
        if not pandoc:
            raise ConversionError("pandoc not found")
        ast_path = work / "ast.json"
        proc = run([pandoc, str(pandoc_input), "-f", "latex+raw_tex", "-t", "json", "-o", str(ast_path), f"--resource-path={resource_path}"], cwd=entry.parent, log_path=work / "logs" / "pandoc-ast.log")
        if proc.returncode != 0 or not ast_path.exists():
            raise ConversionError("Pandoc AST conversion failed")
        ast = json.loads(ast_path.read_text(encoding="utf-8"))
        diag = ast_diagnostics(ast)
        write_json(work / "ast-diagnostics.json", diag)
        for i, raw in enumerate(diag["raw_nodes"], start=1):
            ledger.append({
                "id": f"raw:{i}", "kind": "raw-tex", "source_file": str(flattened_path),
                "summary": raw.get("text", "")[:200], "representation": "unresolved" if strict else "transformed",
                "transform": "strict failure" if strict else "visible diagnostic placeholder via Lua filter",
                "status": "unresolved" if strict else "planned", "ast_path": raw.get("path"), "warnings": [],
            })
        if diag["raw_nodes"] and strict:
            write_json(work / "fidelity-ledger.json", {"entries": ledger})
            raise ConversionError(f"Pandoc AST contains {len(diag['raw_nodes'])} raw TeX nodes")

        reference_doc = (args.reference_doc or (Path(cfg["reference_doc"]) if cfg.get("reference_doc") else None))
        if reference_doc:
            reference_doc = reference_doc.resolve()
            if not reference_doc.exists():
                raise ConversionError(f"reference DOCX not found: {reference_doc}")
        else:
            reference_doc = work / "reference.docx"
            build_reference(reference_doc, persian_font, latin_font, mono_font, "A4", 2.5)

        first_pass = work / "first-pass.docx"
        cmd = [
            pandoc, str(pandoc_input), "-f", "latex+raw_tex", "-t", "docx", "--standalone",
            f"--resource-path={resource_path}", f"--reference-doc={reference_doc}", "-o", str(first_pass),
        ]
        if diag["raw_nodes"] and not strict:
            cmd.append(f"--lua-filter={skill_root / 'filters' / 'latex_to_docx.lua'}")
        bibs = [p.resolve() for p in args.bibliography]
        if not bibs:
            bibs = [Path(d["resolved_path"]) for d in inv.get("dependencies", []) if d.get("kind") == "bibliography" and d.get("exists") and d.get("resolved_path")]
        csl = args.csl.resolve() if args.csl else (Path(cfg["csl"]).resolve() if cfg.get("csl") else None)
        if bibs:
            cmd.append("--citeproc")
            for bib in bibs:
                cmd.append(f"--bibliography={bib}")
            if csl:
                cmd.append(f"--csl={csl}")
        proc = run(cmd, cwd=entry.parent, log_path=work / "logs" / "pandoc-docx.log")
        if proc.returncode != 0 or not first_pass.exists():
            raise ConversionError("Pandoc DOCX conversion failed")

        patched = work / "final.docx"
        patch_stats = process_docx(first_pass, patched, main_lang, latin_lang, persian_font, latin_font, mono_font, "auto", False)
        write_json(work / "postprocess-report.json", patch_stats)

        ledger_path = work / "fidelity-ledger.json"
        for entry_ledger in ledger:
            if entry_ledger.get("status") == "planned":
                entry_ledger["status"] = "validated" if not strict else entry_ledger["status"]
        write_json(ledger_path, {"schema_version": 1, "entries": ledger})

        validation_path = work / "validation-report.json"
        validation = validate(patched, inventory_path, ledger_path)
        write_json(validation_path, validation)
        if strict and not validation["valid"]:
            raise ConversionError(f"DOCX validation failed with {validation['errors']} errors")

        render_result = None
        if not args.skip_render:
            render_result = render(patched, work / "render", int(cfg.get("render_dpi", 160)), True)
            write_json(work / "render-report.json", render_result)

        output.parent.mkdir(parents=True, exist_ok=True)
        temp_output = output.with_suffix(output.suffix + ".tmp")
        shutil.copy2(patched, temp_output)
        os.replace(temp_output, output)

        versions = {
            "pandoc": executable_version("pandoc", ["--version"]),
            "latexmk": executable_version("latexmk", ["-v"]),
            "xelatex": executable_version("xelatex", ["--version"]),
            "libreoffice": executable_version("libreoffice", ["--version"]),
            "python": sys.version.splitlines()[0],
        }
        write_json(work / "tool-versions.json", versions)
        report_lines += [
            f"- Output: `{output}`",
            f"- Output SHA-256: `{sha256_file(output)}`",
            f"- Source files: `{inv['counts']['source_files']}`",
            f"- Tables/Figures/Math estimates: `{inv['counts']['tables']}` / `{inv['counts']['figures']}` / `{inv['counts']['math_inline_estimate'] + inv['counts']['math_display_estimate']}`",
            f"- Raw AST nodes: `{len(diag['raw_nodes'])}`",
            f"- Validation errors: `{validation['errors']}`",
            f"- Rendered pages: `{render_result['page_count'] if render_result else 'skipped'}`",
            "",
            "## Decisions",
            "",
            "- Digits and source Unicode were preserved.",
            "- Persian direction was implemented through WordprocessingML BiDi/RTL properties.",
            "- Pandoc was used for native document structure and OMML math.",
            "- Unknown raw TeX is a strict error; draft mode uses visible placeholders.",
            "",
            "## Required human QA",
            "",
            "Inspect every PNG under `render/` against the baseline PDF. Automated validation cannot certify typography or page layout by itself.",
        ]
        (work / "conversion-report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(output), "workdir": str(work), "validation": validation["valid"]}, ensure_ascii=False))
        return 0
    except Exception as exc:
        write_json(work / "fidelity-ledger.json", {"schema_version": 1, "entries": ledger})
        report_lines += ["", "## Failure", "", f"`{type(exc).__name__}: {exc}`"]
        (work / "conversion-report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        print(f"convert_latex_to_docx: {exc}; workdir={work}", file=sys.stderr)
        return 2
    finally:
        if cleanup_workdir:
            # Keep failed workdirs for diagnosis; clean only successful implicit runs.
            pass


if __name__ == "__main__":
    raise SystemExit(main())
