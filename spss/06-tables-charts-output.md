# 06 — Custom Tables, Charts/GPL, Output and OMS

Source docs: Custom Tables, GPL Reference, Core System User Guide Ch. 10–14, 22–24, Brief Guide Ch. 5–6, Statistics Base (P-P/Q-Q, ROC, Time-Series plots).

## Table of contents

1. Custom Tables (CTABLES)
2. Classic charts vs GGRAPH/GPL
3. GPL essentials (wrapper + ELEMENT gallery)
4. Output: Viewer, pivot tables, TableLooks
5. OUTPUT SAVE / OUTPUT EXPORT
6. OMS (Output Management System)
7. Production jobs and scripting hooks
8. Recipes

---

## 1. Custom Tables (CTABLES)

GUI: `Analyze > Tables > Custom Tables` (Table Builder). Concepts that map directly to syntax:

- **Stacking** (variables one below another), **Nesting** (`A > B` иерархия in rows/cols), **Layers** (separate panels).
- Totals: `What You See Is What Gets Totaled`; display position; nested/layer totals; custom total summaries.
- Summaries: `Count, Valid N, Missing, Mean, Median, %, Row/Col %, Confidence Intervals, Tests of Independence (Chi-Square), Compare Column Means/Proportions`.
- Multiple Response Sets and weights need explicit handling (see dialog notes).

Sample data throughout the manual: `survey_sample.sav` (NORC GSS subset). Note: >12,000 value labels forces syntax (`CTABLES`) instead of the Builder. `CTABLES` itself is fully specified in the Syntax Reference — keep pasted Builder syntax verbatim; typical head:

```spss
CTABLES
  /TABLE gender [C] BY inccat [C]
  /CATEGORIES VARIABLES=gender inccat ORDER=A KEY=VALUE EMPTY=INCLUDE
  /TITLES TITLE='Demo profile'.
```

Adjust `ORDER` (A/D), `EMPTY` (INCLUDE/EXCLUDE), `MISSING` handling, and `/TEST` subcommands only as documented in the Syntax Reference.

## 2. Classic charts vs GGRAPH/GPL

- **Chart Builder / Chart Facility (Ch. 16):** bar/line/pie/histogram/scatter/box/P-P/Q-Q/ROC/pareto/population-pyramid. Dialog-paste emits either legacy (`GRAPH`, `BAR`, `HISTOGRAM`, `EXAMINE /PLOT=...`) or `GGRAPH` blocks. Keep pasted blocks.
- **Legacy quick charts:**

```spss
FREQUENCIES VARIABLES=gender /BARCHART PERCENT /PIECHART FREQ.
GRAPH /BAR(SIMPLE)=PCT BY gender.
EXAMINE VARIABLES=income /PLOT=BOXPLOT HISTOGRAM NPPLOT.
PPLOT VARIABLES=income /TYPE=Q-Q /DIST=NORMAL.
```

- **GGRAPH/GPL** for anything custom (facets, aesthetics, densities, binning). Required wrapper — GPL never runs standalone.

## 3. GPL essentials

```spss
GGRAPH
  /GRAPHDATASET NAME="Employeedata" VARIABLES=jobcat salary
  /GRAPHSPEC SOURCE=INLINE.
BEGIN GPL
  SOURCE: s = userSource(id("Employeedata"))
  DATA: jobcat = col(source(s), name("jobcat"), unit.category())
  DATA: salary = col(source(s), name("salary"))
  COORD: rect(dim(1,2))
  SCALE: linear(dim(2), min(0))
  ELEMENT: interval(position(summary.mean(jobcat*salary)))
END GPL.
```

Statements: `SOURCE, DATA, TRANS, COORD, SCALE, GUIDE, ELEMENT, PAGE, GRAPH, COMMENT`. Key functions:

- Geometry: `ELEMENT: point | interval | line | area | polygon | schema | contour | edge`.
- Position/summary: `position(...)`, `summary.mean/count/sum/median`, `bin.rect/hex/dot`, `density.normal/kernel`.
- Aesthetics: `color(...) size(...) shape(...) transparency(...) label(...)`.
- Layout: `layout.grid/network`, `scale(...)`, faceting via `row()/column()` in position.

ELEMENT gallery (swap the last line above):

```
ELEMENT: point(position(salbegin*salary))
ELEMENT: interval(position(summary.count(jobcat)))
ELEMENT: interval(position(summary.mean(jobcat*salary*gender)), color(jobcat))
ELEMENT: line(position(summary.mean(date*salary)))
ELEMENT: schema(position(bin.rect(salary)))   /* histogram */
```

