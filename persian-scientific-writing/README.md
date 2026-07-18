# Persian Scientific Writing

**Agent skill for rigorous academic Persian**

Write, rewrite, translate, structure, and edit scholarly Persian for theses, dissertations, journal and conference papers, research proposals, literature reviews, abstracts, and related academic sections — with discipline-appropriate terminology, orthography, and scholarly integrity.

---

## Why this skill

Academic Persian is not casual Persian with harder words, and it is not English research prose translated word-for-word. This skill gives coding agents a clear workflow for:

| Need | What the skill enforces |
| --- | --- |
| **Meaning over calque** | Idiomatic Persian structure instead of mirrored English syntax |
| **Scholarly integrity** | No invented sources, stats, methods, or findings |
| **Source audit** | Candidate claims and citation decisions mined from supplied files before prose |
| **Authorial originality** | Present-study voice and expert interpretation grounded only in supplied evidence |
| **Document craft** | Thesis, paper, proposal, and review structures that stay aligned |
| **Orthography** | No English prose, ASCII round parentheses or comma, or Arabic diacritics outside narrow protected cases |
| **Submission polish** | Multi-pass revision plus a final quality-control checklist |

Use it when the deliverable is in Persian, or when English academic material must become natural Persian academic prose. Do **not** use it for casual Persian or non-academic translation.

---

## Features

- **Task routing** — Loads only the reference material needed for structure, style, or final QC
- **Brief first** — Clarifies document type, discipline, purpose, length, and citation style before drafting
- **Claim–evidence–reasoning** — Paragraphs with a clear function, attributed evidence, and explicit interpretation
- **Full source mining** — Six-field candidate audits and a visible citation plan for attached files and labeled source blocks
- **Present-study voice** — `ما` for the authors' own supplied work and interpretation; third person for prior work
- **Strict Persian surface form** — Persian equivalents instead of floating English words, punctuation-safe prose, and no harakat
- **Translation as adaptation** — Rebuilds propositions in Persian while preserving stance, hedging, units, and citations
- **Revision passes** — Substance → structure → language → mechanics → final audit
- **Venue-aware defaults** — Institutional templates and journal guides override skill defaults when supplied

---

## Repository layout

```text
persian-scientific-writing/
├── SKILL.md                          # Entrypoint: routing, integrity, workflow, delivery
├── agents/
│   └── openai.yml                    # Codex / OpenAI agent display metadata
├── references/
│   ├── document-structures.md        # Thesis, paper, proposal, literature-review outlines
│   ├── originality-and-citations.md  # Source audit, authorial voice, English/diacritic constraints
│   ├── persian-style.md              # Register, orthography, RTL, terminology, citations
│   └── quality-control.md            # Submission-ready checklist
└── README.md
```

| File | Role |
| --- | --- |
| [`SKILL.md`](SKILL.md) | Agent instructions: when to load, how to brief, draft, revise, and deliver |
| [`references/document-structures.md`](references/document-structures.md) | Default section maps and problem→method→result alignment audit |
| [`references/originality-and-citations.md`](references/originality-and-citations.md) | Six-step source mining, citation choice, authorial voice, and language-constraint workflow |
| [`references/persian-style.md`](references/persian-style.md) | Formal Persian register, نیم‌فاصله, punctuation, numerals, terminology |
| [`references/quality-control.md`](references/quality-control.md) | Evidence, argument, language, citation, and handoff checks |
| [`agents/openai.yml`](agents/openai.yml) | UI name, short description, and default prompt for compatible agents |

---

## Install

### Codex CLI

Copy the skill into your Codex skills directory:

```bash
# Windows (PowerShell)
Copy-Item -Recurse .\persian-scientific-writing $env:USERPROFILE\.codex\skills\

# macOS / Linux
cp -R persian-scientific-writing ~/.codex/skills/
```

### Claude Code / other Agent Skills hosts

Install into the host’s skills path (examples):

```bash
# Claude Code (user skills)
cp -R persian-scientific-writing ~/.claude/skills/

# Generic agents skills directory
cp -R persian-scientific-writing ~/.agents/skills/
```

Restart or reload the agent so it picks up the new skill description.

> **Note:** Exact install paths depend on your agent runtime. The skill itself is plain Markdown + YAML and follows the common Agent Skills layout (`SKILL.md` + progressive references).

---

## When agents should load it

The frontmatter description is written for automatic skill selection. Typical triggers:

- Drafting or editing a **Persian thesis / dissertation section**
- Writing a **Persian journal or conference paper**
- Preparing a **Persian research proposal** or grant abstract
- Producing a **literature review** or **structured abstract** in Persian
- **Translating / adapting** English academic text into natural scientific Persian
- Fixing **نیم‌فاصله**, terminology drift, RTL citation issues, or consistency review

---

## Usage examples

### Draft a thesis section

