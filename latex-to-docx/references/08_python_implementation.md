# Python implementation plan

The supplied scripts are a reference implementation. Extend them through typed, testable components rather than accumulating regex replacements in one file.

## Module architecture

```text
Config
  paths, strictness, languages, fonts, engine, template, target app
SourceGraph
  files, include edges, assets, build metadata, hashes
Inventory
  constructs, counts, custom macros/environments, Persian signals
Ledger
  per-construct representation, transformation, validation, status
CommandRunner
  subprocess execution, timeout, logs, versions, environment
Flattener
  include resolution, source map, verbatim-safe normalization
AstAnalyzer
  Pandoc JSON traversal, raw-node diagnostics, object counts
AssetConverter
  PDF/EPS/TikZ/PGF -> SVG/PNG with provenance
DocxPostprocessor
  idempotent OOXML patches
Validator
  package/XML/relationship/content/RTL/count/render checks
ReportWriter
  deterministic Markdown/JSON summaries and hashes
```

Use `dataclasses` or Pydantic-like validation without requiring a heavy runtime dependency. Store paths as `pathlib.Path` and serialize as POSIX relative paths where possible.

## Subprocess discipline

- Pass an argument list, never a shell command string.
- Set `cwd` explicitly to the source/project directory.
- Capture stdout/stderr to log files and include the command in the report.
- Use finite timeouts and terminate the process tree on timeout.
- Set deterministic locale/environment (`LC_ALL=C.UTF-8`, `LANG=C.UTF-8`) while preserving TeX-required variables.
- Check return codes and required output files.
- Record executable path and version.
- Treat warnings that imply lost content as ledger entries or errors.

## File safety

- Copy or hash inputs before transformation.
- Resolve paths and reject output paths inside immutable source copies.
- Use `tempfile.TemporaryDirectory` or a dedicated work directory.
- Write JSON/XML/DOCX to a temporary sibling and atomically replace the destination after validation.
- Sort traversal and JSON keys.
- Use SHA-256 for provenance.

## Parsing strategy

Regex is acceptable for dependency discovery only when combined with lexical protections:

1. strip comments while respecting escaped `%`;
2. mask verbatim-like environments and inline verb commands;
3. parse balanced braces for command arguments;
4. retain line numbers and source spans;
5. use Pandoc AST for semantic body parsing;
6. treat custom TeX expansion as a targeted rule with tests.

Do not attempt to implement TeX macro expansion generally in Python. TeX is a programming language; use the original engine for visual reference and isolate known semantic transforms.

## AST handling

Walk Pandoc JSON recursively and collect:

- node type counts;
- headers/identifiers;
- images and captions;
- tables and spans;
- math nodes;
- citations;
- notes;
- RawInline/RawBlock payloads.

A transform rule must declare:

```python
@dataclass(frozen=True)
class TransformRule:
    name: str
    source_pattern: str
    target_semantics: str
    version: str
    fixture: str
```

Each rule emits a ledger entry. Unknown raw TeX fails strict mode.

## OOXML handling

A DOCX is an OPC ZIP package. Use `zipfile` and `lxml` for features not exposed by `python-docx`. Preserve compression, relationships, content types, and unrelated XML. Register namespaces and use qualified names. Patch all relevant story parts.

Idempotency test: extract XML before and after a second patch; semantic elements/counts must remain unchanged.

## Error classes

Use specific exceptions:

```python
class ConversionError(RuntimeError): ...
class SourceGraphError(ConversionError): ...
class BaselineCompileError(ConversionError): ...
class PandocError(ConversionError): ...
class UnsupportedConstructError(ConversionError): ...
class DocxIntegrityError(ConversionError): ...
class ValidationError(ConversionError): ...
```

Include a remediation message and source location. Strict mode raises; draft mode writes a visible placeholder and ledger warning.

## Logging and reporting

Use structured events with severity, stage, source location, command, and artifact. The final report should include:

- contract decisions and their origin (user/inferred);
- source graph summary;
- tool versions;
- conversion commands;
- object count reconciliation;
- ledger status totals;
- validation results;
- known deviations;
- hashes of delivered files.

## Tests

At minimum include fixtures for:

- Persian paragraph with ZWNJ and mixed English/URL;
- nested `\input`;
- inline/display math;
- RTL table and merged cells;
- figure/caption/label;
- citation and bibliography;
- unknown raw command in strict mode;
- header/footer and footnote RTL;
- idempotent postprocessing;
- broken media relationship detection.

Run unit tests on source parsing and OOXML patches, then an end-to-end smoke test when Pandoc/LibreOffice/TeX are present.
