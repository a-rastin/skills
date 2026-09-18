* minimal-analysis.sps : frequencies + descriptives + export.
* Data : /data/demo.sav   Author :            Date : .
SET UNICODE ON.
GET FILE='/data/demo.sav'.
CODEBOOK ALL /VARINFO LABEL VALUELABELS MISSING /OPTIONS VARORDER=MEASURE.
FREQUENCIES VARIABLES=gender inccat
  /BARCHART PERCENT
  /ORDER=ANALYSIS.
DESCRIPTIVES VARIABLES=age income
  /STATISTICS=MEAN STDDEV MIN MAX.
OUTPUT EXPORT /CONTENTS EXPORT=VISIBLELAYERS /XLSX DOCUMENTFILE='/out/tables.xlsx'.
OUTPUT SAVE OUTFILE='/out/analysis.spv'.
