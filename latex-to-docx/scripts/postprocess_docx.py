#!/usr/bin/env python3
"""Apply idempotent Persian RTL, language, font, and table patches to DOCX XML."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XML = "http://www.w3.org/XML/1998/namespace"
NS = {"w": W, "m": M}
qn = lambda tag: f"{{{W}}}{tag}"
ARABIC_LETTER_RE = re.compile(r"[\u0621-\u063A\u0641-\u064A\u066E-\u06D3\u06FA-\u06FF\u0750-\u077F\u08A0-\u08FF]")
LATIN_LETTER_RE = re.compile(r"[A-Za-z]")
URL_RE = re.compile(r"(?:https?://|www\.|\b\w+[.-]\w+@|\bdoi:)\S*", re.I)
STORY_RE = re.compile(r"word/(?:document|header\d+|footer\d+|footnotes|endnotes|comments)\.xml$")
CENTER_STYLES = {"Title", "Subtitle", "Author", "Date", "Caption", "TableCaption", "FigureCaption"}
LEFT_STYLES = {"SourceCode", "CodeBlock", "Verbatim", "VerbatimChar"}



ORDER_MAP = {
    "tblPr": ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription", "tblPrChange"],
    "pPr": ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"],
    "rPr": ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline", "shadow", "emboss", "imprint", "noProof", "snapToGrid", "vanish", "webHidden", "color", "spacing", "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath", "rPrChange"],
    "tcPr": ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark", "headers", "cellIns", "cellDel", "cellMerge", "tcPrChange"],
}

def reorder_children(parent: etree._Element) -> None:
    local = etree.QName(parent).localname
    order = ORDER_MAP.get(local)
    if not order:
        return
    rank = {name: i for i, name in enumerate(order)}
    children = list(parent)
    indexed = list(enumerate(children))
    indexed.sort(key=lambda pair: (rank.get(etree.QName(pair[1]).localname, len(rank)), pair[0]))
    for child in children:
        parent.remove(child)
    for _, child in indexed:
        parent.append(child)

def ensure(parent: etree._Element, tag: str, first: bool = False) -> etree._Element:
    child = parent.find(qn(tag))
    if child is None:
        child = etree.Element(qn(tag))
        if first:
            parent.insert(0, child)
        else:
            parent.append(child)
    return child


def set_onoff(parent: etree._Element, tag: str, value: bool) -> etree._Element:
    node = ensure(parent, tag)
    node.set(qn("val"), "1" if value else "0")
    return node


def paragraph_text(p: etree._Element) -> str:
    return "".join(p.xpath(".//w:t/text()", namespaces=NS))


def run_text(r: etree._Element) -> str:
    return "".join(r.xpath(".//w:t/text()", namespaces=NS))


def classify(text: str) -> str:
    if ARABIC_LETTER_RE.search(text):
        return "rtl"
    if LATIN_LETTER_RE.search(text) or URL_RE.search(text):
        return "ltr"
    return "neutral"


def patch_run(r: etree._Element, paragraph_dir: str, main_lang: str, latin_lang: str, persian_font: str, latin_font: str, mono_font: str) -> str:
    text = run_text(r)
    direction = classify(text)
    if not text or direction == "neutral":
        return direction
    rPr = r.find(qn("rPr"))
    if rPr is None:
        rPr = etree.Element(qn("rPr"))
        r.insert(0, rPr)
    is_rtl = direction == "rtl"
    set_onoff(rPr, "rtl", is_rtl)
    lang = ensure(rPr, "lang")
    lang.set(qn("val"), main_lang if is_rtl else latin_lang)
    if is_rtl:
        lang.set(qn("bidi"), main_lang)
    fonts = ensure(rPr, "rFonts")
    is_code = any(x in text for x in ("/", "\\", "::", "=>")) and not is_rtl
    lfont = mono_font if is_code else latin_font
    fonts.set(qn("ascii"), lfont)
    fonts.set(qn("hAnsi"), lfont)
    fonts.set(qn("cs"), persian_font)
    fonts.set(qn("eastAsia"), persian_font if is_rtl else lfont)
    reorder_children(rPr)
    return direction


def patch_paragraph(p: etree._Element, main_lang: str, latin_lang: str, persian_font: str, latin_font: str, mono_font: str, force_explicit_ltr: bool) -> Counter:
    stats = Counter()
    text = paragraph_text(p)
    pdir = classify(text)
    pPr = p.find(qn("pPr"))
    if pPr is None and (pdir == "rtl" or force_explicit_ltr):
        pPr = etree.Element(qn("pPr"))
        p.insert(0, pPr)
    if pPr is not None:
        if pdir == "rtl":
            set_onoff(pPr, "bidi", True)
            jc = pPr.find(qn("jc"))
            style_nodes = pPr.findall(qn("pStyle"))
            style_id = style_nodes[0].get(qn("val"), "") if style_nodes else ""
            if jc is None:
                jc = etree.SubElement(pPr, qn("jc"))
                if style_id in CENTER_STYLES:
                    jc.set(qn("val"), "center")
                elif style_id in LEFT_STYLES:
                    jc.set(qn("val"), "left")
                else:
                    jc.set(qn("val"), "right")
            stats["rtl_paragraphs"] += 1
        elif force_explicit_ltr and text.strip():
            set_onoff(pPr, "bidi", False)
            stats["ltr_paragraphs"] += 1
    for r in p.xpath(".//w:r", namespaces=NS):
        direction = patch_run(r, pdir, main_lang, latin_lang, persian_font, latin_font, mono_font)
        if direction == "rtl":
            stats["rtl_runs"] += 1
        elif direction == "ltr":
            stats["ltr_runs"] += 1
    if pPr is not None:
        reorder_children(pPr)
    return stats


def patch_story(root: etree._Element, main_lang: str, latin_lang: str, persian_font: str, latin_font: str, mono_font: str, rtl_tables: str, force_explicit_ltr: bool) -> Counter:
    stats = Counter()
    for p in root.xpath(".//w:p", namespaces=NS):
        stats.update(patch_paragraph(p, main_lang, latin_lang, persian_font, latin_font, mono_font, force_explicit_ltr))
    for tbl in root.xpath(".//w:tbl", namespaces=NS):
        text = "".join(tbl.xpath(".//w:t/text()", namespaces=NS))
        should_rtl = rtl_tables == "all" or (rtl_tables == "auto" and ARABIC_LETTER_RE.search(text) is not None)
        tblPr = tbl.find(qn("tblPr"))
        if tblPr is None:
            tblPr = etree.Element(qn("tblPr"))
            tbl.insert(0, tblPr)
        if should_rtl:
            set_onoff(tblPr, "bidiVisual", True)
            stats["rtl_tables"] += 1
        elif rtl_tables == "none":
            existing = tblPr.find(qn("bidiVisual"))
            if existing is not None:
                tblPr.remove(existing)

        # Give renderers deterministic table geometry. Pandoc often emits only
        # tblGrid widths; LibreOffice can collapse RTL auto-width cells without tcW.
        grid_widths = []
        grid = tbl.find(qn("tblGrid"))
        if grid is not None:
            for col in grid.findall(qn("gridCol")):
                try:
                    grid_widths.append(int(col.get(qn("w"), "0")))
                except ValueError:
                    grid_widths.append(0)
        if grid_widths and sum(grid_widths) > 0:
            tblW = ensure(tblPr, "tblW")
            tblW.set(qn("type"), "dxa")
            tblW.set(qn("w"), str(sum(grid_widths)))
            layout = ensure(tblPr, "tblLayout")
            layout.set(qn("type"), "fixed")
            jc = ensure(tblPr, "jc")
            jc.set(qn("val"), "center")
            for tr in tbl.findall(qn("tr")):
                col_index = 0
                for tc in tr.findall(qn("tc")):
                    tcPr = tc.find(qn("tcPr"))
                    if tcPr is None:
                        tcPr = etree.Element(qn("tcPr"))
                        tc.insert(0, tcPr)
                    span_node = tcPr.find(qn("gridSpan"))
                    try:
                        span = int(span_node.get(qn("val"), "1")) if span_node is not None else 1
                    except ValueError:
                        span = 1
                    width = sum(grid_widths[col_index:col_index + span])
                    if width > 0:
                        tcW = ensure(tcPr, "tcW")
                        tcW.set(qn("type"), "dxa")
                        tcW.set(qn("w"), str(width))
                    reorder_children(tcPr)
                    col_index += span
        reorder_children(tblPr)
    return stats


def patch_settings(root: etree._Element, main_lang: str, latin_lang: str):
    theme = root.find(qn("themeFontLang"))
    if theme is None:
        theme = etree.SubElement(root, qn("themeFontLang"))
    theme.set(qn("val"), latin_lang)
    theme.set(qn("eastAsia"), latin_lang)
    theme.set(qn("bidi"), main_lang)
    update = root.find(qn("updateFields"))
    if update is None:
        update = etree.SubElement(root, qn("updateFields"))
    update.set(qn("val"), "true")


def patch_styles(root: etree._Element, main_lang: str, latin_lang: str, persian_font: str, latin_font: str):
    # Patch document defaults for future/uncategorized runs. Paragraph direction is
    # applied directly in story parts to avoid forcing English-only paragraphs RTL.
    doc_defaults = root.find(qn("docDefaults"))
    if doc_defaults is None:
        doc_defaults = etree.SubElement(root, qn("docDefaults"))
    rpr_default = ensure(doc_defaults, "rPrDefault")
    rpr = ensure(rpr_default, "rPr")
    fonts = ensure(rpr, "rFonts")
    fonts.set(qn("ascii"), latin_font)
    fonts.set(qn("hAnsi"), latin_font)
    fonts.set(qn("cs"), persian_font)
    fonts.set(qn("eastAsia"), persian_font)
    lang = ensure(rpr, "lang")
    lang.set(qn("val"), latin_lang)
    lang.set(qn("eastAsia"), latin_lang)
    lang.set(qn("bidi"), main_lang)
    reorder_children(rpr)


def process_docx(input_path: Path, output_path: Path, main_lang: str = "fa-IR", latin_lang: str = "en-US", persian_font: str = "Noto Naskh Arabic", latin_font: str = "Liberation Serif", mono_font: str = "DejaVu Sans Mono", rtl_tables: str = "auto", force_explicit_ltr: bool = False) -> dict:
    input_path = input_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    stats = Counter()
    with zipfile.ZipFile(input_path, "r") as zin:
        infos = zin.infolist()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx", dir=output_path.parent) as tmp:
            tmp_path = Path(tmp.name)
        try:
            with zipfile.ZipFile(tmp_path, "w") as zout:
                for info in infos:
                    data = zin.read(info.filename)
                    if info.filename.endswith(".xml") and (STORY_RE.match(info.filename) or info.filename in {"word/settings.xml", "word/styles.xml"}):
                        parser = etree.XMLParser(remove_blank_text=False, resolve_entities=False)
                        root = etree.fromstring(data, parser)
                        if STORY_RE.match(info.filename):
                            part_stats = patch_story(root, main_lang, latin_lang, persian_font, latin_font, mono_font, rtl_tables, force_explicit_ltr)
                            stats.update(part_stats)
                            stats["story_parts"] += 1
                        elif info.filename == "word/settings.xml":
                            patch_settings(root, main_lang, latin_lang)
                        elif info.filename == "word/styles.xml":
                            patch_styles(root, main_lang, latin_lang, persian_font, latin_font)
                        data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
                    zout.writestr(info, data)
            os.replace(tmp_path, output_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
    return dict(stats)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--main-lang", default="fa-IR")
    parser.add_argument("--latin-lang", default="en-US")
    parser.add_argument("--persian-font", default="Noto Naskh Arabic")
    parser.add_argument("--latin-font", default="Liberation Serif")
    parser.add_argument("--mono-font", default="DejaVu Sans Mono")
    parser.add_argument("--rtl-tables", choices=["auto", "all", "none"], default="auto")
    parser.add_argument("--force-explicit-ltr", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    stats = process_docx(args.input, args.output, args.main_lang, args.latin_lang, args.persian_font, args.latin_font, args.mono_font, args.rtl_tables, args.force_explicit_ltr)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
