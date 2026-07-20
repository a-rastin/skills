# OOXML recipes

Namespace:

```python
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
qn = lambda tag: f"{{{W}}}{tag}"
```

## Idempotent element setter

```python
def ensure(parent, tag):
    node = parent.find(qn(tag))
    if node is None:
        node = etree.SubElement(parent, qn(tag))
    return node
```

When child order matters, insert according to WordprocessingML schema order rather than always appending. The supplied postprocessor uses a pragmatic order for BiDi/language/font properties and validates resulting XML.

## Paragraph RTL

```python
pPr = p.find(qn("pPr"))
if pPr is None:
    pPr = etree.Element(qn("pPr"))
    p.insert(0, pPr)
ensure(pPr, "bidi")
jc = ensure(pPr, "jc")
jc.set(qn("val"), "right")
```

Preserve source alignment: only set right when alignment is absent or policy requests it. Centered Persian text keeps `w:bidi` plus center justification.

## Run RTL and language

```python
rPr = r.find(qn("rPr"))
if rPr is None:
    rPr = etree.Element(qn("rPr"))
    r.insert(0, rPr)
ensure(rPr, "rtl")
lang = ensure(rPr, "lang")
lang.set(qn("val"), "fa-IR")
lang.set(qn("bidi"), "fa-IR")
fonts = ensure(rPr, "rFonts")
fonts.set(qn("ascii"), latin_font)
fonts.set(qn("hAnsi"), latin_font)
fonts.set(qn("cs"), persian_font)
```

For LTR runs set `<w:rtl w:val="0"/>` and `w:lang@w:val="en-US"`.

## RTL table

```python
tblPr = table.find(qn("tblPr"))
if tblPr is None:
    tblPr = etree.Element(qn("tblPr"))
    table.insert(0, tblPr)
ensure(tblPr, "bidiVisual")
```

## Repeating table header

```xml
<w:trPr><w:tblHeader/></w:trPr>
```

## Cell merges

Horizontal span:

```xml
<w:tcPr><w:gridSpan w:val="3"/></w:tcPr>
```

Vertical merge start/continuation:

```xml
<w:vMerge w:val="restart"/>
<w:vMerge/>
```

## Theme language

In `word/settings.xml`:

```xml
<w:themeFontLang w:val="en-US" w:eastAsia="en-US" w:bidi="fa-IR"/>
<w:updateFields w:val="true"/>
```

## Field code

A complex field uses begin/instruction/separate/result/end runs:

```xml
<w:r><w:fldChar w:fldCharType="begin"/></w:r>
<w:r><w:instrText xml:space="preserve"> REF ltx_sec_abc123 \h </w:instrText></w:r>
<w:r><w:fldChar w:fldCharType="separate"/></w:r>
<w:r><w:t>۱.۲</w:t></w:r>
<w:r><w:fldChar w:fldCharType="end"/></w:r>
```

## Bookmark

```xml
<w:bookmarkStart w:id="42" w:name="ltx_sec_abc123"/>
...
<w:bookmarkEnd w:id="42"/>
```

Bookmark IDs must be unique numeric values; names must be stable and valid for Word.

## Alt text

Set `descr` on the drawing non-visual properties (`wp:docPr`) and a meaningful `name`. Preserve existing IDs and relationships.

## Story parts to patch

At minimum inspect:

- `word/document.xml`;
- `word/header*.xml`;
- `word/footer*.xml`;
- `word/footnotes.xml`;
- `word/endnotes.xml`;
- `word/comments.xml`;
- text boxes embedded in drawings/VML when present;
- `word/styles.xml` and `word/settings.xml`.
