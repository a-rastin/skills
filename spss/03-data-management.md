# 03 — Data Management (define, transform, restructure)

Source docs: Core System User Guide Ch. 7–9; Command Syntax Reference (`VARIABLE LABELS`, `VALUE LABELS`, `FORMATS`, `MISSING VALUES`, `RENAME`, `COMPUTE`, `IF`, `DO IF`, `RECODE`, `COUNT`, `AUTORECODE`, `RANK`, `SELECT IF`, `SAMPLE`, `SORT CASES`, `SPLIT FILE`, `WEIGHT`, `FILTER`, `AGGREGATE`, `MATCH/ADD FILES`, `VECTOR`, `DO REPEAT`, `LOOP`); Brief Guide Ch. 8–9; Data Preparation manual; SAS-Data-Management Guide Ch. 2, 6.

## Table of contents

1. Dictionary: labels, formats, missing, measure, roles
2. COMPUTE / IF / DO IF (+ functions)
3. RECODE / COUNT / AUTORECODE / RANK
4. DO REPEAT / VECTOR / LOOP
5. Selecting, sorting, splitting, weighting
6. Combining: MATCH FILES / ADD FILES / UPDATE / STAR JOIN
7. Aggregating and reshaping
8. Dates
9. Validation and cleaning workflow
10. Common snippets

---

## 1. Dictionary (metadata agents must get right)

```spss
VARIABLE LABELS age 'Age in years' income 'Annual household income (USD)'.
VALUE LABELS gender 1 'Male' 2 'Female' / inccat 1 'Low' 2 'Mid' 3 'High'.
ADD VALUE LABELS gender 9 'Unknown'.
FORMATS income (DOLLAR8.0) hiredate (ADATE10).
MISSING VALUES income (999999) gender (9).
RENAME VARIABLES (oldname = newname).
VARIABLE LEVEL age (SCALE) gender (NOMINAL) inccat (ORDINAL).
VARIABLE ROLE income (INPUT) default (TARGET) id (NONE).
VARIABLE ATTRIBUTE VARIABLES=income ATTRIBUTE=source('hr-extract 2026-09').
```

- `VARIABLE LABELS` / `VALUE LABELS` replace; `ADD VALUE LABELS` appends.
- `FORMATS` controls display (and sometimes input width). Common: `F8.0` numeric, `A24` string, `DOLLAR`, `COMMA`, `PCT`, `DATE/ADATE/SDATE`, `DATETIME`, `TIME`.
- String width is fixed at creation (`STRING city (A24).`); widening later truncates unless recreated. Plan widths before `SAVE`.
- `MISSING VALUES` declares user-missing (excluded from most stats but visible). System-missing (`$SYSMIS`, blank numeric) is always missing.
- Set measurement level (`SCALE/NOMINAL/ORDINAL`) — Trees, Models, and chart defaults depend on it.
- Audit with `DISPLAY DICTIONARY.` / `CODEBOOK`.

## 2. COMPUTE / IF / DO IF

```spss
COMPUTE bmi = weight_kg / (height_m ** 2).
COMPUTE agegrp = TRUNC((age - 18) / 10) + 1.
IF (gender = 2 AND income > 50000) bonus = income * 0.05.
DO IF (age >= 65).
  COMPUTE senior = 1.
ELSE IF (age >= 18).
  COMPUTE senior = 0.
ELSE.
  COMPUTE senior = $SYSMIS.
END IF.
EXECUTE.
```

Key functions (full list in Syntax Reference; these cover 90%):

- Arithmetic/string: `ABS MOD RND TRUNC LN LG10 EXP SQRT SUM MEAN MIN MAX NVALID NMISS`.
- Strings: `CONCAT SUBSTR INDEX UPCASE LOWER LTRIM RTRIM REPLACE VALUELBL`.
- Logical: `ANY(v,a,b,c) RANGE(v,lo,hi) MISSING(v) SYSMIS(v) VALUE(v)`.
- Distributions/RV: `NORMAL(1) UNIFORM(1) RV.NORMAL(m,s) RV.UNIFORM(a,b)` — set seed first (`SET MTINDEX=` or `SET SEED=`).
- Dates: `XDATE.YEAR(d) XDATE.MONTH(d) XDATE.MDAY(d) DATEDIFF(d1,d2,'days') DATESUM(d,n,'days') YRMODA(y,m,d)`.
- Lags/leads need sorted file: `LAG(v) LAG(v,2) LEAD(v)`.

`TEMPORARY.` + transform + procedure = one-off test without changing data:

```spss
TEMPORARY.
RECODE income (Lowest THRU 30000=1) (30000 THRU Highest=2) INTO income2.
FREQUENCIES VARIABLES=income2.
```

## 3. RECODE / COUNT / AUTORECODE / RANK

```spss
RECODE gender ('m'=1) ('f'=2) (ELSE=9) INTO gender_n.
RECODE income (MISSING=SYSMIS) (999999=SYSMIS).
RECODE age (18 THRU 29=1) (30 THRU 44=2) (45 THRU Hi=3) (ELSE=SYSMIS) INTO agegrp.
COUNT n_missing = age income educ (MISSING).
AUTORECODE VARIABLES=dept /INTO dept_n /PRINT.
RANK VARIABLES=income /NTILES(5) INTO income_q /PRINT=YES /TIES=MEAN.
EXECUTE.
```

