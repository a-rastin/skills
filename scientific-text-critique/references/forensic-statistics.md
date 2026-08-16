# Forensic statistics and reproducibility checks

## Contents

1. Evidence hierarchy
2. Recalculation sequence
3. Arithmetic and distributional identities
4. GRIM, GRIMMER, and DEBIT
5. Duplicate and near-duplicate patterns
6. Digits, rounding, and heaping
7. Variance, correlation, and multivariate structure
8. Randomization and allocation integrity
9. Longitudinal, biological, and operational constraints
10. Missingness, dates, sites, and investigators
11. Monte Carlo, permutation, and bootstrap checks
12. Convergence and escalation

## 1. Use an evidence hierarchy

Classify a signal before interpreting it:

1. **Exact contradiction:** No values can satisfy the reported quantities under verified definitions, denominators, and rounding rules.
2. **Reproducible discrepancy:** Available data or sufficient summaries produce a different result under the reported method.
3. **Model-dependent anomaly:** A pattern is unusual under a stated stochastic, biological, operational, or randomization model.
4. **Provenance concern:** Source records, audit trails, timestamps, authorship, or chain of custody require independent verification.

Do not turn levels 2–4 into an accusation. An exact numerical contradiction establishes an error in the set of claims, not its cause or intent.

## 2. Follow the recalculation sequence

Prefer the highest available evidence tier:

1. Raw data, data dictionary, protocol, code, and software environment.
2. Raw data without original code.
3. Sufficient cell counts or summary statistics.
4. Rounded manuscript values only.

For every recalculation:

- record the source location, analysis population, numerator, denominator, missing count, grouping, weights, units, and rounding precision;
- identify whether SD means sample SD or population SD and whether uncertainty is SD, SE, CI, IQR, or something else;
- reproduce the stated test before trying alternative tests;
- use exact or higher-precision inputs when available;
- distinguish a discrepancy caused only by plausible display rounding;
- retain code, package versions, random seeds, warnings, and convergence messages for consequential checks.

Create one row per result with reported value, recalculated value, absolute and relative difference, assumptions, and verdict.

## 3. Check arithmetic and distributional identities

### Counts, percentages, and flow

- Verify `percentage = count / denominator × 100` within stated rounding.
- Reconcile group totals, subtotals, mutually exclusive categories, event counts, exclusions, analyzed observations, and missing observations.
- Track changing denominators by outcome and time point. A percentage may be arithmetically correct but misleading if its denominator changes silently.
- Check contingency-table margins against prose, models, figures, and participant-flow diagrams.

### Means and variances

- Check weighted subgroup means against the overall mean when groups are exhaustive and weights are counts.
- Use within/between-group variance decomposition only when group definitions and variance conventions match.
- Verify `SE = SD / sqrt(n)` only for an unweighted simple mean of independent observations. Replace `n` with the appropriate effective information or model-based variance for clustered, weighted, repeated, or complex samples.
- Check bounds: a mean must lie within the possible range; variance cannot be negative; SD cannot exceed distribution-specific bounds.
- For bounded data on `[a,b]`, use bounds such as `Var(X) <= (b-a)^2/4` as screens, accounting for finite-sample conventions and reported rounding.

### Estimates, tests, confidence intervals, and p-values

- Reconstruct `test statistic = estimate / SE` only when the null value is zero and the reported model uses that Wald statistic.
- For ratios, work on the log scale when the method is log-Wald: `SE(log ratio)` and `exp(log ratio ± critical value × SE)`.
- Check whether a two-sided confidence interval at level `1-alpha` excludes the null exactly when the corresponding two-sided test is significant at `alpha`, allowing for method differences and rounding.
- Verify test-specific degrees of freedom, tail, continuity or small-sample correction, variance estimator, and model family.
- Do not recompute a paired test from marginal SDs without the within-pair covariance. Do not force an independent equal-variance t test when Welch, paired, clustered, or adjusted analysis was reported.
- Recompute categorical, rank-based, likelihood, score, Wald, exact, survival, and regression results from sufficient inputs only. State when summaries are insufficient.

### Regression and survival identities

- Verify transformations such as `OR = exp(beta)` and transformed confidence limits.
- Check reference categories, contrast direction, coefficient signs, and whether prose reverses the comparison.
- Confirm that predicted probabilities and survival estimates stay within admissible ranges.
- Check that Kaplan–Meier survival is nonincreasing, numbers at risk are nonincreasing except for explicitly described staggered entry, events do not exceed persons at risk, and time origins match.
- Reconcile model sample size and event count with exclusions and missingness.

### Correlations and matrices

