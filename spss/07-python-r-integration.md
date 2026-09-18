# 07 — Python and R Integration

Source docs: `Python_Reference_Guide_for_IBM_SPSS_Statistics`, `R_Integration_Package_for_IBM_SPSS_Statistics`, SAS-Data-Management Guide Ch. 3–5.

Bundled runtime: Python 3.10 on all OSes (`Python 3.10 for IBM SPSS Statistics 31` + IDLE). R via `Integration Plug-in for R` (Windows/Linux/macOS/Server; external IDEs supported since v23).

## Table of contents

1. BEGIN PROGRAM blocks (rules for both languages)
2. Python: spss module essentials
3. Python: cursors, datasets, pivot tables, OMS/XPath
4. Python: external process + extension commands
5. R: spssdata / spssdictionary / spsspkg essentials
6. R: graphics, OMS, external process
7. Path/encoding pitfalls
8. Snippets

---

## 1. BEGIN PROGRAM blocks

```spss
BEGIN PROGRAM PYTHON3.
import spss
spss.Submit("FREQUENCIES VARIABLES=var1 var2 var3.")
END PROGRAM.

BEGIN PROGRAM R.
File1N <- spssdata.GetCaseCount()
print(File1N)
END PROGRAM.
```

- First Python block in a session must `import spss`; later blocks may omit it. Inside SPSS, `BEGIN PROGRAM R` auto-loads the right plug-in — no `library()` needed.
- Only host-language statements inside the block. SPSS commands must be strings passed to `Submit`.
- Nesting: a block may `Submit("INSERT FILE='/x/nested.sps'.")` where the nested file holds its own `BEGIN PROGRAM`; triple-quoted strings avoid quoting hell; ~5 nesting levels.
- Paths: SPSS-relative paths resolve from the backend dir, Python/R I/O from their own cwd — **always use absolute paths with forward slashes**: `spss.Submit("GET FILE '/data/demo.sav'.")`, `scan(file="/Rdata.txt")`. Escape Windows backslashes or avoid them.
- Unicode: honour `SET UNICODE`; check `spss.PyInvokeSpss.IsUTF8mode()` / `spsspkg.IsUTF8mode()`; truncate with `spssaux.truncatestring` when writing labels.

## 2. Python: spss module essentials

| Call | Purpose |
|------|---------|
| `spss.Submit("...")` | Run SPSS syntax (dynamic generation, `%(name)s` interpolation) |
| `spss.GetVariableCount/Name/Type/Label/Format/MeasurementLevel/Role/MissingValues/Attributes` | Dictionary reads |
| `spss.GetCaseCount()` | N cases (honours FILTER/USE) |
| `spss.ActiveDataset/SetActive/GetDatasets` | Multi-dataset control |
| `spss.SetMacroValue` | Feed Python values into `!macros` |
| `spss.SetOutput/IsOutputOn/SetOutputLanguage` | Output control |
| `spss.GetSPSSLocale/Setting/WeightVar/SplitVariableNames` | Session state |
| `spss.CreateXPathDictionary/EvaluateXPath/DeleteXPathHandle/GetHandleList/GetFileHandles/GetImage` | OMS/XML workspace reads |
| `spss.StartSPSS/StopSPSS` | External-process mode only |

## 3. Python: data access + output building

```python
# Read all cases.
cur = spss.Cursor()
data = cur.fetchall()
cur.close()

# Create variables then rows.
cur = spss.Cursor(accessType='w')
cur.SetVarNameAndType(['var4', 'strvar'], [0, 8])
cur.SetVarFormat('var4', 5, 2, 0)
cur.CommitDictionary()
# ... SetValueNumeric / SetValueChar + CommitCase per row ...
cur.EndChanges()   # or cur.close()

# Dataset API (higher level than Cursor).
import spss
ds = spss.Dataset(name=None)
# ds.varlist / ds.cases / ds.CaseList.append(...) / deepCopy / close
# After EndDataStep: DATASET ACTIVATE + SAVE OUTFILE via Submit.

# Custom pivot table inside a StartProcedure block.
spss.StartProcedure('MyProc')
tbl = spss.BasePivotTable('Title', 'OMSid')
tbl.Append(...)  # / Insert / SetCategories / SetCell / SetCellsByRow...
spss.EndProcedure()

# Dynamic save per group value.
spss.Submit(r"""
DATASET ACTIVATE %(name)s.
SAVE OUTFILE='/mydata/saldata_%(strdept)s.sav'.
""" % locals())
```

Cursors auto-close at `END PROGRAM` and do not persist across blocks. `SpssClient`/`SpssDataDoc` (Ch. 3 Scripting Guide) automate Viewer/syntax docs externally. Localise custom-procedure strings via `pot/mo` files.