```text
Use persian-scientific-writing to draft the methodology chapter of my Persian MSc thesis
in educational psychology. Design: mixed methods. I will paste notes on sample, instruments,
and analysis. Do not invent citations. Flag missing ethics details with placeholders.
```

### Adapt English into academic Persian

```text
Translate the following Results paragraph into rigorous academic Persian. Preserve all
p-values, CIs, sample sizes, and hedging. Prefer idiomatic Persian over literal English order.
```

### Style and QC pass

```text
Revise this Persian discussion for formal academic register, consistent terminology,
and نیم‌فاصله. Then run the quality-control checklist and list only issues that need my decision.
```

### Structure alignment

```text
Check whether my Persian proposal’s objectives, methods, and expected outcomes align.
Suggest structural fixes without inventing new evidence or results.
```

---

## Workflow (how the skill thinks)

```text
1. Select task        → structure / style / QC references
2. Establish brief    → type, audience, purpose, constraints
3. Mine sources       → six-field candidate audit from supplied context
4. Decide citations   → select support and assign exact citation spots
5. Protect integrity  → no fabricated evidence
6. Outline and write  → present-study voice + claim–evidence–reasoning
7. Verify constraints → no floating English, forbidden ASCII, or harakat
8. Revise and deliver → clean Persian prose + optional editorial notes
```

---

## Integrity principles

These are non-negotiable defaults built into the skill:

1. **Never invent** sources, quotations, data, statistics, methods, approvals, or findings  
2. **Preserve uncertainty** — limitations, negation, effect direction, units, and statistical meaning  
3. **Use placeholders** when evidence is absent; do not manufacture plausible citations  
4. **Cite only** user-supplied or properly verified sources  
5. **Language polish ≠ scientific validation** — editing does not endorse the analysis  
6. **Avoid patchwriting** — paraphrase with attribution, not disguised plagiarism  

---

## Document types covered

| Type | Guidance highlights |
| --- | --- |
| **Thesis / dissertation** | Preliminary matter → intro → literature → methods → results → discussion → conclusion |
| **Journal / conference paper** | Title, abstract, keywords, IMRaD-style body, required statements |
| **Research proposal** | Gap, aims, methods, feasibility, innovation; prospective language only |
| **Literature review** | Scope, synthesis (not one-paragraph-per-paper), gap that motivates the study |
| **Abstracts & sections** | Structured or unstructured; consistent with parent document aims |

All outlines are **defaults**. University templates, journal author guidelines, and funder forms take precedence.

---

## Persian style highlights

- Contemporary **formal** Persian — precise, readable, not ornate or bureaucratic  
- **نیم‌فاصله** in compounds and affixes (`می‌شود`, `داده‌ها`, `روش‌های`)  
- Persian punctuation in Persian prose: `،` `؛` `؟` and guillemets `«…»`  
- No ordinary English words inside Persian sentences; narrow carve-outs protect exact nomenclature and technical literals  
- No authored ASCII `(`, `,`, or `)`, and no Arabic harakat outside explicitly tagged Arabic quotations  
- First mention for an untranslatable term: `برابر فارسی «English term؛ ABBR»`; subsequent mentions use Persian only  
- Careful **RTL/LTR** handling for citations, years, equations, and Latin terms  
- Hedging calibrated to evidence: e.g. `نشان می‌دهد`, `می‌تواند`, `احتمالاً`

Full detail: [`references/persian-style.md`](references/persian-style.md)

---

## Compatibility

| Component | Support |
| --- | --- |
| OpenAI Codex skills | Yes (`agents/openai.yaml` included) |
| Claude Code / Agent Skills | Yes (`SKILL.md` frontmatter + progressive disclosure) |
| Other Markdown skill loaders | Yes, if they resolve relative `references/` links |

No runtime scripts, API keys, or native binaries required.

---

## Design notes

- **Progressive disclosure** — `SKILL.md` stays compact; detailed guidance lives in `references/` and loads only when needed  
- **Authoritative override** — user, supervisor, journal, or funder rules beat skill defaults  
- **Clean delivery** — primary output is polished Persian; editorial commentary is separated unless the user asks for inline notes  
- **Alignment audit** — problem → gap → purpose → method → result → conclusion stays coherent  

---

## Contributing

Improvements welcome, especially:

- Discipline-specific terminology notes (medicine, engineering, social sciences, etc.)
- Additional venue templates (common Iranian university formats, major Persian journals)
- Edge cases for bidirectional text, citation styles, and numeral conventions
- Clearer examples of good vs. calqued academic Persian

Please keep changes consistent with the integrity rules above and avoid bloating `SKILL.md` — prefer new or expanded files under `references/`.

---

## License

No license file is included yet. Add a `LICENSE` (for example MIT or Apache-2.0) before public release if you want others to reuse or fork the skill under clear terms.

---

## Author

Prepared as an agent skill for academic Persian writing workflows.  
Feedback and pull requests that strengthen scholarly accuracy and Persian naturalness are especially appreciated.
