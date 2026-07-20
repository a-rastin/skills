# Citations, bibliography, cross-references, TOC, notes, and fields

## Citation branch selection

Determine whether the project uses BibTeX/natbib, BibLaTeX/biber, manually formatted references, or another system. Preserve citation semantics: source keys, locator/prefix/suffix, suppress-author behavior, textual vs parenthetical form, sorting, and locale.

### Standard representable styles

Use Pandoc citeproc when bibliography data and an appropriate CSL are available:

```bash
pandoc flattened.tex --citeproc \
  --bibliography references.bib \
  --csl style.csl \
  --metadata link-citations=true \
  -o output.docx
```

Verify every cited key resolves and the bibliography count matches expected unique references.

### Exact custom BibLaTeX styles

Pandoc CSL may not reproduce an institution-specific BibLaTeX style exactly. Use one of:

1. obtain an equivalent verified CSL;
2. export formatted references/citations from the LaTeX toolchain and reconstruct semantic links where possible;
3. preserve visible formatted citation text and bibliography as static text while retaining keys in the ledger;
4. ask the user to choose semantic editability versus exact appearance when both cannot be achieved.

Never silently substitute a different citation style.

## Labels and references

Build a symbol table of every `\label` and every reference command (`\ref`, `\pageref`, `\eqref`, `\autoref`, `\cref`, `\Cref`). Each label must resolve to one target.

Preferred Word mapping:

- target number -> `SEQ` field;
- target anchor -> bookmark with a sanitized unique name;
- cross-reference -> `REF` field;
- page reference -> `PAGEREF` field;
- hyperlink -> field/hyperlink relationship to bookmark.

Set `w:updateFields w:val="true"` so Word updates fields on open. For deterministic headless rendering, also store a correct cached visible result or materialize display text in a QA copy. Do not mistake a cached value for a live field.

## Bookmark naming

Word bookmark names have stricter syntax than arbitrary LaTeX labels. Create a stable mapping:

```text
latex label: sec:روش-کار
bookmark: ltx_sec_6f5a2d7c
```

Use a readable prefix plus a short hash. Store both directions in the ledger.

## Captions and numbering

Use separate `SEQ Figure`, `SEQ Table`, and `SEQ Equation` fields unless the source shares counters. Preserve chapter-scoped numbering only when Word field expressions and heading numbering reproduce it; otherwise use static visible numbering with an explicit limitation.

Keep captions with their object and apply language/direction independently from the object.

## Table of contents and lists

Insert a live TOC field using heading styles. Insert lists of figures/tables only when captions use appropriate fields/styles. Field codes may not update in LibreOffice/headless mode exactly as Word does, so set update-on-open and verify cached text.

## Footnotes and endnotes

Preserve note order, markers, and note content. Patch RTL in `footnotes.xml`/`endnotes.xml`. Reconcile source note count with DOCX note references. If a source package implements custom marginal notes or multiple note series, classify and map explicitly.

## Indexes, glossaries, and acronyms

A fully live Word index/glossary may require fields not emitted by Pandoc. Choose one:

- semantic Word fields when supported and tested;
- static generated section with preserved entries and links;
- explicit unresolved status.

Preserve Persian collation/sorting decisions; do not silently apply English sorting.

## Validation

- every citation key resolves or is listed unresolved;
- bibliography item count and order match the chosen style contract;
- every label has a target and every reference points to a valid bookmark;
- fields contain valid begin/separate/end structure;
- cached field text is nonempty;
- TOC levels match heading levels;
- notes, captions, and references display correctly in RTL and LTR contexts.
