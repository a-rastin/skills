* data-definition.sps : dictionary for a new data file.
* Data : (inline example)   Author :            Date : .
DATA LIST FREE / id (F8.0) gender (A8) age (F8.0) income (F8.0).
BEGIN DATA
1 male 34 52000
2 female 41 61000
END DATA.
EXECUTE.
VARIABLE LABELS id 'Respondent ID' gender 'Gender' age 'Age in years'
  income 'Annual household income (USD)'.
VALUE LABELS gender 'm' 'Male' 'f' 'Female' / age 999 'Unknown'.
MISSING VALUES age (999).
FORMATS income (DOLLAR8.0).
VARIABLE LEVEL age income (SCALE) gender (NOMINAL).
CODEBOOK ALL /VARINFO LABEL VALUELABELS MISSING.
SAVE OUTFILE='/out/new.sav' /COMPRESSED.
