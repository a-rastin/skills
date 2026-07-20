#!/usr/bin/env python3
"""Validate DOCX package integrity, Persian RTL metadata, and source-object counts."""
from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"w": W, "m": M, "a": A, "r": R, "pr": PKG_REL}
qn = lambda tag: f"{{{W}}}{tag}"
ARABIC_LETTER_RE = re.compile(r"[\u0621-\u063A\u0641-\u064A\u066E-\u06D3\u06FA-\u06FF\u0750-\u077F\u08A0-\u08FF]")
STORY_RE = re.compile(r"word/(?:document|header\d+|footer\d+|footnotes|endnotes|comments)\.xml$")


def issue(severity: str, code: str, message: str, **details) -> dict:
    return {"severity": severity, "code": code, "message": message, **details}


def source_part_for_rels(rels_name: str) -> str:
    p = PurePosixPath(rels_name)
    if rels_name == "_rels/.rels":
        return ""
    parts = list(p.parts)
    try:
        idx = parts.index("_rels")
    except ValueError:
        return ""
    name = parts[idx + 1]
    if not name.endswith(".rels"):
        return ""
    source_name = name[:-5]
    return str(PurePosixPath(*parts[:idx], source_name))


def resolve_rel_target(source_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    base = posixpath.dirname(source_part)
    return posixpath.normpath(posixpath.join(base, target))


def load_json(path: Path | None) -> dict | list | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def validate(docx_path: Path, inventory_path: Path | None = None, ledger_path: Path | None = None) -> dict:
    issues: list[dict] = []
    counts = Counter()
    inventory = load_json(inventory_path)
    ledger = load_json(ledger_path)
    try:
        zf = zipfile.ZipFile(docx_path, "r")
    except Exception as exc:
        return {"valid": False, "issues": [issue("error", "ZIP_OPEN_FAILED", str(exc))], "counts": {}}

    with zf:
        names = zf.namelist()
        name_set = set(names)
        duplicates = [n for n, c in Counter(names).items() if c > 1]
        if duplicates:
            issues.append(issue("error", "ZIP_DUPLICATE_MEMBERS", "Duplicate package members", members=duplicates))
        for required in ("[Content_Types].xml", "_rels/.rels", "word/document.xml"):
            if required not in name_set:
                issues.append(issue("error", "REQUIRED_PART_MISSING", f"Missing {required}", part=required))
        bad_zip_member = zf.testzip()
        if bad_zip_member:
            issues.append(issue("error", "ZIP_CRC_FAILED", "CRC failure", part=bad_zip_member))

        xml_roots: dict[str, etree._Element] = {}
        for name in names:
            if name.endswith((".xml", ".rels")):
                try:
                    xml_roots[name] = etree.fromstring(zf.read(name), etree.XMLParser(resolve_entities=False))
                    counts["xml_parts"] += 1
                except Exception as exc:
                    issues.append(issue("error", "XML_PARSE_FAILED", str(exc), part=name))

        for rels_name, root in xml_roots.items():
            if not rels_name.endswith(".rels"):
                continue
            source_part = source_part_for_rels(rels_name)
            for rel in root.xpath("/*[local-name()='Relationships']/*[local-name()='Relationship']"):
                if rel.get("TargetMode") == "External":
                    counts["external_relationships"] += 1
                    continue
                target = rel.get("Target", "")
                resolved = resolve_rel_target(source_part, target)
                if resolved not in name_set:
                    issues.append(issue("error", "BROKEN_RELATIONSHIP", "Internal relationship target missing", rels=rels_name, source=source_part, target=target, resolved=resolved, relationship_id=rel.get("Id")))
                else:
                    counts["internal_relationships"] += 1

        for name, root in xml_roots.items():
            if not STORY_RE.match(name):
                continue
            counts["story_parts"] += 1
            for p_idx, p in enumerate(root.xpath(".//w:p", namespaces=NS)):
                text = "".join(p.xpath(".//w:t/text()", namespaces=NS))
                if "\ufffd" in text:
                    issues.append(issue("error", "REPLACEMENT_CHARACTER", "Replacement character found", part=name, paragraph_index=p_idx, text_sample=text[:120]))
                if ARABIC_LETTER_RE.search(text):
                    counts["arabic_paragraphs"] += 1
                    pPr = p.find(qn("pPr"))
                    bidi = pPr.find(qn("bidi")) if pPr is not None else None
                    if bidi is None or bidi.get(qn("val"), "1") in {"0", "false", "off"}:
                        issues.append(issue("error", "RTL_PARAGRAPH_MISSING", "Arabic-script paragraph lacks active w:bidi", part=name, paragraph_index=p_idx, text_sample=text[:120]))
                for r_idx, r in enumerate(p.xpath(".//w:r", namespaces=NS)):
                    rtext = "".join(r.xpath(".//w:t/text()", namespaces=NS))
                    if not ARABIC_LETTER_RE.search(rtext):
                        continue
                    counts["arabic_runs"] += 1
                    rPr = r.find(qn("rPr"))
                    rtl = rPr.find(qn("rtl")) if rPr is not None else None
                    lang = rPr.find(qn("lang")) if rPr is not None else None
                    if rtl is None or rtl.get(qn("val"), "1") in {"0", "false", "off"}:
                        issues.append(issue("error", "RTL_RUN_MISSING", "Arabic-script run lacks active w:rtl", part=name, paragraph_index=p_idx, run_index=r_idx, text_sample=rtext[:120]))
                    if lang is None or not lang.get(qn("bidi"), "").lower().startswith(("fa", "ar")):
                        issues.append(issue("error", "RTL_LANGUAGE_MISSING", "Arabic-script run lacks bidi language", part=name, paragraph_index=p_idx, run_index=r_idx, text_sample=rtext[:120]))
            for t_idx, tbl in enumerate(root.xpath(".//w:tbl", namespaces=NS)):
                counts["tables"] += 1
                text = "".join(tbl.xpath(".//w:t/text()", namespaces=NS))
                if ARABIC_LETTER_RE.search(text):
                    tblPr = tbl.find(qn("tblPr"))
                    bidi = tblPr.find(qn("bidiVisual")) if tblPr is not None else None
                    if bidi is None or bidi.get(qn("val"), "1") in {"0", "false", "off"}:
                        issues.append(issue("error", "RTL_TABLE_MISSING", "Arabic-script table lacks active w:bidiVisual", part=name, table_index=t_idx))

            counts["math_objects"] += len(root.xpath(".//m:oMath", namespaces=NS))
            counts["math_paragraphs"] += len(root.xpath(".//m:oMathPara", namespaces=NS))
            counts["image_blips"] += len(root.xpath(".//a:blip", namespaces=NS))
            counts["headings"] += len(root.xpath(".//w:p[w:pPr/w:pStyle[starts-with(@w:val, 'Heading')]]", namespaces=NS))
            counts["footnote_references"] += len(root.xpath(".//w:footnoteReference", namespaces=NS))

        for name in names:
            if name.startswith("word/media/"):
                counts["media_files"] += 1
                if len(zf.read(name)) == 0:
                    issues.append(issue("error", "EMPTY_MEDIA", "Media file is empty", part=name))

    fallback_counts = Counter()
    unresolved_counts = Counter()
    if isinstance(ledger, list):
        entries = ledger
    elif isinstance(ledger, dict):
        entries = ledger.get("entries", [])
    else:
        entries = []
    for entry in entries:
        kind = entry.get("kind", "unknown")
        rep = entry.get("representation", "")
        status = entry.get("status", "")
        if "fallback" in rep:
            fallback_counts[kind] += 1
        if status == "unresolved" or rep == "unresolved":
            unresolved_counts[kind] += 1

    if isinstance(inventory, dict):
        src = inventory.get("counts", {})
        checks = [
            ("tables", int(src.get("tables", 0)), counts["tables"], fallback_counts["table"] + fallback_counts["tables"]),
            ("figures", int(src.get("figures", 0)), counts["image_blips"], fallback_counts["figure"] + fallback_counts["figures"]),
        ]
        src_math = int(src.get("math_inline_estimate", 0)) + int(src.get("math_display_estimate", 0))
        checks.append(("math", src_math, counts["math_objects"], fallback_counts["math"] + fallback_counts["equation"]))
        reconciliation = []
        for kind, source_count, native_count, fallback_count in checks:
            row = {"kind": kind, "source": source_count, "native": native_count, "fallback": fallback_count, "unresolved": unresolved_counts[kind]}
            reconciliation.append(row)
            if source_count > native_count + fallback_count + unresolved_counts[kind]:
                issues.append(issue("error", "COUNT_MISMATCH", f"Source {kind} exceed DOCX native+fallback+unresolved", **row))
        counts["reconciliation_checks"] = len(reconciliation)
    else:
        reconciliation = []

    errors = sum(1 for x in issues if x["severity"] == "error")
    warnings = sum(1 for x in issues if x["severity"] == "warning")
    return {
        "valid": errors == 0,
        "errors": errors,
        "warnings": warnings,
        "counts": dict(counts),
        "reconciliation": reconciliation,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docx", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    report = validate(args.docx, args.inventory, args.ledger)
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 2 if args.strict and not report["valid"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
