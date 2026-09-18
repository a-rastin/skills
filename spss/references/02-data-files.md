# 02 — Data Files (.sps, .sav, .zsav, .por, imports/exports)

Source docs: Core System User Guide Ch. 3–6, 9, 22, 26; Command Syntax Reference (`GET`, `SAVE`, `GET DATA`, `DATA LIST`, `FILE HANDLE`, `SAVE TRANSLATE`, `EXPORT/IMPORT`, `APPLY DICTIONARY`, `SYSFILE INFO`); Data File Driver Guide; SAS-Data-Management Guide Ch. 2.

## Table of contents

1. File-type map
2. Opening data: GET / GET DATA / DATA LIST
3. Saving data: SAVE / XSAVE / SAVE TRANSLATE / EXPORT
4. Inline data (BEGIN DATA)
5. Text/Excel/CSV/SAS/Stata/ODBC imports
6. Encodings (Unicode vs locale) and encryption
7. Inspecting files (SYSFILE INFO, DISPLAY, CODEBOOK)
8. DATASET MANAGEMENT (multiple open files)
9. ODBC driver (read .sav as SQL)
10. Recipes

---

## 1. File-type map

| Ext | What | How created | How opened |
|-----|------|-------------|------------|
| `.sps` | Syntax (text) | Syntax Editor, `Paste`, any text editor | `File > Open > Syntax`, `INSERT FILE=` |
| `.sav` | Data + dictionary (binary) | `SAVE OUTFILE=`, `File > Save` | `GET FILE=` |
| `.zsav` | Compressed data (v21+, always UTF-8) | `SAVE ... /ZCOMPRESSED.` | `GET FILE=` (same as `.sav`) |
| `.por` | Portable (8-byte names, legacy exchange) | `EXPORT OUTFILE=` | `IMPORT FILE=` |
| `.spv` | Viewer output (binary) | `OUTPUT SAVE`, dialogs | Viewer; never hand-edit |
| `.stt` | TableLook template | Tables UI | Applied to pivots |
| `.csplan/.csaplan` | Complex Samples plans | Sampling/Analysis Prep wizards | `/PLAN FILE=` subcommand |
| `.xml` (model) | Saved models/TSMODEL | `OUTFILE` subcommands | `TSAPPLY`, scoring |
| `.sav` via OMS | Output tables as data | `OMS ... /DESTINATION FORMAT=SAV` | `GET FILE=` |

Never write binary files by hand. Agents write `.sps` text; `.sav` is produced by SPSS (`SAVE`) or by `scripts/new_sav.py` (CSV → SAV via pandas/pyreadstat) when SPSS is unavailable.

## 2. Opening data

```spss
* SPSS native.
GET FILE='/data/demo.sav'.
* Compressed — identical syntax.
GET FILE='/data/demo.zsav'.

* Named file handle (reuse long paths).
FILE HANDLE demo /NAME='/data/demo.sav'.
GET FILE=demo.

* All open datasets list.
DATASET NAMES.
```

## 3. Saving data

```spss
SAVE OUTFILE='/out/clean.sav'
  /KEEP=id age gender income
  /COMPRESSED.          /* or /ZCOMPRESSED for .zsav semantics */
XSAVE OUTFILE='/out/clean.sav'  /* pending-execution variant; needs a reader to flush */.

* Rename/map on save.
SAVE OUTFILE='/out/clean.sav' /MAP /RENAME=(old1=new1) /DROP=temp1 temp2.

* Password-protect (v21/22+, ≤10 chars, case-sensitive; loss = unrecoverable).
SAVE OUTFILE='/out/secure.sav' /PASSPROTECT='s3cretKey'.

* Portable (8-byte names only; not in Unicode mode).
EXPORT OUTFILE='/out/legacy.por'.
IMPORT FILE='/out/legacy.por'.

* Other formats.
SAVE TRANSLATE OUTFILE='/out/clean.csv' /TYPE=CSV /ENCODING='UTF8' /FIELDNAMES.
SAVE TRANSLATE OUTFILE='/out/clean.xlsx' /TYPE=XLSX /FIELDNAMES /CELLS=VALUES.
SAVE TRANSLATE OUTFILE='/out/clean.dta' /TYPE=STATA.
```

`SAVE` is immediate; `XSAVE` waits for the next reader. Prefer `SAVE` unless building a multi-step pending chain.

## 4. Inline data (BEGIN DATA)

For small reproducible examples only (≤1024 bytes/line):

```spss
DATA LIST FREE / id (F8.0) gender (A8) income (F8.0).
BEGIN DATA
1 male 52000
2 female 61000
3 female 48000
END DATA.
EXECUTE.
```

- `BEGIN DATA` has no `.`; data lines have no `.`; `END DATA` starts in col 1 and the command ends with `.`.
- Fixed format alternative: `DATA LIST FIXED / id 1-4 gender 6-11 (A) income 13-20.`
- `INPUT PROGRAM ... END INPUT PROGRAM.` for complex generated input; `REREAD`, `REPEATING DATA`, `FILE TYPE` for nested/hierarchical text (see Command Index + `Defining Complex Files` appendix).

## 5. Imports

