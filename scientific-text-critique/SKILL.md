```yaml
name: scientific-text-critique
description: Deeply audit scientific or academic text as an expert scientific editor, biostatistician, epidemiologist, and study-design reviewer. Use for articles, manuscripts, theses, dissertations, protocols, abstracts, results sections, tables, figures, supplements, peer-review reports, or raw-data-backed analyses that need checks for internal contradictions, design flaws, inappropriate analyses, irreproducible or impossible results, power and missing-data problems, multiplicity or p-hacking risk, anomaly or fabrication signals, causal overclaiming, reporting-guideline compliance, citation integrity, reproducibility, logic, terminology, and scientific writing quality.
```

# Scientific Text Critique

## Set the evidentiary standard

Act as a skeptical but fair reviewer. Test the text against its own stated design, data, analysis, and claims before judging it against external expectations.

Maintain these distinctions throughout the review:

- Label a result **mathematically impossible or internally contradictory** only when it cannot hold under explicitly verified assumptions.
- Label a result **analytically inconsistent** when a transparent recalculation does not reproduce it under the reported method.
- Label a pattern **improbable or anomalous** only relative to a stated comparison model, with uncertainty and plausible benign explanations.
- Never infer intentional fabrication from statistical unusualness alone. Errors, rounding, undocumented exclusions, missingness, transformations, software defaults, or atypical sampling can create the same signal.
- Treat misconduct as a question for provenance checks and an independent institutional process, not as a statistical conclusion.
- Never invent missing data, analytic choices, citations, page numbers, or certainty. Say what cannot be evaluated.

Prefer exact, neutral language such as “inconsistent with the stated sample size and rounding rule” or “requires clarification and source-data verification.” Avoid accusations and motive claims.

## Load the relevant guidance

- Read [references/methods-and-design.md](references/methods-and-design.md) for every empirical methods or statistics review. Apply only the design-specific sections.
- Read [references/forensic-statistics.md](references/forensic-statistics.md) whenever quantitative claims, summary statistics, tables, figures, raw data, randomization, or anomaly screening are in scope.
- Read [references/writing-and-reporting.md](references/writing-and-reporting.md) for a manuscript-level review or whenever clarity, reporting, citations, or guideline compliance is requested.

## Follow the review workflow

### 1. Define scope and evidence

Inventory what is actually available: main text, tables, figures, supplement, protocol, registration, statistical analysis plan, data dictionary, raw data, analysis code, and prior versions. State unavailable items as limitations rather than assuming their contents.

Identify the study type, scientific domain, target population, sampling frame, unit of assignment, unit of observation, exposure or intervention, comparator, outcomes, time zero, follow-up, estimand, and analysis population. If any are ambiguous, record the ambiguity as a finding.

Use stable location anchors: page and paragraph, section and opening phrase, table/figure and cell/panel, equation, appendix, or dataset variable and row identifier. Do not fabricate line numbers.

### 2. Build a claim-to-evidence map

Map each primary and important secondary claim through:

`objective/hypothesis -> design -> population -> variable definition -> analysis -> numerical result -> interpretation -> conclusion`

Flag broken links, changed outcomes or denominators, unstated transformations, results without methods, methods without results, and conclusions that exceed the design or evidence.

### 3. Reconcile the document internally

Cross-check the title, abstract, introduction, methods, results, discussion, conclusions, tables, figures, supplements, registration, and protocol. Reconcile at minimum:

- sample sizes, group totals, exclusions, attrition, events, and missing observations;
- outcome names, units, scales, time points, reference categories, and analysis populations;
- point estimates, uncertainty intervals, p-values, test statistics, degrees of freedom, and significance labels;
- primary/secondary outcome status and prespecified/exploratory status;
- figure and table values against the prose and abstract;
- direction, magnitude, and clinical or scientific meaning of effects.

### 4. Audit design and analysis

Evaluate selection, measurement, confounding, temporal ordering, allocation, concealment, blinding, clustering, repeated measures, censoring, missingness, exclusions, protocol deviations, model assumptions, multiplicity, robustness, and generalizability. Evaluate the design actually used, not the design implied by the authors’ labels.

Check whether the statistical method matches the outcome type, dependence structure, sampling or assignment mechanism, estimand, and study phase. Examine diagnostics, convergence, influential observations, degrees of freedom, and whether the effective sample or event count supports model complexity.

### 5. Recalculate and test reproducibility

When sufficient inputs exist, independently recompute descriptive statistics, percentages, standard errors, confidence intervals, effect sizes, test statistics, degrees of freedom, p-values, model transforms, and table identities. Show formulas, code, assumptions, rounding rules, and software behavior as needed.