Rules: `GRAPHDATASET VARIABLES=` must cover every `DATA:` column; `userSource(id(...))` must match `NAME=`; coordinates default `rect`, use `polar` for pie/coxcomb.

## 4. Output: Viewer, pivot tables, TableLooks

- Viewer (`*.spv`, Ch. 10): Classic vs Workbook modes; Outline pane + Contents pane. AI Output Assistant (Ch. 11) summarises selected blocks. Pivot Table Editor: transpose, sort, group, hide, decimal control; TableLooks (`*.stt`) restyle en masse. Chart Editor annotates GPL output.
- Automated Output Modification (Ch. 14): `Analyze > ...` + `Utilities > ...` rules to rename/reorder/hide blocks — record as production-job steps.
- `TABLES/IGRAPH Converter` (`syntaxconverter.exe input.sps output.sps [-b]`) migrates legacy `TABLES/IGRAPH` to `CTABLES/GGRAPH`.

## 5. OUTPUT SAVE / OUTPUT EXPORT

```spss
OUTPUT SAVE OUTFILE='/out/analysis.spv'.
OUTPUT EXPORT
  /CONTENTS EXPORT=VISIBLELAYERS MODELDIALOGS=PRINTABLE
  /XLSX DOCUMENTFILE='/out/tables.xlsx' OPERATION=CREATESHEET
  /PDF DOCUMENTFILE='/out/report.pdf' EMBEDFONTS=YES.
```

Targets: Word/Excel/PowerPoint/PDF/HTML/XML/text. `EXPORT=VISIBLELAYERS` respects hidden layers; use `ALLLAYERS` to dump everything.

## 6. OMS (Output Management System, Ch. 23)

Route output objects to data/files for downstream use:

```spss
OMS
  /SELECT TABLES
  /IF COMMANDS=['Frequencies' 'Regression'] SUBTYPES=['Frequencies' 'Coefficients']
  /DESTINATION FORMAT=SAV OUTFILE='/out/coefs.sav' VIEWER=YES
  /TAG='myrun'.
FREQUENCIES VARIABLES=gender income.
REGRESSION /DEPENDENT income /METHOD=ENTER age educ.
OMSEND TAG='myrun'.

* Alternate destinations: FORMAT=XLSX/DOC/PDF/XML/HTML/TEXT, plus /COLUMNS, /IMAGES.
```

Patterns: one `OMS ... /TAG` → analysis → `OMSEND TAG`. Use `VIEWER=YES` to keep interactive output while also saving. `SHOW OMS.` lists active routings.

## 7. Production jobs and scriptinghooks

- Production Facility (Ch. 22): `.spp` jobs bundle `.sps` + data + output + OMS + scheduling; run headless via `stats.exe -production job.spj`.
- Scoring (Ch. 17): `MODEL HANDLE`, scoring wizard, PMML/XML export from Trees/Neural/Regression — apply with `APPLYMODEL` or `TSAPPLY`.
- Scripting (Ch. 24): Basic/Python autoscripts on output items; Extensions (Ch. 21) install `STATS ...` commands.
- Encryption (Ch. 26): `SAVE ... /PASSPROTECT` for data; Viewer/Syntax encryption in `File > Save As`.

## 8. Recipes

```spss
* Tables + charts + export bundle.
CTABLES /TABLE gender [C] BY inccat [C] /CATEGORIES VARIABLES=ALL ORDER=A EMPTY=INCLUDE.
GGRAPH /GRAPHDATASET NAME="d" VARIABLES=jobcat salary /GRAPHSPEC SOURCE=INLINE.
BEGIN GPL
  SOURCE: s = userSource(id("d"))
  DATA: jobcat = col(source(s), name("jobcat"), unit.category())
  DATA: salary = col(source(s), name("salary"))
  ELEMENT: interval(position(summary.mean(jobcat*salary)))
END GPL.
OUTPUT EXPORT /CONTENTS EXPORT=VISIBLELAYERS /XLSX DOCUMENTFILE='/out/bundle.xlsx'.

* Harvest coefficients as data.
OMS /SELECT TABLES /IF COMMANDS=['Regression'] SUBTYPES=['Coefficients']
  /DESTINATION FORMAT=SAV OUTFILE='/out/coefs.sav' VIEWER=YES /TAG='reg'.
REGRESSION /DEPENDENT income /METHOD=ENTER age educ.
OMSEND TAG='reg'.
GET FILE='/out/coefs.sav'.
```
