# Study-design and statistical-method audit

## Contents

1. Reconstruct the study and estimand
2. Apply design-specific checks
3. Match analysis to data and dependence
4. Audit sample size, power, and precision
5. Audit missing data
6. Audit multiplicity and analytical flexibility
7. Audit models and assumptions
8. Audit robustness, interpretation, and generalizability

## 1. Reconstruct the study and estimand

Do not accept design labels without verifying their operational meaning. Extract:

- target population, sampling frame, eligibility, recruitment, setting, and dates;
- unit of assignment, intervention/exposure, comparator, and allocation mechanism;
- unit of observation and unit of analysis;
- outcome definition, measurement instrument, scale, assessor, and timing;
- time zero, follow-up, censoring, competing events, and analysis population;
- estimand: population, treatment/exposure contrast, outcome, time horizon, and handling of intercurrent events;
- primary hypothesis, directionality, smallest meaningful effect, and prespecified analysis.

Flag target-population/analysis-sample mismatch, ambiguous time zero, post-exposure eligibility, outcome switching, inconsistent variable definitions, and a statistical parameter that does not answer the scientific question.

## 2. Apply design-specific checks

### Randomized trials

Check sequence generation, allocation concealment, implementation roles, blocking/stratification, masking, contamination, adherence, co-interventions, protocol deviations, post-randomization exclusions, attrition, and registration timing.

Distinguish intention-to-treat, treatment-policy, per-protocol, as-treated, and safety populations. Determine whether handling of intercurrent events matches the claimed estimand. Account for cluster or stratified assignment in both analysis and precision. Treat subgroup and per-protocol causal claims cautiously.

### Observational cohorts and cross-sectional studies

Check sampling and participation, exposure timing, reverse causation, confounding, selection, measurement error, informative loss to follow-up, positivity, time-varying confounding, immortal-time bias, overadjustment, and collider conditioning.

Require a defensible covariate-selection rationale grounded in the causal question. Do not accept significance-driven adjustment. Distinguish prevalence, incidence, risk, rate, odds, and hazard.

### Case-control studies

Check whether controls represent the exposure distribution in the source population that generated cases, whether matching is handled in analysis, whether selection depends on exposure, and whether odds ratios are interpreted appropriately. Verify index dates and exposure ascertainment symmetry.

### Diagnostic-accuracy studies

Check patient spectrum, sampling, index-test threshold selection, reference standard, blinding, timing, indeterminate results, partial/differential verification, incorporation bias, and paired comparison of tests. Reconcile sensitivity/specificity counts with the `2×2` table and distinguish predictive values from intrinsic accuracy measures.

### Prediction and machine-learning studies

Check target definition, predictor availability at intended use time, participant-level train/validation/test separation, preprocessing leakage, feature selection, hyperparameter tuning, class imbalance, optimism correction, calibration, discrimination, decision usefulness, and external or temporal validation.

Require the full pipeline to be contained within resampling. Account for clusters and repeated records. Evaluate effective sample size and event count relative to model flexibility; do not rely on accuracy alone.

### Survival and event-history studies

Check time origin, delayed entry, censoring mechanism, competing risks, recurrent events, proportional hazards, time-dependent exposures/covariates, immortal time, and event adjudication. Distinguish hazards from risks and avoid interpreting a hazard ratio as a constant risk ratio.

### Repeated-measure, clustered, and multilevel studies

Identify every dependence level. Check whether models, standard errors, degrees of freedom, and power account for repeated measures, households, centers, batches, classrooms, clinicians, or other clusters. Flag pseudoreplication and treatment effects tested against technical rather than biological replication.

### Laboratory, animal, and preclinical studies

Distinguish biological from technical replicates. Check allocation/randomization, blinding, batch and plate effects, cage/litter effects, exclusions, stopping, dose selection, assay range, normalization, and independent replication. The experimental unit is the smallest unit independently assigned to a condition.

### Systematic reviews and meta-analyses

Check protocol/registration, search coverage and date, reproducible queries, screening, duplicate reports, extraction, risk-of-bias assessment, effect-measure compatibility, dependence among effects, heterogeneity, model choice, small-study/publication bias, sensitivity analyses, and certainty of evidence. Do not treat a funnel-plot pattern as proof of publication bias.

### Qualitative and mixed-methods studies

Do not force quantitative criteria onto qualitative work. Check sampling rationale, researcher positionality/reflexivity, consent, data collection context, coding process, discrepant cases, saturation or information-power claims, triangulation, audit trail, quotations-to-theme linkage, and integration of qualitative and quantitative components.

## 3. Match analysis to data and dependence

Identify outcome scale, distribution, bounds, zero inflation, censoring, clustering, repeated measures, pairing, survey weights, and sampling design before judging the method.

- For continuous outcomes, check linearity/additivity where relevant, residual behavior, variance assumptions, influential observations, and whether transformations preserve the estimand.
- For ordinal outcomes, justify treating scores as continuous or use an ordinal/robust method. Distinguish a single ordinal item from a multi-item scale.
- For counts and rates, consider exposure time, overdispersion, zero inflation, and Poisson versus negative-binomial structure.
- For binary outcomes, use methods respecting probability bounds and interpret risk difference, risk ratio, odds ratio, and marginal versus conditional effects correctly.
- For paired or repeated outcomes, model within-unit dependence. Marginal summaries do not identify paired-test variance.
- For clustered or survey data, incorporate design weights, strata, primary sampling units, finite-population corrections, and multistage dependence when applicable.
- For nonparametric tests, verify independence/pairing, outcome ordering, estimand, tie handling, and whether authors incorrectly describe the test as a comparison of medians without distributional conditions.

