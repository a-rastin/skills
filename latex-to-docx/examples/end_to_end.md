# End-to-end example

From the skill directory:

```bash
python scripts/create_reference_docx.py \
  --output work/reference.docx \
  --persian-font "Noto Naskh Arabic" \
  --latin-font "Liberation Serif"

python scripts/convert_latex_to_docx.py \
  tests/fixtures/main.tex \
  --output work/result.docx \
  --reference-doc work/reference.docx \
  --strict \
  --workdir work/run
```

The orchestrator writes:

- `work/result.docx`
- `work/run/inventory.json`
- `work/run/fidelity-ledger.json`
- `work/run/validation-report.json`
- `work/run/conversion-report.md`
- `work/run/render/page-*.png`

For a real project, inspect `conversion-report.md`, every ledger entry, and every rendered page before delivery.