## 4. Python: external process + extensions

```python
# External CPython driving SPSS (needs sitecustomize.py under PYTHON_HOME).
import spss
spss.StartSPSS()
spss.Submit("GET FILE '/data/demo.sav'. FREQUENCIES VARIABLES=gender.")
spss.StopSPSS()
```

- Multi-version installs: `SpssClient.pth`, `GetDefaultPlugInVersion/SetDefaultPlugInVersion/ShowInstalledPlugInVersions`.
- Extension commands (`STATS PSM`, `SPSSINC TRANS`, `SPSSINC MODIFY TABLES`, ...) are Python programs exposed as SPSS commands — install via Extensions Hub, invoke as normal commands, read their help with `STATS <NAME> /HELP`.

## 5. R essentials

Packages auto-available inside `BEGIN PROGRAM R`: `spssdata`, `spssdictionary`, `spsspkg`, `spssRGraphics`, `spsspivottable`, `spssxmlworkspace`.

```r
casedata <- spssdata.GetDataFromSPSS(variables=c("age","income","employ"))
casedata <- spssdata.GetDataFromSPSS(factorMode="labels")   # value labels as factors
casedata <- spssdata.GetDataFromSPSS(rDate="POSIXct")       # SPSS dates -> POSIXct
n <- spssdata.GetCaseCount()
dict <- spssdictionary.GetDictionaryFromSPSS()

# Write a new dataset, then save.
spssdictionary.SetDictionaryToSPSS("results", dict)
spssdata.SetDataToSPSS("results", casedata)
spssdictionary.SetActive("results")
spssdictionary.EndDataStep()
spsspkg.Submit("SAVE OUTFILE = '/data/results.sav'.")

# Pivot output.
spsspivottable.Display(obj, title="My table")
spsspkg.StartProcedure("MyProc"); spsspkg.EndProcedure()
```

Key reads: `GetDictionaryFromSPSS/GetCategoricalDictionaryFromSPSS`, `GetVariableCount/Name/Type/Label/Format/MeasurementLevel`, `GetValueLabels/GetUserMissingValues`, `GetDataSetList/GetOpenedDataSetList`, `GetSplitDataFromSPSS/GetSplitVariableNames/IsLastSplit`, `SetVariableAttributes/EditCategoricalDictionary/SetValueLabel/SetUserMissing`. Session: `GetSPSSVersion/GetSPSSPlugInVersion/GetStatisticsPath/GetSPSSLocale/IsBackendReady/IsDistributedMode/IsUTF8mode/IsXDriven`, `SetOutput/SetStatisticsOutput/SetOutputLanguage`.

Caveats: `GetDataFromSPSS` honours `FILTER/USE`, returns only the first split group when split, skips weighting; args `cases/row.label/keepUserMissing/missingValueToNA/factorMode/rDate`. Dates: R `POSIXct`, SPSS time = seconds from midnight. Write path is always dictionary-first, data-second. R vars are global except inside functions.

## 6. R graphics, OMS, external process

```r
# Show an R graphic in SPSS output.
spssRGraphics.Submit("/temp/R_graphic.jpg")

# Harvest output XML.
h <- spssxmlworkspace.CreateXPathDictionary(...)
spssxmlworkspace.EvaluateXPath(h, "//pivotTable")
spssxmlworkspace.DeleteXmlWorkspaceObject(h)
```

```r
# External R IDE driving SPSS (no BEGIN PROGRAM needed).
library(spssstatistics)
spsspkg.StartStatistics()
spsspkg.Submit(c("GET FILE '/data/employee data.sav'.", "FREQUENCIES VARIABLES=gender jobcat."))
spsspkg.StopStatistics()
```

`FILE HANDLE` names are visible via `spssdata.GetFileHandles()` / `spssdictionary.GetFileHandles()`.

## 7. Pitfalls (both languages)

1. Absolute forward-slash paths everywhere.
2. Flush pending transforms with `EXECUTE.` before a program block reads cases.
3. `DATASET ACTIVATE` the right dataset before reads/writes.
4. Close/commit (`EndChanges/EndDataStep/close`) before `SAVE OUTFILE`.
5. Reproducibility: `SET MTINDEX=` (Mersenne Twister) for bootstrap/Monte-Carlo/R sampling.
6. Do not persist Cursor/Dataset objects across `END PROGRAM`.

## 8. Snippet: dynamic syntax from Python

```spss
BEGIN PROGRAM PYTHON3.
import spss
string1 = "DESCRIPTIVES VARIABLES="
N = spss.GetVariableCount()
names = [spss.GetVariableName(i) for i in range(N)]
spss.Submit(string1 + " ".join(names) + ".")
END PROGRAM.
```
