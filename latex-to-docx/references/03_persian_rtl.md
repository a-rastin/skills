# Persian and mixed RTL/LTR conversion

Persian fidelity depends on preserving Unicode logical order and expressing direction through WordprocessingML. Character reversal is corruption.

## Script detection

Classify text by Unicode script:

- Persian/Arabic letters: Arabic blocks including presentation supplements only when present in source;
- Latin letters and code symbols;
- digits: preserve source forms and treat direction contextually;
- neutral punctuation/whitespace: inherit from surrounding strong runs.

Paragraph direction should follow the dominant semantic language, not a crude character majority when style/context already declares direction. Use source direction commands first, paragraph style second, script detection third.

## Required OOXML

For an RTL paragraph:

```xml
<w:pPr>
  <w:bidi/>
  <w:jc w:val="right"/>
</w:pPr>
```

For a Persian/Arabic run:

```xml
<w:rPr>
  <w:rtl/>
  <w:lang w:val="fa-IR" w:bidi="fa-IR"/>
  <w:rFonts w:ascii="Latin Font" w:hAnsi="Latin Font"
            w:cs="Persian Font" w:eastAsia="Persian Font"/>
</w:rPr>
```

For an explicit LTR run inside RTL text, set `w:rtl w:val="0"` and `w:lang w:val="en-US"`. For RTL tables add `<w:bidiVisual/>` under `w:tblPr`; then validate the visual column order.

Set `w:themeFontLang w:val="en-US" w:eastAsia="en-US" w:bidi="fa-IR"` in `word/settings.xml`. Apply language/font defaults in `styles.xml`, then use direct formatting only where direction changes.

## Mixed text segmentation

Split runs at script-direction boundaries while preserving style and hyperlinks. Typical LTR spans in Persian paragraphs:

- URLs, email addresses, DOIs;
- file paths and command lines;
- code and identifiers;
- Latin acronyms and English phrases explicitly marked LTR;
- equation objects.

Keep punctuation attached to the semantic span when source markup makes that clear. If punctuation visually jumps across a boundary, prefer separate runs and explicit run direction. Use LRM/RLM or Unicode isolates only after render evidence shows they are needed; record inserted control characters.

## Unicode policy

- Normalize ordinary prose to NFC.
- Preserve ZWNJ. It is semantically and typographically significant in Persian.
- Preserve Arabic/Persian Yeh and Kaf variants unless a user-approved normalization map exists.
- Preserve Persian/Arabic/Western digits exactly by default.
- Preserve combining marks and Quranic/phonetic marks.
- Reject accidental replacement characters and visibly report invalid decoding.

## Fonts

Use family names, not font files. Check installed coverage with `fc-match`/font APIs. A chosen Persian font must cover every Arabic-script code point in the document. Configure:

- complex-script font (`w:cs`) for Persian;
- ASCII/high ANSI font for Latin;
- monospaced font for code;
- equation font through Word/Pandoc defaults unless a tested OMML configuration exists.

A visual QA pass must detect tofu, fallback font drift, clipped diacritics, and bad baseline alignment.

## Paragraphs and headings

Apply RTL and right alignment to Persian body paragraphs and headings. Preserve centered titles/captions as centered while still setting `w:bidi`. Do not replace semantic alignment with right alignment when the source explicitly centers or justifies.

For justified Persian text use Word justification plus BiDi. Compare inter-word spacing to baseline; Word and XeTeX will not break lines identically.

## Lists and numbering

- Preserve logical list hierarchy.
- Set paragraph BiDi for list items.
- Mirror indentation so the number/bullet appears on the right.
- Validate hanging indent and continuation lines.
- For exact Persian digit numbering, either use literal source numbering or a tested Word numbering definition/locale. Do not assume Word will display Persian digits from a generic decimal format.

## Tables

Apply `w:bidiVisual` to tables whose logical first column should appear at the right. Set each cell paragraph independently: Persian cells RTL, numeric/code cells LTR or centered. Confirm merged-cell coordinates after visual reversal; Word's visual table direction can surprise code that assumes XML order equals displayed order.

## Captions, notes, headers, and footers

Patch all story parts, not only `word/document.xml`: headers, footers, footnotes, endnotes, comments, and text boxes where accessible. Caption direction follows caption language. Equation numbers and page numbers may remain LTR while the surrounding caption/footer is RTL.

## Search and replace safety

Never reverse strings, reorder tokens, or apply a global Arabic reshaper. Word performs shaping and BiDi display. Never use presentation-form glyphs as a substitute for correct Unicode text.

## Persian acceptance tests

- copied text from Word retains the same logical Unicode sequence as the source;
- ZWNJ positions match;
- Persian paragraphs include `w:bidi`;
- Persian runs include `w:rtl` and `w:lang w:bidi="fa-IR"`;
- LTR spans remain readable and correctly ordered;
- table first/last columns match the baseline;
- lists, captions, footnotes, and headers display on the intended side;
- no missing glyphs or clipped marks appear in rendered pages.
