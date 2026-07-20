# `latex-to-docx` skill package

A fidelity-first skill and runnable reference pipeline for converting LaTeX source trees—especially Persian and mixed RTL/LTR projects—into editable DOCX files.

The package uses a hybrid strategy:

1. inspect and flatten the LaTeX source graph;
2. compile a XeLaTeX/LaTeX baseline PDF;
3. use Pandoc for AST parsing, document structure, citations, and native OMML math;
4. apply targeted WordprocessingML patches for Persian direction, language, fonts, and tables;
5. reconcile source-object counts and render every DOCX page for visual QA.

The scripts are a conservative golden path, not a claim that arbitrary TeX is automatically representable in Word. Strict mode stops when content would otherwise be lost.

## Minimum runtime

- Python 3.10+
- `pandoc`
- `python-docx`
- `lxml`
- `latexmk` and the source document's TeX engine
- LibreOffice and `pdftoppm` for rendering
- Inkscape for SVG/PDF/EPS figure conversion when needed

Run the example in [`examples/end_to_end.md`](examples/end_to_end.md).