Check whether an adjusted estimate and an unadjusted descriptive comparison are being conflated.

## 4. Audit sample size, power, and precision

Reconstruct the calculation using primary outcome, effect or margin, variance/event-rate assumption, allocation ratio, alpha, sidedness, power, attrition, design effect, number/size of clusters, noncompliance, and analysis method.

Flag:

- a calculation for a different outcome or test than the primary analysis;
- effect sizes chosen from an unstable pilot without uncertainty;
- failure to inflate for attrition, clustering, multiplicity, unequal allocation, or low event rate;
- too few clusters or events despite a large participant count;
- model complexity unsupported by effective information;
- “no effect” conclusions based only on nonsignificance and wide intervals;
- retrospective observed power used to interpret a completed study.

For equivalence or noninferiority, verify the clinical/scientific justification and prespecification of margins, analysis populations, alpha, and whether the confidence interval supports the exact claim. For feasibility or pilot work, prioritize estimation and feasibility precision over definitive efficacy claims.

## 5. Audit missing data

Distinguish item missingness, missing covariates, missing outcomes, withdrawal, loss to follow-up, truncation, censoring, and values below detection. Reconcile missing counts with every analysis `n`.

Evaluate:

- reasons, timing, and patterns by group, outcome, site, and prognosis;
- whether complete-case assumptions are credible;
- whether missingness can depend on observed or unobserved values;
- whether the imputation model includes outcomes, exposures, interactions, nonlinearities, design variables, and useful auxiliaries;
- compatibility between imputation and analysis models;
- number of imputations, diagnostics, pooling, and uncertainty;
- handling of clustered, longitudinal, bounded, categorical, censored, and derived variables;
- sensitivity analyses for departures from missing-at-random assumptions.

Do not accept mean imputation, missing-indicator methods, last observation carried forward, or single imputation as generally unbiased defaults. Do not claim that multiple imputation repairs selection caused by unavailable or unmeasured information without assumptions.

## 6. Audit multiplicity and analytical flexibility

Inventory every outcome, time point, subgroup, exposure, model, transformation, covariate set, interaction, threshold, interim look, exclusion rule, and alternative analysis that could generate claims.

Compare manuscript, protocol, registration, statistical analysis plan, and repository timestamps. Distinguish confirmatory from exploratory analyses. Check:

- prespecified primary family and multiplicity control;
- selective emphasis on significant results;
- outcome or time-point switching;
- data-driven subgroup, cut-point, transformation, or covariate choice;
- optional stopping and repeated peeking;
- HARKing or hypotheses presented as a priori after results were known;
- p-value rounding, threshold language, and “trend” claims;
- multiplicity created by multiple model variants even if only one table is shown.

Recommend an appropriate familywise, false-discovery, hierarchical, gatekeeping, simultaneous-interval, multivariate, or clearly exploratory treatment based on the scientific decision. Adjustment does not cure selective reporting; require transparent disclosure.

## 7. Audit models and assumptions

For each model, identify likelihood/estimating equation, link, outcome distribution, predictors, interactions, nonlinear terms, random effects or correlation structure, variance estimator, weights, handling of missingness, and inference method.

Check:

- convergence, boundary estimates, singular fits, complete/quasi-separation, sparse cells, and numerical warnings;
- linearity and functional form, including continuous predictors not arbitrarily categorized;
- residuals, heteroscedasticity, overdispersion, proportionality, influence, leverage, and outliers;
- multicollinearity and whether coefficients answer stable scientific contrasts;
- overfitting, tuning leakage, optimism, and internal validation;
- interaction scale and whether subgroup claims are based on interaction tests rather than separate within-group significance;
- random-effects distribution and enough higher-level units;
- robust/clustered standard errors with an adequate number of clusters;
- penalization, priors, or regularization chosen and reported transparently;
- likelihood, Wald, score, bootstrap, permutation, or Bayesian uncertainty used consistently.

For Bayesian analyses, check prior justification and sensitivity, likelihood, parameterization, convergence diagnostics, effective sample size, posterior predictive checks, interval definition, and whether posterior probabilities are described accurately.

## 8. Audit robustness, interpretation, and generalizability

Require robustness analyses targeted to credible threats rather than a large collection of cosmetic model variants. Useful checks may include alternative confounding control, missing-not-at-random sensitivity, measurement error, unmeasured confounding, competing risks, influential cases, clustering, model form, outcome definition, and protocol deviations.

Interpret in this order:

1. What population and estimand does the design identify?
2. What is the effect direction and magnitude?
3. How precise is it?
4. How vulnerable is it to bias and assumptions?
5. Is it scientifically or clinically important?
6. Does it transport to the claimed population and setting?

Do not equate randomization with freedom from all bias, adjustment with removal of all confounding, nonsignificance with equivalence, statistical significance with importance, or prediction with causation. Calibrate causal verbs to identification assumptions and preserve uncertainty in the abstract and conclusion.
