# Official technical sources

Use primary documentation and verify the installed tool version before relying on version-specific behavior.

## Pandoc

- User's Guide: https://pandoc.org/MANUAL.html
- Lua filters: https://pandoc.org/lua-filters.html
- Math output behavior (DOCX uses OMML): https://pandoc.org/demo/example33/8.13-math.html
- Reference DOCX option: https://pandoc.org/MANUAL.html#option--reference-doc

## python-docx

- Documentation: https://python-docx.readthedocs.io/en/latest/
- Styles: https://python-docx.readthedocs.io/en/latest/user/styles-using.html
- Tables: https://python-docx.readthedocs.io/en/latest/user/tables.html
- Pictures/shapes: https://python-docx.readthedocs.io/en/latest/user/shapes.html

`python-docx` does not expose every WordprocessingML feature; use `lxml`/OOXML patches for BiDi, fields, and advanced table behavior.

## Microsoft Open XML / WordprocessingML

- Wordprocessing document structure: https://learn.microsoft.com/en-us/office/open-xml/word/how-to-open-and-add-text-to-a-word-processing-document
- Paragraph properties: https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.paragraphproperties
- Paragraph BiDi (`w:bidi`): https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.bidi
- Run RTL (`w:rtl`): https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.righttolefttext
- Wordprocessing namespace index: https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing

## Persian LaTeX

- XePersian package: https://ctan.org/pkg/xepersian
- XePersian documentation: https://mirrors.ctan.org/macros/xetex/latex/xepersian/xepersian-doc.pdf

## Unicode

- Unicode Bidirectional Algorithm, UAX #9: https://www.unicode.org/reports/tr9/
- Unicode normalization, UAX #15: https://www.unicode.org/reports/tr15/

## Rendering/conversion tools

- LibreOffice command-line conversion: https://help.libreoffice.org/latest/en-US/text/shared/guide/start_parameters.html
- Inkscape command line: https://inkscape.org/doc/inkscape-man.html
- Poppler tools (`pdftoppm`, `pdfinfo`): https://poppler.freedesktop.org/

## Version capture

Record outputs from:

```bash
pandoc --version
python -c "import docx,lxml; print(docx.__version__, lxml.__version__)"
latexmk -v
xelatex --version
libreoffice --version
inkscape --version
pdftoppm -v
```
