# Figures, graphs, diagrams, TikZ, and PGFPlots

## Asset resolution

Resolve each `\includegraphics` against the current source directory, `\graphicspath`, and declared extensions. Preserve crop, trim, rotation, scale, width, and height. Hash the selected asset and record any alternate files with the same stem.

## Representation order

1. Reuse a high-quality original asset.
2. Prefer SVG for modern Word when the target supports it.
3. Retain a 300-DPI PNG compatibility fallback.
4. Use JPEG only for photographic content where loss is acceptable.
5. Avoid screenshots of plots when vector/source output exists.

Use inline placement for stability unless the source contract requires text wrapping. Word floating anchors vary across renderers.

## TikZ and PGFPlots

Extract each environment with the preamble definitions it depends on. Build a standalone TeX file using the original engine and fonts. Compile to PDF, crop the bounding box, then convert:

```bash
xelatex -interaction=nonstopmode -halt-on-error figure.tex
pdfcrop figure.pdf figure-crop.pdf
inkscape figure-crop.pdf --export-type=svg --export-filename=figure.svg
pdftoppm -png -r 300 -singlefile figure-crop.pdf figure
```

When `pdfcrop` is unavailable, use a tight bounding-box conversion method and verify no labels are clipped. Preserve Persian text in the figure by using the original engine/font setup.

## PGFPlots and charts

If data and plotting code are available, prefer regenerating a clean vector chart from the authoritative source. Do not reverse-engineer data from a rendered chart. Preserve axes, units, legends, error bars, annotations, log scales, and color semantics.

A chart is not editable merely because it is vector. Creating a native Word chart requires rebuilding its embedded workbook and chart XML; do this only when editability is explicitly required and source data are available. Otherwise use vector art and document the limitation.

## EPS/PDF/SVG conversion

- EPS/PS: convert through Ghostscript/Inkscape to PDF/SVG/PNG; inspect transparency and fonts.
- PDF: select the correct page, crop, convert to SVG/PNG.
- SVG: sanitize external references, embed fonts as outlines only when licensing/requirements allow, and retain accessible text when possible.
- TIFF: convert to PNG unless TIFF support is contractually required.

## Subfigures

Represent a subfigure group as a borderless Word table or a controlled set of inline images. Preserve order, individual labels/captions, group caption, and cross-references. In RTL documents verify whether source order is semantic or visual before applying `bidiVisual`.

## Sizing

Compute physical size from source dimensions and page width. For raster output:

```text
pixels = inches × target_DPI
```

Use at least 300 DPI for line art and 150–220 DPI for photographs when file size matters. Never upscale a low-resolution source and call it higher quality; record the limitation.

## Captions and alt text

Use a caption paragraph with a `SEQ Figure` field and bookmark when cross-references are required. Alt text should communicate the figure's purpose/content, not only repeat the filename. A detailed chart may need a short alt text plus a nearby textual description.

## Validation

Confirm:

- every source figure has a DOCX image or ledgered fallback;
- aspect ratio and crop match;
- Persian labels render correctly;
- no image is clipped or exceeds margins;
- subfigure order/captions match;
- image relationships resolve;
- SVG compatibility matches the target application;
- alt text exists for meaningful figures.