```spss
* CSV / TXT.
GET DATA /TYPE=TXT
  /FILE='/data/raw.csv'
  /ENCODING='UTF8'
  /ARRANGEMENT=DELIMITED
  /DELCASE=LINE
  /DELIMITERS=","
  /QUALIFIER='"'
  /FIRSTCASE=2
  /VARIABLES=id F8.0 gender A8 income F8.0.
CACHE.
EXECUTE.

* Excel.
GET DATA /TYPE=XLSX
  /FILE='/data/raw.xlsx'
  /SHEET=NAME 'Sheet1'
  /CELLRANGE=FULL
  /READNAMES=ON.
CACHE.
EXECUTE.

* SAS / Stata / delimited generics.
GET SAS DATA='/data/demo.sd7'.
GET STATA FILE='/data/statafile.dta'.
GET TRANSLATE FILE='/data/legacy.wk1' /TYPE=WK1.

* Databases (ODBC).
GET DATA /TYPE=ODBC /CONNECT='DSN=mydb;UID=user;PWD=***'
  /SQL='SELECT age, marital, inccat, gender FROM demo.Cases WHERE age > 40'.
CACHE.
EXECUTE.
```

Always follow `GET DATA` with `CACHE. EXECUTE.` so the data is materialised and later runs don't re-query. Protect the raw file: do transforms on a copy and `SAVE` to a new path.

## 6. Encodings and encryption

- Default since v16 is Unicode mode (`SET UNICODE ON.`). Save with `SET UNICODE ON` unless the consumer needs legacy locale encoding (v7.0 compat option in `Save As`).
- `.por` cannot be written in Unicode mode; switch or use `.sav`/CSV for exchange.
- `.zsav` is always UTF-8.
- Text I/O: specify `/ENCODING='UTF8'` (or `'Locale'`) on both `GET DATA` and `SAVE TRANSLATE`/`WRITE`.
- Encrypted `.sav/.spv/.sps` (Ch. 26): password ≤10 chars, case-sensitive, v21/22+ only. `SAVE ... /PASSPROTECT='...'`. Warn the user to store the password separately.

## 7. Inspecting files

```spss
SYSFILE INFO FILE='/data/demo.sav'.   /* dictionary dump to output */
DISPLAY DICTIONARY.                    /* active-file dictionary */
DISPLAY VARIABLES.
CODEBOOK gender income
  /VARINFO LABEL VALUELABELS MISSING MEASURE
  /OPTIONS VARORDER=MEASURE.
APPLY DICTIONARY FROM='/data/master.sav'
  /SOURCE VARIABLES=id gender /TARGET VARIABLES=id gender.
DOCUMENT This file cleaned 2026-09-18: deduped, labelled, see clean.sps.
ADD DOCUMENT Second line of file history.
```

`CODEBOOK` is the fastest human-readable audit; `SYSFILE INFO` audits a file without opening it.

## 8. Multiple open datasets

```spss
DATASET NAME demographics WINDOW=HIDDEN.
DATASET ACTIVATE demographics.
DATASET COPYSubset WINDOW=HIDDEN.
DATASET CLOSE subset.
SHOW DATASETS.  /* via SHOW? use DATASET DISPLAY in newer releases; SHOW ALL lists session state */
```

Rules: one active dataset; transforms apply to the active one; `DATASET ACTIVATE` before `SAVE` to be sure which file you write.

## 9. ODBC driver (read .sav as SQL)

With the Data File Driver installed, any ODBC/JDBC client (or SPSS itself) can query `.sav`:

```spss
GET DATA /TYPE=ODBC
  /CONNECT="DRIVER=IBM SPSS Statistics 22 Data File Driver - Standalone;SDSN=SAVDB;"
  /SQL="SELECT age, marital, inccat, gender FROM demo.Cases WHERE (age > 40 AND gender = 'm')".
CACHE.
EXECUTE.
APPLY DICTIONARY FROM '/examples/data/demo.sav'.
```

Views: `CasesView` (value labels applied, preferred), `Cases` (raw + `RECORD_NUM`), plus `Variables`, `VarAttributes`, `MrSets`, etc. Use for BI tools, not for routine editing.

## 10. Recipes

**Open → audit → save cleaned copy:**

```spss
SET UNICODE ON.
GET FILE='/data/demo.sav'.
CODEBOOK ALL /VARINFO LABEL VALUELABELS MISSING /OPTIONS VARORDER=MEASURE.
FREQUENCIES VARIABLES=ALL /FORMAT=NOTABLE /STATISTICS=MINIMUM MAXIMUM MEAN.
SAVE OUTFILE='/out/demo_clean.sav' /COMPRESSED.
```

**CSV → SAV (inside SPSS):**

```spss
GET DATA /TYPE=TXT /FILE='/data/raw.csv' /ENCODING='UTF8'
  /ARRANGEMENT=DELIMITED /DELCASE=LINE /DELIMITERS="," /QUALIFIER='"'
  /FIRSTCASE=2 /VARIABLES=id F8.0 gender A8 income F8.0.
CACHE.
EXECUTE.
VARIABLE LABELS id 'Respondent ID' income 'Annual income (USD)'.
VALUE LABELS gender 'm' 'Male' 'f' 'Female'.
SAVE OUTFILE='/out/raw.sav' /COMPRESSED.
```

**Without SPSS installed:** use `scripts/new_sav.py input.csv output.sav --labels labels.json` (pandas/pyreadstat) then write analysis `.sps` against the future `.sav` path and tell the user to run it in SPSS.
