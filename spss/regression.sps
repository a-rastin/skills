* regression.sps : binary logistic + diagnostics.
* Data : /data/bankloan.sav   Author :            Date : .
SET UNICODE ON.
SET MTINDEX=12345.
GET FILE='/data/bankloan.sav'.
LOGISTIC REGRESSION VARIABLES=default
  /METHOD=ENTER age employ address income debtinc creddebt othdebt
  /CONTRAST (gender)=Indicator(1)
  /PRINT=SUMMARY CI(95)
  /CRITERIA=PIN(.05) POUT(.10) ITERATE(20) CUT(.5)
  /SAVE=PRED PGROUP RESID
  /CLASSPLOT.
OUTPUT EXPORT /CONTENTS EXPORT=VISIBLELAYERS /PDF DOCUMENTFILE='/out/regression.pdf'.
