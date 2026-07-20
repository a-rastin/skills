# Tables

Tables should remain editable Word tables. Rasterization is a last resort for a specific construct, not the default for complex data.

## Parse to a logical grid

Build an intermediate model before writing OOXML:

```text
TableModel
  caption, label, direction, preferred_width
  columns: alignment, width, semantic_type
  rows: header/body/footer, repeat_header
  cells: row, col, row_span, col_span, content_blocks,
         horizontal_alignment, vertical_alignment, direction,
         borders, shading, padding
```

Resolve `\multicolumn` to `gridSpan` and `\multirow` to `vMerge`. Validate that spans form a rectangular grid without overlaps.

## Source features

- `l/c/r` -> left/center/right cell alignment;
- `p{}`, `m{}`, `b{}` -> fixed/proportional width plus vertical alignment;
- `tabularx` X columns -> distribute remaining width;
- `booktabs` -> top/mid/bottom borders with no accidental vertical rules;
- `longtable` -> normal Word table with repeating header rows and page-break-safe rows;
- `threeparttable` notes -> paragraphs immediately below the table with a dedicated style;
- rotated/landscape table -> landscape section when needed;
- `\resizebox` -> prefer landscape, width optimization, or font adjustment before any image fallback.

## Width algorithm

1. Determine writable page width from section size and margins.
2. Reserve fixed-width columns.
3. Estimate minimum content width from longest unbreakable tokens, numerals, and equations.
4. Allocate remaining width proportionally to flexible columns.
5. Set exact table width and grid column widths in twips.
6. Use fixed layout for deterministic widths; allow autofit only for genuinely fluid simple tables.
7. Render and adjust; never shrink body text below the agreed readable minimum without reporting it.

## RTL tables

Set `w:bidiVisual` when the source's first logical column appears at the right. Keep a stable logical grid in the ledger and verify displayed order. Patch cell paragraphs independently. Numeric and Latin cells can remain LTR while the table is visually RTL.

## Headers and page breaks

- mark header rows with `w:tblHeader`;
- keep short rows together when possible;
- allow long rows to split only when necessary;
- repeat multirow header blocks accurately;
- avoid orphaned captions; keep caption with the next table;
- for a table that cannot fit portrait width, create a dedicated landscape section and restore the following section.

## Borders, shading, and cell content

Map explicit rules only. Apply cell margins, vertical alignment, shading, and paragraph spacing. Preserve multiple paragraphs, lists, hyperlinks, images, and OMML within cells. Do not flatten rich cell content into plain text.

## Table footnotes

Word footnotes inside tables can be fragile across renderers. Prefer table notes below the table when the source uses symbolic table notes. Preserve ordinary document footnotes only when target Word behavior is tested.

## Validation

For every table reconcile:

- logical row/column count;
- merged-cell spans;
- header rows and repeated headers;
- caption/label;
- displayed RTL column order;
- cell text and math;
- width within margins;
- page breaks and border continuity.

Inspect every multi-page table in the rendered output.
