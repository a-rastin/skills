# 01 — Syntax Fundamentals

Source docs: `IBM_SPSS_Statistics_Command_Syntax_Reference` (Universals, Commands, COMMENT, DEFINE/!ENDDEFINE, INCLUDE/INSERT, SET/SHOW), `IBM_SPSS_Statistics_Core_System_User_Guide` Ch. 15, `IBM_SPSS_Statistics_Brief_Guide` Ch. 7.

Read this file whenever you write or edit any `.sps` file.

## Table of contents

1. What a `.sps` file is
2. Interactive vs batch (INCLUDE/INSERT) modes
3. Commands, subcommands, keywords
4. Terminator `.` and blank lines
5. Line length and case
6. Variable names, lists, scratch/system variables
7. Constants (numbers, strings, dates)
8. Comments
9. Command order and program states (pending vs immediate)
10. EXECUTE and data-reading procedures
11. Abbreviations
12. Macros (DEFINE)
13. SET/SHOW essentials
14. Minimal valid file + checklist

---

## 1. What a `.sps` file is

- Plain-text command file, conventionally UTF-8, extension `.sps`.
- Open with `File > Open > Syntax`; run selection with `Run > Selection` (or `INSERT FILE='/path/file.sps'.`).
- The pasted output of any dialog (`Paste` button) is valid syntax — when in doubt, describe the dialog clicks and emit the pasted equivalent.
- Journal file (`journal.jnl`) logs every executed command; it is editable into a `.sps` file.

## 2. Interactive vs batch modes

**Interactive (Syntax Editor, default):**

- Each command may start in any column but must start on a new line.
- Each command ends with `.` as the last non-blank character. A fully blank line also terminates a command.
- Continuation lines are free-form.

**Batch (`INCLUDE FILE=`):**

- Every command must begin in column 1; continuation lines must have column 1 blank (use `+`/`-` for indent display).
- Lines limited to 256 characters (truncated beyond).
- Terminators optional but keep them anyway.

**Rule: always write `INSERT`-compatible syntax** (starts in col 1 where practical, always terminated, ≤256 chars/line). Prefer `INSERT` over `INCLUDE`:

```spss
INSERT FILE='/projects/analysis/clean.sps'.
```

`INSERT` accepts both interactive and batch layouts; `INCLUDE` accepts batch only.

## 3. Commands, subcommands, keywords

```
CODEBOOK gender
  /VARINFO LABEL VALUELABELS MISSING
  /OPTIONS VARORDER=MEASURE.
```

- **Command**: first word (`CODEBOOK`, `FREQUENCIES`, `COMPUTE`). Case-insensitive.
- **Subcommand**: introduced by `/` (`/VARINFO`, `/OPTIONS`). The first `/` may be omitted on some commands, but always write it.
- **Keyword**: named option inside a subcommand (`VARORDER`), followed by `=` and **keyword values** (`MEASURE`).
- `=` is required exactly where the Syntax Reference shows it. Do not add or drop it by guess.

## 4. Terminator `.` and blank lines

- `.` must be the last non-blank character of the command. Nothing (not even a comment) follows it on the same line.
- Exceptions with NO trailing `.`:
  - `BEGIN DATA` (no period)
  - Inline data lines themselves (no period)
- `END DATA` must start in column 1, with exactly one space after it if data is on the same line, else on its own line:

```spss
DATA LIST FREE / age (F8.0) income (F8.0).
BEGIN DATA
34 52000
41 61000
END DATA.
```

- Never leave a blank line in the middle of a command — it terminates the command and the remainder errors.

## 5. Line length and case

- Keep every line ≤ 251 display chars (hard limit 256 in batch). Long lines show red in the editor.
- Commands/keywords are case-insensitive (`frequencies` = `FREQUENCIES`); inline string data IS case-sensitive.
- Decimal separator is always `.` regardless of locale (`3.14`, never `3,14`).
- Quoted strings must fit on one line: `'Customer satisfaction'` or `"m"`.

## 6. Variable names, lists, scratch/system variables

Valid names:

- Unique, ≤64 bytes. First char: letter or `@`, `#`, `$`. Rest: letters, digits, `.`, `_`, `$`, `#`, `@`.
- No spaces. No leading or trailing `.` (trailing `.` is confused with the terminator). Avoid trailing `_`.
- Mixed case is preserved for display but matching is case-insensitive.
- Reserved words forbidden as names: `ALL AND BY EQ GE GT LE LT NE NOT OR TO WITH`.
- Use `TO` for consecutive-dictionary ranges (`age1 TO age5`) and `ALL` for all variables. `TO` depends on file order — after reordering, verify.
- `#name` = scratch variable: exists only during syntax execution, never saved to `.sav`. Useful in `LOOP`/`VECTOR`.
- `$name` = system variable (`$CASENUM`, `$SYSMIS`, `$DATE`, `$TIME`, `$LENGTH`, `$WIDTH`).
- 3–4 letter command abbreviations are legal (`FREQ VAR=...`) but **never abbreviate in generated files** — always spell out (`FREQUENCIES VARIABLES=...`) for readability.

