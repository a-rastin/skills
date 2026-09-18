* python-integration.sps : dynamic descriptives via Python 3.10 plug-in.
* Data : /data/demo.sav   Requires : Integration Plug-in for Python. .
SET UNICODE ON.
GET FILE='/data/demo.sav'.
EXECUTE.
BEGIN PROGRAM PYTHON3.
import spss
names = [spss.GetVariableName(i) for i in range(spss.GetVariableCount())]
spss.Submit("DESCRIPTIVES VARIABLES=" + " ".join(names) + ".")
END PROGRAM.
