# Mathematics and equations

## Primary representation

Use Pandoc's DOCX writer to convert TeX math to native Office Math Markup Language (OMML). Native OMML is editable, searchable, scalable, and preferable to equation images.

## Preparation

1. Inventory all math environments and custom macros.
2. Build a macro table from `\newcommand`, `\renewcommand`, `\DeclareMathOperator`, and package semantics.
3. Test representative expressions through Pandoc JSON and DOCX.
4. Expand only unsupported macros into standard LaTeX, preserving source locations.
5. Keep text-language commands inside math explicit; Persian prose embedded in equations may require OMML text runs with language/direction patches.

## Environment mapping

- inline math -> inline `m:oMath`;
- display equation -> `m:oMathPara`;
- aligned/gathered systems -> OMML equation array when Pandoc supports it;
- matrices/cases/fractions/radicals/scripts/operators -> native OMML;
- equation labels -> bookmark around equation/number;
- equation references -> Word `REF` field or static visible text with ledgered limitation.

## Numbered equations

A stable Word layout is a borderless three-column table:

1. narrow spacer/number cell;
2. centered equation cell containing OMML;
3. mirrored number/spacer cell according to source convention.

Use a `SEQ Equation` field for the number and a bookmark for cross-reference. In Persian documents, set the paragraph/table direction explicitly and keep the numeric field LTR. Avoid manual tabs when page width can vary.

## Unsupported equations

Attempt in this order:

1. expand custom macros;
2. rewrite into equivalent standard TeX;
3. use a targeted Pandoc filter;
4. convert MathML to OMML through a tested transform;
5. render the isolated equation as SVG/PNG.

An image fallback requires:

- 300+ DPI PNG and preferably SVG;
- alt text containing a concise spoken formula and/or retained LaTeX source reference;
- baseline-aligned inline placement for inline math;
- ledger entry with source snippet and reason OMML failed.

## Validation

Reconcile source math count with DOCX `m:oMath`/`m:oMathPara` plus ledgered image fallbacks. Inspect:

- operators and delimiters;
- superscripts/subscripts;
- matrices and alignment;
- italic/upright semantics;
- equation numbers and references;
- Persian text inside math;
- line wrapping and clipping.

A count mismatch is an error until explained.
