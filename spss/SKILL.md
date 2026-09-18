---
name: spss
description: Create and edit IBM SPSS Statistics files (.sps syntax, .sav/.zsav data, .spv output jobs). Use whenever the user mentions SPSS, syntax commands, SAV data, FREQUENCIES/REGRESSION/GLM/MIXED/FACTOR/CTABLES/GGRAPH, or pasting dialogs to syntax — even if they don't say the word 'skill'.
---

# SPSS

Create and edit IBM SPSS Statistics files: syntax (`.sps`), data (`.sav`/`.zsav`), and output/export jobs (`.spv`).

## Workflow

1. **Identify task type** — new syntax, edit existing `.sps`, define/import data, run analysis, chart/table, output/export, Python/R integration.
2. **Read the matching reference** (read only what you need):
   - Syntax rules, terminators, comments, variables, execution modes → `references/01-syntax-fundamentals.md`
   - File types, GET/SAVE, imports/exports, encodings → `references/02-data-files.md`
   - Data definition and transformation (COMPUTE, RECODE, MERGE, AGGREGATE) → `references/03-data-management.md`
   - Descriptives and Base procedures (FREQUENCIES → RELIABILITY) → `references/04-descriptives-base.md`
   - Advanced modules (Regression, GLM/MIXED/GENLIN, Survival, Categories, Complex Samples, Forecasting, Trees, Neural, Conjoint, Missing Values, etc.) → `references/05-advanced-models.md`
   - Custom Tables, charts/GPL, OMS and output export → `references/06-tables-charts-output.md`
   - Python (`BEGIN PROGRAM PYTHON3`) and R (`BEGIN PROGRAM R`) integration → `references/07-python-r-integration.md`
   - Fast command lookup (alphabetical index with one-line purpose) → `references/08-command-index.md`
3. **Start from a template** in `assets/templates/` when creating a new file; preserve the header block (purpose, data source, date).
4. **Validate** before finishing: run `scripts/validate_sps.py <file.sps>` (stdlib only). For data-file creation from CSV, use `scripts/new_sav.py --help`.
5. **Never assume SPSS is installed.** Generate correct syntax + instructions to run (`Run > Selection` or `INSERT FILE=`); do not claim you executed it unless you did.

## Hard rules (from the manuals)

- Every command ends with `.` as the last non-blank character. `BEGIN DATA` has no `.`; data lines have no `.`; `END DATA` starts in column 1.
- One command starts per line; subcommands start with `/`; use `=` where the reference shows it.
- Variable names: ≤64 bytes, start with letter or `@ # $`, no spaces, no leading/trailing `.`, never a reserved word (`ALL AND BY EQ GE GT LE LT NE NOT OR TO WITH`).
- Comments between commands only: `* ... .` or `COMMENT ... .`; inline `/* ... */` only where a blank is legal — never on its own line inside a command.
- Transformations (`COMPUTE IF RECODE COUNT SELECT IF ...`) are pending until the next data-reading procedure (`FREQUENCIES LIST SAVE EXECUTE ...`). Add `EXECUTE.` when you need them forced.
- Prefer `INSERT FILE=` over `INCLUDE`; use forward slashes in paths: `GET FILE='/data/demo.sav'.`
- This skill writes `.sps` (text) and helper-generated data files. It does not write binary `.spv` directly — generate the syntax + `OUTPUT SAVE` / `OUTPUT EXPORT` step instead.

## Examples

**Example 1 — new analysis:**
User: "Frequencies on gender and income in demo.sav"
Do: GET FILE → FREQUENCIES with BARCHART → OUTPUT EXPORT. See `assets/templates/minimal-analysis.sps`.

**Example 2 — edit data definition:**
User: "Add value labels to this .sps"
Do: read file, edit `VALUE LABELS` / `VARIABLE LABELS` / `MISSING VALUES` blocks per `references/03-data-management.md`, then validate.

**Example 3 — advanced model:**
User: "Binary logistic for default on age/income"
Do: read `references/05-advanced-models.md` (LOGISTIC REGRESSION section), emit `LOGISTIC REGRESSION ... /METHOD=ENTER ... /SAVE=PRED ... .`
