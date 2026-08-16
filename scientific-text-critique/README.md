# Scientific Text Critique

`scientific-text-critique` is a Codex skill for rigorous review of scientific and academic writing. It combines the perspectives of a scientific editor, biostatistician, epidemiologist, and study-design reviewer.

Use it with articles, manuscripts, theses, dissertations, protocols, abstracts, results sections, tables, figures, supplements, peer-review drafts, and analyses accompanied by raw data or code.

## What it reviews

- Internal contradictions across abstracts, methods, results, tables, figures, supplements, protocols, and registrations
- Study design, sampling, randomization, allocation concealment, blinding, confounding, bias, clustering, repeated measures, and causal identification
- Statistical test and model selection, assumptions, convergence, effect sizes, confidence intervals, p-values, power, sample size, missing data, and multiplicity
- Arithmetic identities and reproducibility of reported results
- Forensic-statistical signals, including GRIM, GRIMMER, DEBIT, duplicate or near-duplicate records, digit/heaping patterns, multivariate anomalies, randomization integrity, longitudinal consistency, and operational constraints
- Scientific writing, logic, terminology, causal overclaiming, reproducibility, reporting-guideline coverage, and citation integrity

## Evidentiary safeguards

The skill distinguishes among:

1. mathematically impossible or directly contradictory findings;
2. reproducible analytic discrepancies;
3. statistically improbable or anomalous patterns under a stated model;
4. unresolved concerns requiring source records or independent verification.

Statistical unusualness alone is never treated as proof of intentional fabrication. Plausible explanations such as rounding, transcription, coding errors, undocumented exclusions, missingness, transformations, and software behavior are considered explicitly.

The skill does not invent data, analytic choices, citations, or certainty.

## Usage

Invoke the skill explicitly in Codex:

```text
$scientific-text-critique Review the attached manuscript and prioritize issues that could change its conclusions.
```

More focused examples:

```text
$scientific-text-critique Recalculate every result supported by the reported summary statistics and identify irreproducible values.
```

```text
$scientific-text-critique Audit this thesis chapter for study-design flaws, inappropriate models, missing-data bias, multiplicity, and causal overclaiming.
```

```text
$scientific-text-critique Screen these tables and raw data for internal contradictions and forensic anomalies, clearly separating impossible findings from merely unusual ones.
```

Provide as much of the evidence package as possible: main text, tables, figures, supplements, protocol, registration, statistical analysis plan, data dictionary, raw data, analysis code, and software details. Missing materials are reported as limitations rather than inferred.

Codex can also invoke the skill implicitly when a request matches its description. See the [official OpenAI documentation for skills](https://learn.chatgpt.com/docs/build-skills).

## Review output

Unless another format is requested, the review contains:

- Executive assessment
- Scope and evidence limitations
- Study and claim map
- Structured findings table
- Numerical reconciliation and recalculations
- Cross-section consistency audit
- Forensic interpretation
- Prioritized correction plan

Each finding identifies its location, explains the problem, presents evidence or a recalculation, assigns severity and confidence, and proposes a precise correction or verification step.

### Severity

| Level | Meaning |
|---|---|
| Critical | May invalidate or reverse a central conclusion, creates a safety or ethics concern, or exposes a central impossibility. |
| Major | Materially threatens validity, reproducibility, or interpretation. |
| Moderate | Important but bounded weakness or unresolved uncertainty. |
| Minor | Local clarity, terminology, style, or low-impact reporting problem. |

### Confidence

| Level | Meaning |
|---|---|
| High | Direct contradiction, verified arithmetic, or reproduced discrepancy. |
| Medium | Strong inference with explicit assumptions and remaining alternatives. |
| Low | Plausible concern or screening signal requiring more evidence. |

Severity and confidence are assigned independently.

## Skill structure

```text
scientific-text-critique/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── references/
    ├── forensic-statistics.md
    ├── methods-and-design.md
    └── writing-and-reporting.md
```

- `SKILL.md` defines the core workflow, safeguards, issue taxonomy, and output format.
- `references/forensic-statistics.md` documents recalculation and anomaly-screening methods with applicability limits.
- `references/methods-and-design.md` covers design-specific and statistical-method review.
- `references/writing-and-reporting.md` covers scientific writing, transparency, guidelines, and citations.
- `agents/openai.yaml` supplies Codex display metadata and the default prompt.

## Limitations

The quality and certainty of a review depend on the materials provided. Manuscript-only checks cannot replace analysis of raw data, code, audit trails, or source records. The skill supports expert review but does not replace subject-matter consultation, formal peer review, research-integrity procedures, or legal and regulatory assessment.