## 7. Constants

- Numbers: optional sign, `.` decimal, optional `E` exponent (`-12.5`, `1.0E3`).
- Strings: single or double quotes, single line, double the quote to embed (`'O''Brien'`).
- Dates/times: SPSS stores datetimes as seconds since 1582-10-14. Prefer readable constructors over raw numbers; see `03-data-management.md` for date functions.

## 8. Comments

Only between commands:

```spss
* This is a comment.
COMMENT This is also a comment.
```

- `* text.` and `COMMENT text.` are separate commands: they need their own line and their own terminating `.`. They print in output but are not saved.
- Inline `/* ... */` is allowed only where a blank would be legal (between tokens, never inside a quoted string or inline data). Never put it on its own line inside a command — the line break reads as a blank-line terminator and breaks the command:

```spss
* GOOD.
FREQUENCIES VARIABLES=gender /* demographic */ income
  /BARCHART PERCENT.

* BAD — standalone comment line inside command breaks it.
* FREQUENCIES VARIABLES=gender
*   /* comment on its own line */
*   /BARCHART PERCENT.
```

## 9. Command order and program states

Two families (Syntax Reference appendix "Commands and Program States"):

**Immediate-effect (dictionary-altering or session):** executed when encountered. Examples: `GET`, `SET`, `SHOW`, `TITLE`, `SUBTITLE`, `INCLUDE`/`INSERT`, `OUTPUT SAVE`, plus dictionary commands `VALUE LABELS`, `ADD VALUE LABELS`, `VARIABLE LABELS`, `FORMATS`, `MISSING VALUES`, `RENAME VARIABLES`, `APPLY DICTIONARY`, `DOCUMENT`.

**Pending-execution (transformations):** queued, executed on the next data-reading procedure. Examples: `COMPUTE`, `IF`, `DO IF`, `RECODE`, `COUNT`, `SELECT IF`, `FILTER`, `WEIGHT`, `TEMPORARY`, `LOOP`, `DO REPEAT`, `VECTOR`.

Data-reading procedures that flush the pending queue: `LIST`, `FREQUENCIES`, `DESCRIPTIVES`, `CROSSTABS`, `SAVE`, `XSAVE`, `SORT CASES` (some contexts), `EXECUTE`, and most analysis procedures.

Consequences:

- `TEMPORARY.` affects only the next procedure. A second procedure after it sees unmodified data.
- `SELECT IF` before `SAVE` filters what is saved; `SELECT IF` after the last procedure with no following reader does nothing until the next reader runs.

## 10. EXECUTE and data-reading procedures

- End a transformation block with `EXECUTE.` when you need values materialised now (before `LIST`, before checking, before a Python block that reads cases):

```spss
COMPUTE bmi = weight_kg / (height_m ** 2).
EXECUTE.
FREQUENCIES VARIABLES=bmi /FORMAT=NOTABLE /STATISTICS=MEAN MEDIAN.
```

- Do not sprinkle `EXECUTE.` after every line; one per block is enough. Pasted dialog syntax never includes it unnecessarily.

## 11. Macros (DEFINE)

For repeated boilerplate, use the macro facility (`Universals > Using Macro Facility`):

```spss
DEFINE !myfreq (vars = !TOKENS(1))
FREQUENCIES VARIABLES=!vars
  /BARCHART PERCENT
  /ORDER=ANALYSIS.
!ENDDEFINE.

!myfreq vars = gender.
```

- Macro calls start with `!`, expand before execution. Keep macros small; prefer `INSERT` files over clever macros for maintainability.
- `SET MPRINT ON.` echoes expansions for debugging; `SET MPRINT OFF.` for final files.

## 12. SET/SHOW essentials

```spss
SET UNICODE ON.      /* .sav in Unicode mode (default since v16). */
SHOW UNICODE.
SET LOCALE='en_US'.
SET MTINDEX=12345.   /* Mersenne Twister seed; reproducible Monte Carlo/bootstrap. */
SET SEED=12345.      /* Legacy uniform generator. */
SET MXLOOPS=1000.    /* Max LOOP iterations guard. */
```

Query state with `SHOW ALL.` / `SHOW <keyword>.` during debugging.

## 13. Minimal valid file + checklist

```spss
* demo-frequencies.sps : purpose, data, author, date.
SET UNICODE ON.
GET FILE='/data/demo.sav'.
FREQUENCIES VARIABLES=gender inccat
  /BARCHART PERCENT
  /ORDER=ANALYSIS.
OUTPUT EXPORT /CONTENTS EXPORT=VISIBLELAYERS /XLSX DOCUMENTFILE='/out/freq.xlsx'.
```

Before handing off, check:

1. Every command ends with `.` (except `BEGIN DATA`).
2. `END DATA` in column 1 if inline data present.
3. No line >256 chars; no blank line inside a command.
4. All variables spelled fully; strings quoted on one line.
5. `GET FILE` path uses forward slashes and exists.
6. One `EXECUTE.` after each transformation block that must materialise.
7. Ran `scripts/validate_sps.py` and fixed all ERROR lines.
