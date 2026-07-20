# Requirements Grilling Gate

This gate converts ambiguity into explicit decisions before source transformation. Ask a question only when the answer changes the output and the project cannot supply it. Otherwise infer a default, cite the evidence in `conversion-report.md`, and proceed.

## Blocking questions

Ask the user only for unresolved items in this list:

1. **Entry point:** Which `.tex` is the root when more than one file contains `\documentclass` or builds a distinct document?
2. **Target application:** Microsoft Word version, Word Online, or LibreOffice? This changes SVG, field, and equation compatibility.
3. **Template:** Is there a mandatory institutional `.docx`/`.dotx`? Use it as `--reference-doc` rather than imitating it.
4. **Editability contract:** Must equations, tables, charts, and diagrams remain editable, or is a visual fallback acceptable for specific constructs?
5. **Fonts:** Which installed Persian and Latin families are required? Font names are configuration; font files are never bundled.
6. **Digit policy:** Preserve source digits, force Persian digits, or force Western digits? Default: preserve exactly.
7. **Bibliography fidelity:** Is semantic citation correctness sufficient, or must the output match a custom BibLaTeX style exactly?
8. **Pagination fidelity:** Is a reflowed Word document acceptable, or are section/page breaks contractually fixed?
9. **Unknown constructs:** In strict mode, should conversion stop at the first unresolved construct or complete a draft with explicit placeholders? Default: stop.

## Defaults used when evidence is absent

| Decision | Default |
|---|---|
| Invocation | Model-invoked; the task should trigger from LaTeX-to-Word requests. |
| Output | Editable DOCX plus conversion report, fidelity ledger, and validation report. |
| Baseline engine | XeLaTeX for XePersian/polyglossia/Persian sources; otherwise the engine detected from project tooling. |
| Main language | `fa-IR` when Arabic-script Persian text or XePersian is detected. |
| Paragraph direction | RTL when a paragraph contains Persian/Arabic-script letters; LTR otherwise. |
| Mixed runs | Persian/Arabic runs RTL; Latin/code/URL runs LTR; character order is never reversed. |
| Unicode | NFC normalization; preserve ZWNJ/ZWJ and source code points. |
| Digits | Preserve source digits. |
| Persian font | Configurable family name; default `Noto Naskh Arabic` only when installed. |
| Latin font | Configurable family name; default `Liberation Serif` only when installed. |
| Math | Native OMML through Pandoc; image fallback only for an isolated unsupported equation. |
| Tables | Native editable Word tables; reproduce merges, borders, widths, and direction. |
| Figures | Reuse original assets; compile TikZ/PGFPlots; prefer SVG, retain 300-DPI PNG fallback. |
| Citations | Pandoc citeproc with project bibliography/CSL when representable. |
| Fields | Insert/update TOC, SEQ, and REF fields where reliable; cache visible results for headless QA. |
| QA | Structural validation plus render-and-inspect of every page. |
| Failure policy | No silent deletion; unresolved content fails strict mode. |

## Project interrogation sequence

1. Discover roots and build scripts (`latexmkrc`, Makefile, CI, editor recipes).
2. Read the preamble before asking about engine, language, fonts, geometry, bibliography, or packages.
3. Read institutional templates/configuration before asking about style.
4. Inspect installed fonts before declaring a font missing.
5. Compile the source before asking whether a construct is intentional.
6. Ask one compact batch of genuinely blocking questions, then record answers verbatim.

## Definition of done for grilling

The conversion may begin when every blocking field is either answered or resolved by an explicit default with evidence. The report must distinguish user decisions from inferred decisions.