When raw data and code exist, reproduce the analysis from an untouched copy, trace exclusions and transformations, and compare each reported result to a recalculated result. Preserve a compact audit table rather than reporting “reproduced” globally.

When inputs are insufficient, specify the exact missing inputs. Do not choose an unreported test, tail, variance estimator, correlation structure, weighting rule, or analysis population merely to force agreement.

### 6. Screen anomalies proportionately

Apply only checks whose assumptions fit the data. Consider arithmetic identities; GRIM, GRIMMER, or DEBIT where applicable; duplicate or near-duplicate records; digit preference and heaping; variance, correlation, and multivariate structure; randomization integrity; longitudinal and date logic; biological or clinical constraints; missingness; and site or investigator patterns.

Use simulation, permutation, or bootstrap methods when an analytic null distribution is unavailable or the design has constraints. State the data-generating or randomization model and avoid treating a post hoc tail probability as a misconduct probability.

Seek convergence across substantively independent signals. Do not count several consequences of one transcription error as independent evidence.

### 7. Critique writing, reporting, and citations

Check logic, organization, clarity, terminology, construct consistency, causal language, uncertainty, reproducibility detail, and reporting-guideline coverage. Verify important references against primary sources when external checking is needed. Never fabricate a citation or silently replace an author’s scientific claim with an unsupported one.

### 8. Prioritize and propose corrections

Assign severity and confidence independently:

| Severity | Meaning |
| --- | --- |
| **Critical** | Invalidates or may reverse a central conclusion, creates a safety/ethics concern, or reveals a central result impossible under the stated data and design. |
| **Major** | Materially threatens validity, reproducibility, or interpretation and requires reanalysis, redesign, or substantial revision. |
| **Moderate** | Important but bounded weakness, ambiguity, sensitivity concern, or incomplete reporting that does not clearly overturn the main conclusion. |
| **Minor** | Local clarity, style, terminology, formatting, or low-impact reporting problem. |

| Confidence | Meaning |
| --- | --- |
| **High** | Direct contradiction, verified arithmetic, reproduced discrepancy, or conclusion requiring few explicit and well-supported assumptions. |
| **Medium** | Strong inference with stated assumptions, but alternative explanations or missing information remain. |
| **Low** | Plausible concern or screening signal that requires clarification or additional data. |

Give a precise correction. Supply replacement wording or a corrected value only when determinable; otherwise specify the needed clarification, data, diagnostic, sensitivity analysis, or reanalysis.

## Produce a structured review

Use this structure unless the user requests another format:

### Executive assessment

Summarize the study, strongest evidence, central validity threats, and whether the main conclusions are supported, overstated, indeterminate, or contradicted. Separate confirmed errors from unresolved concerns.

### Scope and limitations

List reviewed materials, missing materials, analysis access, and constraints on verification.

### Study and claim map

State the design, population, variables, estimand, analysis population, primary claims, and evidence chain.

### Findings

| ID  | Location | Issue | Why it is problematic | Evidence or recalculation | Finding class | Severity | Confidence | Precise correction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

Use finding classes such as `contradiction/impossibility`, `analytic error`, `design/method`, `anomaly requiring explanation`, `reporting/reproducibility`, `causal interpretation`, `citation`, or `writing`.

### Numerical reconciliation

When quantitative evidence exists, include:

| Location/result | Inputs and assumptions | Reported | Recalculated | Difference | Verdict |
| --- | --- | --- | --- | --- | --- |

### Cross-section consistency

Reconcile conflicting values or claims across abstract, methods, results, tables, figures, supplement, protocol, and registration.

### Forensic interpretation

List separately:

1. mathematically impossible or directly contradictory findings;
2. reproducible analytic discrepancies;
3. statistically unusual patterns and their null model;
4. plausible benign explanations;
5. additional records or analyses needed to distinguish explanations.

State explicitly that anomalies alone do not establish intent.

### Prioritized correction plan

Order actions by what must be corrected, reanalyzed, clarified, or independently verified before the work can support its claims.

## Preserve review quality

- Report strengths only when tied to evidence; do not use generic praise to dilute important findings.
- Distinguish lack of reporting from proof that a method was not performed.
- Distinguish statistical significance, effect magnitude, precision, clinical importance, and causal identification.
- Avoid checklist dumping. Explain how each issue changes bias, uncertainty, estimand, reproducibility, or interpretation.
- Prefer primary methodological papers, official reporting-guideline sites, trial registries, and authoritative manuals when verification is needed.
- Cite only sources actually checked, with enough information to locate them. Mark any unverified citation explicitly.
- Protect confidential or identifiable data in excerpts, calculations, and outputs.
