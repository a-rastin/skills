# Conversion architecture

## Fidelity contract

Word and TeX use different layout engines. Preserve semantic structure, reading order, styles, native equations/tables, captions, references, and visual intent. Treat exact pagination as a separate contract. A conversion passes when no content is silently lost and the accepted visual/semantic deviations are documented.

## Golden path

1. **Immutable input copy** — hash the source tree and work in a temporary directory.
2. **Baseline build** — compile the original source and retain PDF/log.
3. **Inventory** — produce `inventory.json` and initial ledger.
4. **Flatten** — inline reachable TeX source for Pandoc while preserving asset paths.
5. **AST pass** — `pandoc -f latex+raw_tex -t json`; inspect raw nodes and object counts.
6. **Targeted transforms** — expand known macros, normalize direction wrappers, convert unsupported isolated graphics.
7. **DOCX write** — Pandoc with a reference DOCX and explicit resource/citation arguments.
8. **OOXML postprocess** — BiDi, language, fonts, table order, captions, fields, section properties.
9. **Structural QA** — package integrity, XML, relationships, counts, text, RTL, fields, alt text.
10. **Visual QA** — render DOCX, inspect every page against baseline.
11. **Atomic delivery** — move validated artifacts into final paths.

## Recommended command sequence

```bash
python scripts/inspect_latex.py main.tex --output work/inventory.json
python scripts/flatten_latex.py main.tex --output work/flattened.tex --map work/source-map.json
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=work/baseline main.tex
pandoc work/flattened.tex -f latex+raw_tex -t json -o work/ast.json
pandoc work/flattened.tex \
  -f latex+raw_tex \
  -t docx \
  --standalone \
  --resource-path="project:project/figures:work/generated" \
  --reference-doc=reference.docx \
  --lua-filter=filters/latex_to_docx.lua \
  -o work/first-pass.docx
python scripts/postprocess_docx.py work/first-pass.docx work/final.docx --main-lang fa-IR
python scripts/validate_docx.py work/final.docx --inventory work/inventory.json --strict
python scripts/render_docx.py work/final.docx --output-dir work/render
```

The orchestrator performs this sequence with consistent logs and paths.

## Branches

### Standard semantic branch

Use Pandoc directly when the source uses conventional headings, prose, lists, standard math, simple/medium tables, ordinary figures, footnotes, and citations. Postprocess RTL and styles.

### AST transform branch

Use a Lua/Python AST transform when a custom command has known semantics. Transform the smallest possible node. Preserve source location in the ledger. Unit-test each rule with a fixture.

Examples:

- semantic callouts -> custom-styled Div/paragraph;
- `\lr{...}` -> LTR span;
- institution-specific heading macro -> Header node;
- custom figure wrapper -> Figure with caption/identifier.

### OOXML patch branch

Use direct WordprocessingML changes for features Pandoc/python-docx do not expose adequately:

- paragraph/run BiDi and complex-script language/fonts;
- RTL table visual order;
- `SEQ`, `REF`, `PAGEREF`, and TOC fields;
- bookmarks, cached field values, update-on-open;
- repeating table headers, cell merges, section direction/details;
- alt text and relationship repair.

Patches must be idempotent: running them twice produces the same XML meaning.

### Isolated render fallback

Render only the unsupported object, never an entire editable page by default. Compile it with the original preamble and engine, crop tightly, and convert to SVG plus 300-DPI PNG. Insert inline, add alt text, and retain the source snippet/asset path in the ledger.

Appropriate examples: a complex commutative diagram, PSTricks object, bespoke TikZ decoration, or equation unsupported by OMML.

### Page-image branch

A full page as an image destroys editability and accessibility. Use it only under an explicit visual-facsimile contract. Record it as a major deviation.

## Reference DOCX

Use a supplied institutional template whenever available. Pandoc uses the reference document's styles and document properties such as margins, page size, headers, and footers. If none exists, generate one with `create_reference_docx.py` and then inspect it in Word/LibreOffice.

Define and test at least:

- Normal/Body Text;
- Title, Subtitle, Author, Date;
- Heading 1–6;
- Caption, Table Caption, Figure Caption;
- Footnote Text, Bibliography;
- Code/Source Code;
- table styles;
- page size, margins, headers, footers, section defaults.

## Work directory contract

```text
work/
  source-copy/
  inventory.json
  source-map.json
  flattened.tex
  ast.json
  baseline/
    main.pdf
    main.log
  generated/
    figures/
    equations/
  first-pass.docx
  final.docx
  fidelity-ledger.json
  validation-report.json
  conversion-report.md
  render/
    page-1.png
    ...
```

## Determinism

Record executable versions, locale, environment, exact command arguments, input hashes, output hashes, and timestamps. Sort directory traversal and JSON keys. Do not use shell string interpolation for subprocesses. Write outputs atomically.