- `RECODE ... INTO ...` preserves the original; bare `RECODE v ...` overwrites. Prefer `INTO` for auditability.
- Ranges: `LO THRU x`, `x THRU HI`, `MISSING`, `SYSMIS`, `ELSE`. Overlapping ranges apply first-match.
- `AUTORECODE` maps strings → consecutive integers (needed by Categories, Trees, some models).
- Visual Binning dialog ≈ `RECODE` with cutpoints; Optimal Binning (`Transform > Optimal Binning`) is supervised (uses a guide variable) — see `05-advanced-models.md`.

## 4. DO REPEAT / VECTOR / LOOP

```spss
DO REPEAT r = q1 TO q5 / #i = 1 TO 5.
  IF (MISSING(r)) r = 0.
END REPEAT.
VECTOR weekly(7, F8.0).
LOOP #d = 1 TO 7.
  COMPUTE weekly(#d) = 0.
END LOOP.
EXECUTE.
```

- `DO REPEAT` stand-ins expand at compile time; `#i` scratch vars vanish after.
- `VECTOR` creates/short-names a set; `LOOP ... END LOOP` iterates cases. Set `SET MXLOOPS=` guard for large loops.

## 5. Selecting, sorting, splitting, weighting

```spss
SELECT IF (age >= 18 AND NOT MISSING(income)).
SAMPLE .10.                    /* 10% random sample */
SAMPLE 500 FROM 2000.          /* 500 of 2000 */
SORT CASES BY dept (A) salary (D).
SPLIT FILE SEPARATE BY gender. /* or LAYERED; OFF to disable */
WEIGHT BY sampwt.
FILTER BY flag_var.            /* 0/missing = excluded */
USE ALL.
EXECUTE.
```

- `SELECT IF` deletes unselected cases permanently on `SAVE` — test with `TEMPORARY.` + `FREQUENCIES` or save to a new file first.
- `SPLIT FILE` affects all subsequent procedures until `SPLIT FILE OFF.`
- `WEIGHT` (sampling weights) is not Complex-Samples design adjustment — for stratified/cluster designs use `CSPLAN` + `CS*` procedures (see 05).

## 6. Combining files

```spss
* Row-wise (same variables, new cases) — files must be sorted only for MATCH; ADD needs same vars.
ADD FILES FILE='/data/wave1.sav' /FILE='/data/wave2.sav'.
SAVE OUTFILE='/out/stacked.sav'.

* Column-wise keyed join — both sorted by key first.
SORT CASES BY id.
MATCH FILES FILE=* /FILE='/data/lookup.sav' /BY id.
EXECUTE.

* Keyed with non-matches kept/dropped.
MATCH FILES FILE=* /TABLE='/data/lookup.sav' /BY id.  /* TABLE = lookup, keeps all master */
UPDATE FILE=* /FILE='/data/corrections.sav' /BY id.    /* UPDATE overwrites non-missing */
STAR JOIN ... .  /* large fuzzy/approximate joins; see Syntax Reference */
```

Always `SORT CASES BY key` on both inputs before `MATCH/UPDATE`. `APPLY DICTIONARY` after a join to restore labels lost from the secondary file.

## 7. Aggregating and reshaping

```spss
* One row per dept with means and N.
AGGREGATE OUTFILE='/out/dept_means.sav'
  /BREAK=dept
  /mean_salary=MEAN(salary) /n=N /sd_salary=SD(salary).

* Restructure wide<->long (dialog: Data > Restructure).
VARSTOCASES /MAKE salary FROM sal2024 sal2025 /INDEX=year.
CASESTOVARS /ID=id /INDEX=year /SEPARATOR=_.
FLIP VARIABLES=id name /NEWNAMES=varname.
```

Aggregation functions: `SUM MEAN MEDIAN SD MIN MAX N NU NMISS FIRST LAST` (+ `PLT/PGT/PIN/POUT` percentiles).

## 8. Dates

```spss
COMPUTE tenure_days = DATEDIFF($DATE, hiredate, 'days').
COMPUTE fy_start = DATESUM(hiredate, 0, 'years').  /* truncated */
COMPUTE hire_year = XDATE.YEAR(hiredate).
COMPUTE hire_month = XDATE.MONTH(hiredate).
FORMATS tenure_days (F8.0) hiredate (ADATE10).
EXECUTE.
```

Define Dates (`DATA > Define Dates`) + `DATE` command creates time-series cycle vars for Forecasting (`05`).

## 9. Validation and cleaning workflow

From the Data Preparation manual:

1. **Rules**: `Data > Validation > Define Rules` (range, list, cross-variable logic) → saved to dictionary, reusable monthly.
2. **Validate**: `VALIDATE DATA VARIABLES=... /RULES=...` → violations table; save flags.
3. **Auto-prep**: `ADP` (Automated Data Preparation: fix dates, rescale, bin, select/construct fields, rename via XML) for modeling feeds.
4. **Anomalies**: `DETECTANOMALY` (peer-group index + impact) — randomise order-sensitive data first.
5. **Binning**: `Transform > Optimal Binning` (supervised cutpoints, reusable syntax) vs Visual Binning (`RECODE`).

Always keep raw → clean as separate files with a cleaning `.sps` in between; `DOCUMENT` the steps in the `.sav`.

## 10. Common snippets

```spss
* Dedup, keep first per id.
SORT CASES BY id.
MATCH FILES FILE=* /BY id /FIRST=first_flag.
SELECT IF (first_flag = 1).
DROP first_flag.
EXECUTE.

* Z-score within group.
SPLIT FILE SEPARATE BY dept.
DESCRIPTIVES VARIABLES=salary /SAVE.  /* creates Zsalary */
SPLIT FILE OFF.
EXECUTE.

* Missing-value audit.
MVA VARIABLES=age income educ
  /MPATTERN /DPATTERN /TPATTERN
  /TTEST /MISMATCH.
```
