# Validation and quality assurance

Validation has four independent layers. Passing one layer never substitutes for another.

## 1. Package integrity

- DOCX is a readable ZIP/OPC package.
- `[Content_Types].xml` exists and all XML parts parse.
- required parts and relationships exist.
- every internal relationship target resolves.
- no duplicate ZIP member names.
- media files are nonempty and recognized.
- document opens in at least one target-compatible application.

## 2. Structural reconciliation

Compare source inventory against DOCX and ledger:

```text
source count = native DOCX count + explicit fallback count + unresolved count
```

Apply this to:

- headings/sections;
- tables;
- figures/subfigures;
- inline/display equations;
- citations/bibliography items;
- footnotes/endnotes;
- labels/references;
- hyperlinks;
- raw/unknown constructs.

A mismatch without a ledger explanation fails validation.

## 3. Text and RTL validation

- extract text from every story part and compare normalized text against expected source prose;
- verify no replacement characters or accidental presentation-form substitutions;
- verify ZWNJ count/positions for sampled or mapped paragraphs;
- every Persian paragraph has `w:bidi` unless explicitly centered/LTR by source semantics (centered still needs BiDi);
- every Persian run has `w:rtl` and `w:lang@w:bidi=fa-IR`;
- explicit LTR runs are marked and ordered correctly;
- RTL tables use `w:bidiVisual` when required;
- headings, captions, notes, headers, footers, and lists receive the same checks.

## 4. Visual validation

Render the DOCX to PDF and page PNGs. Inspect every page at 100% zoom. Compare against the LaTeX baseline for semantic and visual intent, allowing reflow under the contract.

Check:

- glyph coverage and font consistency;
- Persian joining, ZWNJ behavior, punctuation, mixed LTR order;
- headings, numbering, TOC, page breaks, margins, headers/footers;
- line spacing and paragraph spacing;
- tables within margins, repeated headers, merges, borders, page splits;
- figure crop, aspect ratio, labels, captions, alt-text presence structurally;
- equations, delimiters, alignment, numbering;
- footnotes/endnotes and bibliography;
- no overlap, clipping, blank unexpected pages, or orphaned captions.

Pixel-perfect page diff is diagnostic, not a universal pass criterion, because TeX and Word reflow differently. Use image overlays to locate omissions or gross layout changes, then judge them against the fidelity contract.

## Automated checks

The validator should emit machine-readable issues:

```json
{
  "severity": "error",
  "code": "RTL_RUN_MISSING",
  "part": "word/document.xml",
  "paragraph_index": 17,
  "text_sample": "روش‌های پژوهش",
  "remediation": "add w:rtl and fa-IR bidi language to Arabic-script runs"
}
```

Severity policy:

- `error`: content loss, corruption, broken relationship, missing required direction, unexplained count mismatch, failed render.
- `warning`: accepted fallback, possible font substitution, field not updated headlessly, pagination divergence.
- `info`: tool/version and benign normalization.

## Acceptance gate

Deliver only when:

- zero errors remain;
- every warning is deliberate and present in the conversion report;
- all ledger entries are `validated` or explicitly accepted `unresolved` in non-strict mode;
- every rendered page was inspected after the last content/OOXML change;
- final file hashes match the report.
