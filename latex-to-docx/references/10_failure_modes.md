# Failure modes and recovery

## Silent raw TeX loss

**Symptom:** content vanishes in DOCX while Pandoc exits successfully.

**Detection:** inspect Pandoc JSON for RawInline/RawBlock; reconcile text/object counts.

**Recovery:** targeted transform, isolated render fallback, or strict failure. Keep a visible placeholder only in draft mode.

## Persian characters appear disconnected, reversed, or punctuation moves

**Cause:** manual reshaping/reversal, missing `w:bidi`/`w:rtl`, wrong run segmentation, or font fallback.

**Recovery:** restore logical Unicode source order; patch paragraph/run direction and language; segment mixed spans; choose an installed complex-script font; re-render.

## ZWNJ disappears

**Cause:** destructive normalization, editor replacement, or text extraction/rebuild.

**Recovery:** use NFC, preserve U+200C, compare source/output code points, add regression fixture.

## RTL table columns are reversed incorrectly

**Cause:** misunderstanding XML logical order versus `w:bidiVisual` display order.

**Recovery:** retain a logical grid model; apply `bidiVisual` once; validate first/last columns visually and structurally.

## Equations become images or plain text

**Cause:** unsupported macros or wrong Pandoc input parsing.

**Recovery:** expand macros to standard TeX, verify Math AST nodes, use OMML, and only then use an isolated image fallback.

## Table exceeds margins

**Recovery order:** optimize widths, wrap text, use landscape section, reduce spacing/font within contract, split semantically, then consider an image only if editability is not required.

## TikZ/PGF figure has missing Persian labels

**Cause:** compiled with a different engine/preamble/font or converted through a tool that drops fonts.

**Recovery:** compile standalone with original XeLaTeX/LuaLaTeX settings; crop; convert to SVG/PNG; inspect labels.

## Fields show stale or blank values

**Cause:** headless renderer did not update Word fields.

**Recovery:** set update-on-open, retain cached results, optionally materialize values in a QA copy, and verify in target Microsoft Word when live fields are contractual.

## Citations differ from LaTeX

**Cause:** CSL and BibLaTeX style are not equivalent.

**Recovery:** use verified CSL, reconstruct formatted output, or disclose the style deviation and ask for the preferred fidelity axis.

## LibreOffice render differs from Word

**Cause:** renderer-specific font, field, SVG, anchor, or layout behavior.

**Recovery:** target the user's primary application; use LibreOffice as a QA signal, not sole authority; prefer inline graphics and standard Word features; verify in Microsoft Word when required.

## Compile succeeds only with shell escape

**Recovery:** isolate the source in a controlled work directory, audit commands/packages, enable shell escape only when required, and record it. Never run untrusted arbitrary shell commands from TeX without a sandbox/security decision.

## Corrupted DOCX after XML patch

**Cause:** broken namespace, relationship, content-type, or ZIP rewrite.

**Recovery:** parse every XML part, validate relationships, preserve untouched parts, write atomically, and test patch idempotency.
