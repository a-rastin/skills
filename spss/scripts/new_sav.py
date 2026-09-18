#!/usr/bin/env python3
"""Create an SPSS .sav file from a CSV when SPSS is not installed.

Prefers pyreadstat (best .sav fidelity incl. labels); falls back to
pandas; fails with a clear message if neither is available.

Usage:
  python scripts/new_sav.py input.csv output.sav [--labels labels.json] [--encoding utf-8]

labels.json (optional):
  {
    "variable_labels": {"income": "Annual income (USD)"},
    "value_labels": {"gender": {1: "Male", 2: "Female"}},
    "missing": {"income": [999999]},
    "formats": {"income": "DOLLAR8.0"},
    "measure": {"gender": "nominal", "income": "scale"}
  }
"""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input_csv")
    ap.add_argument("output_sav")
    ap.add_argument("--labels", default=None)
    ap.add_argument("--encoding", default="utf-8")
    args = ap.parse_args()

    meta = {}
    if args.labels:
        with open(args.labels, encoding="utf-8") as f:
            meta = json.load(f)

    try:
        import pandas as pd
    except ImportError:
        print("ERROR: pandas is required (pip install pandas pyreadstat).", file=sys.stderr)
        return 2
    df = pd.read_csv(args.input_csv, encoding=args.encoding)

    var_labels = meta.get("variable_labels", {})
    val_labels = meta.get("value_labels", {})
    miss = meta.get("missing", {})
    formats = meta.get("formats", {})

    try:
        import pyreadstat

        var_format = {k: v for k, v in formats.items() if k in df.columns} or None
        missing_ranges = None  # keep simple: discrete missing via variable_value_labels path
        pyreadstat.write_sav(
            df,
            args.output_sav,
            column_labels=[var_labels.get(c, c) for c in df.columns],
            variable_value_labels={k: {int(kk): vv for kk, vv in v.items()} for k, v in val_labels.items()},
            variable_format={c: formats[c] for c in df.columns if c in formats} or None,
            missing_ranges=missing_ranges,
        )
        print(f"Wrote {args.output_sav} via pyreadstat ({len(df)} rows, {len(df.columns)} cols).")
        if miss:
            print("NOTE: discrete user-missing codes from labels.json were NOT embedded "
                  "(add MISSING VALUES in SPSS syntax); codes:", miss)
        return 0
    except ImportError:
        pass

    # Fallback: SPSS can import CSV directly — emit instructions + keep CSV.
    print("WARNING: pyreadstat not installed; cannot write binary .sav here.", file=sys.stderr)
    print("Install it (pip install pyreadstat) or import the CSV inside SPSS with:", file=sys.stderr)
    cols = ", ".join(f"{c} F8.0" if str(df[c].dtype) != "object" else f"{c} A64" for c in df.columns)
    print(f"GET DATA /TYPE=TXT /FILE='{args.input_csv}' /ENCODING='UTF8' "
          f"/ARRANGEMENT=DELIMITED /DELCASE=LINE /DELIMITERS=\",\" /QUALIFIER='\"' "
          f"/FIRSTCASE=2 /VARIABLES={cols}.\nCACHE.\nEXECUTE.", file=sys.stderr)
    return 3


if __name__ == "__main__":
    sys.exit(main())