- Require correlations to lie in `[-1,1]` and covariance/variance terms to use compatible units.
- Check that a reported correlation or covariance matrix is symmetric and positive semidefinite within plausible rounding tolerance.
- Treat a small negative eigenvalue from rounded entries differently from a materially impossible matrix; perform sensitivity to allowed rounding intervals.

## 4. Apply granular-data checks only when eligible

### GRIM

Use GRIM to test whether a rounded mean can arise from the stated number of integer-valued observations. Establish first:

- the values being averaged are integers or a known sum/average of a fixed number of integer items;
- the effective denominator after missingness is known;
- there are no unreported weights, transformations, imputations, or adjusted/model-based means;
- the display precision and rounding convention are known or sensitively varied.

Enumerate possible integer sums divided by the effective denominator (and item count where the scale construction requires it), then determine whether any possible value rounds to the report. Label failure “GRIM-inconsistent under these assumptions,” not fabricated. GRIM loses discriminating value as the denominator grows and the attainable grid becomes fine.

### GRIMMER

Use GRIMMER or an equivalent exhaustive enumeration to test whether a reported mean and SD can jointly arise from granular integer data. Verify GRIM eligibility first. Specify:

- scale minimum and maximum;
- sample size and any item aggregation;
- sample versus population SD convention;
- mean and SD rounding intervals;
- missingness, weighting, and transformations.

Prefer a validated implementation or enumerate feasible integer configurations/sum-of-squares. Do not apply a simplified pattern outside its documented domain. Report computational limits and alternative feasible configurations. A mismatch is an internal consistency error under the tested assumptions, not evidence of intent.

### DEBIT

Use DEBIT only for genuinely binary `0/1` individual-level data when mean, sample SD, and sample size refer to the same observations. For an exact binary sample mean `m` and sample size `n`, the sample SD is determined by:

`s = sqrt((n/(n-1)) * m * (1-m))`

Test all exact counts and values compatible with the reported rounding intervals rather than treating displayed decimals as exact. Exclude or separately model weighted, clustered/group-level, adjusted, imputed, transformed, or non-`0/1` encodings. A mismatch can result from a wrong mean, SD, denominator, coding, rounding, or missingness.

## 5. Examine duplicates and near-duplicates

With raw data, check exact duplicate rows, repeated IDs, repeated blocks, identical multivariable profiles, copied trajectories, implausibly small distances, and duplicated free text. Use keys that exclude expected constants and metadata.

Before flagging:

- distinguish repeated measurements, twins/households, matched sets, batch controls, legitimate resampling, defaults, detection limits, and common categorical profiles;
- estimate the expected collision rate under the variable distributions and precision;
- compare within and across site, investigator, group, time, and entry order;
- inspect whether duplication includes fields that should change, such as timestamps or repeated laboratory values.

For near-duplicates, define distance, scaling, allowed missingness, and threshold before interpreting. Inspect candidate pairs manually and report false-positive risks.

For images or figures, use specialized image-forensics methods and original files; visual similarity in a rendered PDF alone is a screening signal.

## 6. Treat digit and heaping analyses cautiously

Inspect terminal digits, repeated decimal patterns, rounding to preferred values, heaping at clinical thresholds, and precision inconsistent with the instrument. Compare patterns across groups, sites, investigators, devices, and time periods only when the recording process should be comparable.

Account for:

- instrument resolution and software rounding;
- bounded or discrete variables;
- derived statistics rather than raw measurements;
- clinical protocols and threshold-triggered actions;
- dependence among observations and repeated measures;
- multiple testing and post hoc choice of digit test.

Do not assume uniform terminal digits without a measurement model. Do not apply Benford’s law to assigned numbers, small or truncated ranges, bounded scales, rounded measurements, or derived means/SDs merely because it is available. Digit anomalies are weak, model-dependent evidence unless independently validated for the exact data-generating process.

## 7. Evaluate variance, correlation, and multivariate structure

Possible screens include:

- variances implausibly equal or unequal across randomized groups, sites, waves, or variables;
- means, SDs, correlations, or effect sizes repeated beyond expected rounding collisions;
- correlations incompatible with scale reliability or with other reported correlations;
- covariance matrices that are not positive semidefinite;
- implausibly weak or strong within-person, within-site, or biologically linked correlations;
- restricted multivariate scatter, unusual Mahalanobis-distance distributions, clusters, or empty regions;
- identical regression outputs across allegedly different analyses.

Calibrate all screens using genuine comparator data generated under similar instruments, populations, preprocessing, and design when possible. Model rounding, bounds, missingness, clustering, and variable selection. Avoid assuming normality for convenience. Report sensitivity to plausible data-generating models.

