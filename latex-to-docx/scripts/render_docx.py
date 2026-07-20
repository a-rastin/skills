#!/usr/bin/env python3
"""Render DOCX to PDF and per-page PNGs using LibreOffice and pdftoppm."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(cmd: list[str], *, cwd: Path | None = None, env: dict | None = None, timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)


def render(docx: Path, output_dir: Path, dpi: int = 160, emit_pdf: bool = True) -> dict:
    docx = docx.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    libreoffice = shutil.which("libreoffice") or shutil.which("soffice")
    pdftoppm = shutil.which("pdftoppm")
    if not libreoffice:
        raise RuntimeError("LibreOffice/soffice not found")
    if not pdftoppm:
        raise RuntimeError("pdftoppm not found")
    with tempfile.TemporaryDirectory(prefix="latex-to-docx-render-") as td:
        temp = Path(td)
        home = temp / "home"
        profile = temp / "profile"
        home.mkdir()
        profile.mkdir()
        env = os.environ.copy()
        env["HOME"] = str(home)
        env["TMPDIR"] = str(temp)
        profile_uri = profile.resolve().as_uri()
        proc = run([
            libreoffice,
            "--headless",
            f"-env:UserInstallation={profile_uri}",
            "--convert-to", "pdf",
            "--outdir", str(output_dir),
            str(docx),
        ], env=env)
        pdf = output_dir / f"{docx.stem}.pdf"
        if proc.returncode != 0 or not pdf.exists() or pdf.stat().st_size == 0:
            raise RuntimeError(f"LibreOffice render failed (code {proc.returncode}): {proc.stderr.strip()} {proc.stdout.strip()}")
        prefix = output_dir / "page"
        ppm = run([pdftoppm, "-png", "-r", str(dpi), str(pdf), str(prefix)])
        if ppm.returncode != 0:
            raise RuntimeError(f"pdftoppm failed: {ppm.stderr.strip()}")
        generated = sorted(output_dir.glob("page-*.png"))
        if not generated:
            raise RuntimeError("No page PNGs generated")
        final_pdf = pdf
        if not emit_pdf:
            pdf.unlink(missing_ok=True)
            final_pdf = None
        return {
            "docx": str(docx),
            "pdf": str(final_pdf) if final_pdf else None,
            "pages": [str(p) for p in generated],
            "page_count": len(generated),
            "dpi": dpi,
            "libreoffice_stdout": proc.stdout,
            "libreoffice_stderr": proc.stderr,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--emit-pdf", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = render(args.docx, args.output_dir, args.dpi, args.emit_pdf)
    except Exception as exc:
        print(f"render_docx: {exc}", file=__import__("sys").stderr)
        return 2
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
