---
name: latex-to-docx
description: Fidelity-first conversion of LaTeX source trees—especially Persian and mixed RTL/LTR documents—into editable DOCX. Use when converting .tex projects, reconstructing equations, tables, figures, citations, and cross-references in Word, or validating a DOCX against a LaTeX source/PDF.
---

# LaTeX → DOCX

Use **fidelity** as the leading word: every source construct must be represented natively, represented by an explicit fallback, or recorded as unresolved. “Flawless” means **no unclassified loss** and a visually clean, semantically faithful DOCX; it does not mean identical line/page breaks between TeX and Word.

Read [`GRILLING.md`](GRILLING.md) before acting. Ask only questions whose answers materially change the conversion and cannot be inferred from the project. Record inferred defaults in the conversion report.

## Deliverables

For an actual conversion, produce:

1. `output.docx` — editable Word document.
2. `conversion-report.md` — inputs, decisions, commands, versions, warnings, and deviations.
3. `fidelity-ledger.json` — one entry for every nontrivial or unsupported construct.
4. `validation-report.json` — structural, RTL, count-reconciliation, and render results.
5. Internal QA renders — page PNGs; deliver them only when requested.

## Required workflow

### 1. Lock the fidelity contract

Determine the entry `.tex`, target Word/LibreOffice version, reference/template DOCX, Persian and Latin fonts, digit policy, bibliography style, and whether equations/tables must remain editable. Apply the defaults in `GRILLING.md` when the project answers them implicitly.

**Completion criterion:** every contract field is either supplied, inferred with evidence, or marked as a blocking question.

### 2. Forensically inventory the source tree

Run `scripts/inspect_latex.py` on the entry file. Traverse every `\input`, `\include`, bibliography, and graphic dependency. Inventory document class, packages, custom commands/environments, language/direction commands, math, tables, figures, TikZ/PGFPlots, citations, labels/references, footnotes, headers/footers, page geometry, and raw/unknown commands.

Read [`references/01_source_forensics.md`](references/01_source_forensics.md) while classifying the result.

**Completion criterion:** every included source file and referenced asset exists or is explicitly missing; every nonstandard environment/command is classified as supported, transformable, renderable fallback, or unresolved.

### 3. Establish the visual baseline

Compile the original project with its intended engine. Prefer `latexmk -xelatex` for XePersian/polyglossia projects and preserve the original engine when the source declares another. Keep the baseline PDF and log.

**Completion criterion:** a baseline PDF exists, or the exact compile failure is documented without pretending the source is valid.

### 4. Build the conversion map

Create a fidelity-ledger entry for each special construct. Map it to one of:

- `native` — editable Word paragraph, list, table, image, hyperlink, footnote, field, or OMML equation.
- `transformed` — source is normalized or rewritten before Pandoc.
- `ooxml-patched` — Pandoc output is repaired at the WordprocessingML level.
- `vector-fallback` — isolated construct becomes SVG with a PNG compatibility copy.
- `raster-fallback` — isolated construct becomes a high-resolution image with alt text and retained source.
- `unresolved` — conversion stops in strict mode.

Read [`references/02_conversion_architecture.md`](references/02_conversion_architecture.md).

**Completion criterion:** no special construct lacks a planned representation.

### 5. Normalize and flatten safely

Use `scripts/flatten_latex.py` to produce a UTF-8 flattened source while preserving the original files. Preserve Persian characters, ZWNJ, labels, macro definitions, and asset-relative paths. Normalize line endings and Unicode to NFC; preserve code/verbatim blocks byte-for-byte.

**Completion criterion:** the flattened source contains every reachable source unit once, include cycles are reported, and the original tree remains untouched.

### 6. Generate and inspect the Pandoc AST

Run Pandoc to JSON before writing DOCX. Count `RawInline` and `RawBlock` nodes and inspect their payloads. Add a targeted Lua/Python transform only for constructs whose semantics are understood. Keep unknown raw TeX in the ledger.

Use `filters/latex_to_docx.lua` for conservative normalization and diagnostics.

**Completion criterion:** every raw node is transformed, intentionally preserved by another path, or unresolved; zero raw nodes disappear silently.

### 7. Produce the first DOCX

Use Pandoc with `--reference-doc`, explicit `--resource-path`, and citation options only when their inputs are known. Pandoc should create the document skeleton and native OMML equations. Use the project bibliography and CSL when exact citation formatting can be represented.

Run `scripts/convert_latex_to_docx.py` for the supported golden path.

**Completion criterion:** a DOCX opens as an OPC/ZIP package; all media relationships resolve; expected headings, tables, figures, and equations are present or ledgered.

### 8. Repair specialized content

Apply the relevant reference before patching:

- Persian, Arabic-script, and mixed-direction text: [`references/03_persian_rtl.md`](references/03_persian_rtl.md)
- Mathematics and equation numbering: [`references/04_math.md`](references/04_math.md)
- Tables and long tables: [`references/05_tables.md`](references/05_tables.md)
- Figures, TikZ, PGFPlots, diagrams, and charts: [`references/06_figures_graphs.md`](references/06_figures_graphs.md)
- Citations, labels, cross-references, TOC, notes, and fields: [`references/07_citations_crossrefs.md`](references/07_citations_crossrefs.md)

Run `scripts/postprocess_docx.py` after Pandoc. It must set paragraph BiDi, run RTL, language, complex-script fonts, and RTL table order without manually reversing characters.

**Completion criterion:** Persian paragraphs/runs/tables have the required OOXML properties; LTR code, URLs, formulas, and English spans remain LTR; native objects remain editable.

### 9. Validate structurally and visually

Run `scripts/validate_docx.py` with the source inventory and fidelity ledger. Then render the DOCX to PDF/PNGs with `scripts/render_docx.py` or the platform DOCX renderer. Inspect every page at 100% zoom against the LaTeX baseline.

Read [`references/09_validation_qa.md`](references/09_validation_qa.md).

**Completion criterion:** ZIP/XML/relationship checks pass; source-object counts reconcile; no Persian text lacks required direction metadata; every page is free of missing glyphs, clipping, overlap, broken tables, misplaced captions, and corrupted equations; every deviation appears in the ledger/report.

### 10. Deliver atomically

Write final files to temporary paths, validate them, then rename into the delivery location. Include tool versions and SHA-256 hashes. Deliver the final DOCX and reports, not temporary files.

**Completion criterion:** the delivered DOCX is the exact validated file and the report/ledger identify all deliberate fallbacks.

## Hard fidelity rules

- Preserve source semantics and Unicode order; use Word BiDi properties for display.
- Prefer native Word objects. Use isolated visual fallbacks only when native representation is infeasible.
- Pair every fallback with alt text, the originating file/line, and the retained LaTeX snippet or asset path.
- Treat missing files, unknown raw TeX, failed equations, and count mismatches as errors in strict mode.
- Keep fonts configurable and reference them by family name; package no font files.
- Keep one source of truth: transformation rules live in scripts/references, while the ledger records only per-document decisions.

## Implementation routing

- Python design, subprocess discipline, data models, and extension points: [`references/08_python_implementation.md`](references/08_python_implementation.md)
- Common failures and deterministic recovery: [`references/10_failure_modes.md`](references/10_failure_modes.md)
- OOXML element recipes: [`references/11_ooxml_recipes.md`](references/11_ooxml_recipes.md)
- Official technical sources: [`references/12_sources.md`](references/12_sources.md)
- Runnable invocation: [`examples/end_to_end.md`](examples/end_to_end.md)