## 8. Audit randomization and allocation integrity

Reconstruct the stated assignment mechanism: simple, blocked, stratified, clustered, minimization, adaptive, or another design. Check allocation totals, block/stratum constraints, sequence and run lengths, chronological order, site balance, enrollment timing, and treatment-label consistency.

For baseline covariates:

- do not treat one p-value below .05 as evidence against randomization;
- evaluate the joint pattern with a prespecified or transparent omnibus/randomization test;
- simulate or permute under the actual allocation algorithm, including blocks and strata;
- account for covariate selection and multiplicity;
- consider chance, data errors, post-randomization exclusions, allocation concealment failures, and selective reporting as distinct explanations.

Request the randomization specification, seed or sequence provenance, allocation logs, concealment process, enrollment timestamps, and exclusions when warranted. Do not expose treatment assignments or private participant information unnecessarily.

## 9. Check longitudinal, biological, and operational constraints

### Longitudinal logic

- Verify unique IDs, visit order, time intervals, treatment start, eligibility, outcome dates, censoring, and impossible overlap.
- Reconcile participant status transitions, monotone outcomes where applicable, cumulative events, and attrition.
- Examine copied trajectories, identical changes, abrupt variance shifts, and within-person correlations relative to instrument reliability and timing.
- Distinguish data-entry defaults and scheduled-visit rounding from unexplained regularity.

### Biological and clinical logic

- Check attainable ranges, units, unit conversions, age/sex/anatomical constraints, dose limits, laboratory detection limits, physiological relationships, and mutually dependent measurements.
- Verify that claimed changes are temporally possible and compatible with measurement precision.
- Obtain domain expert review before labeling rare but possible biology as impossible.

### Operational logic

- Check whether recruitment, procedures, assays, and follow-up could fit the stated staff, sites, equipment, calendar, and throughput.
- Treat weekends, holidays, batch runs, copy-forward workflows, and retrospective entry as context-dependent, not inherently suspicious.

## 10. Examine missingness, dates, sites, and investigators

Audit explicit and disguised missing codes, missingness by variable/group/time/site, monotone dropout, impossible combinations, and whether model `n` matches complete cases or imputed records.

Screen for:

- sharp site or investigator differences in recruitment, outcomes, variance, digits, missingness, protocol deviations, or effect sizes;
- bursts, gaps, back-dated entries, implausible visit intervals, or synchronized timestamps;
- a site contributing disproportionate influential observations or treatment benefit;
- changes aligned with personnel, device, protocol, or software changes.

Use hierarchical or shrinkage-aware comparisons for small sites and multiple investigators. Separate operational heterogeneity, case mix, measurement systems, and data-quality failures from fabrication hypotheses.

## 11. Use simulation tools transparently

### Monte Carlo

Define the null data-generating process, design constraints, parameter estimation, rounding, missingness, and test statistic. Record seed, number of simulations, Monte Carlo standard error, tail definition, and sensitivity analyses. If the statistic was chosen after viewing the data, say so.

### Permutation or randomization tests

Permute only exchangeable units and preserve pairs, clusters, blocks, strata, and repeated-measure structures. For trials, prefer the actual assignment mechanism. A naive label shuffle can make ordinary data appear anomalous.

### Bootstrap

Resample the correct unit and preserve dependence. Use bootstrap methods to quantify uncertainty or stability, not to determine whether data were fabricated. State whether intervals are percentile, basic, BCa, or another type and why.

Adjust interpretation for the number of anomaly screens and researcher degrees of freedom. A small simulated tail area is `P(screen at least this extreme | stated null)`, not `P(fabrication | data)`.

## 12. Require converging independent evidence

Create an anomaly ledger with signal, assumptions, null model, strength, benign explanations, dependence on other signals, and verification request. Group signals caused by the same denominator, transcription, exclusion, or rounding problem.

Increase concern only when independent domains converge—for example, irreproducible primary results plus impossible dates plus unexplained source-record gaps. Even then, conclude that independent verification is warranted, not that intent is established.

Request only what is proportionate:

- exact denominators and unrounded outputs;
- data dictionary, missing-code map, and analysis code;
- protocol, registration, amendments, and statistical analysis plan;
- de-identified row-level data or controlled reanalysis;
- randomization and allocation records;
- laboratory/source records, device exports, timestamps, and audit trails;
- site-specific quality-control reports.

If serious concerns persist, recommend confidential review by the journal, sponsor, data-monitoring body, research-integrity office, or other authorized independent party. Preserve neutral language, confidentiality, and chain of custody.
