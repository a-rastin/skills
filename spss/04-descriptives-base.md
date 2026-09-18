# 04 — Descriptives and Base Procedures

Source docs: `IBM_SPSS_Statistics_Base` (Ch. 1 Core features), Syntax Reference entries, Brief Guide Ch. 4–6.

All procedures below assume an active dataset (`GET FILE=` first). Dialog path is `Analyze > ...`; every dialog has a `Paste` button that emits the syntax shown.

## Table of contents

1. Audit first: CODEBOOK, FREQUENCIES, DESCRIPTIVES, EXPLORE
2. Crosstabs, Means, Summarize, OLAP
3. Comparing means: T-TEST, ONEWAY, GLM univariate, Proportions
4. Association: CORRELATIONS, PARTIAL CORR, DISTANCES, CHI-SQUARE
5. Regression family (base): LINEAR, CURVEFIT, PLS, KNN, DISCRIMINANT
6. Reduction: FACTOR, CLUSTER (TwoStep/Hierarchical/K-means)
7. Nonparametrics, Multiple Response, Reliability, Other
8. Power, Meta-analysis, Simulation, Geospatial
9. Snippet library

---

## 1. Audit first

```spss
CODEBOOK gender income /VARINFO LABEL VALUELABELS MISSING /OPTIONS VARORDER=MEASURE.

FREQUENCIES VARIABLES=gender inccat
  /BARCHART PERCENT
  /ORDER=ANALYSIS.

DESCRIPTIVES VARIABLES=age income
  /STATISTICS=MEAN STDDEV MIN MAX SEMEAN KURTOSIS SKEWNESS.

EXAMINE VARIABLES=income BY gender
  /PLOT=BOXPLOT HISTOGRAM NPPLOT
  /STATISTICS=DESCRIPTIVES EXTREME
  /MISSING=LISTWISE.
```

- `FREQUENCIES` = categoricals + histograms/bar/pie; `/FORMAT=NOTABLE` suppresses tables when only charts/stats needed.
- `DESCRIPTIVES` = fast scale summaries; `/SAVE` creates Z-scores.
- `EXAMINE` = EDA with outlier lists, Levene, normality plots.

## 2. Crosstabs, Means, Summarize, OLAP

```spss
CROSSTABS TABLES=gender BY inccat
  /CELLS=COUNT ROW COLUMN EXPECTED RESID
  /STATISTICS=CHISQ PHI LAMBDA CC
  /METHOD=EXACT TIMER(5).   /* Exact Tests module; drop if unavailable */

MEANS TABLES=income BY gender BY dept
  /CELLS=MEAN COUNT STDDEV SEMEAN.

SUMMARIZE TABLES=income BY gender
  /TITLE='Mean income by gender' /MISSING=VARIABLE.
```

OLAP Cubes = pivoted `MEANS` with custom summaries; `REPORT` = paginated case listings with breaks/totals.

## 3. Comparing means

```spss
* One-sample / independent / paired.
T-TEST TESTVAL=50000 /VARIABLES=income.
T-TEST GROUPS=gender(1 2) /VARIABLES=income /MISSING=ANALYSIS /CRITERIA=CI(.95).
T-TEST PAIRS=salbegin WITH salary.

ONEWAY income BY dept
  /STATISTICS=DESCRIPTIVES HOMOGENEITY BROWNFORSYTHE WELCH
  /POSTHOC=TUKEY BONFERRONI ALPHA(0.05)
  /MISSING=ANALYSIS.

* Univariate GLM (ANOVA/ANCOVA with interactions, post-hocs, EMMEANS).
UNIANOVA income BY gender dept WITH age
  /METHOD=SSTYPE(3)
  /POSTHOC=dept(TUKEY)
  /EMMEANS=TABLES(gender*dept)
  /PRINT=DESCRIPTIVE HOMOGENEITY
  /DESIGN=gender dept gender*dept age.
```

Proportions (One-sample / Paired / Independent) and Bland-Altman live under `Analyze > Compare Means` in recent releases — paste dialog syntax.

## 4. Association

```spss
CORRELATIONS VARIABLES=age income educ
  /PRINT=TWOTAIL NOSIG /MISSING=PAIRWISE.

PARTIAL CORR VARIABLES=income educ BY age
  /SIGNIFICANCE=TWOTAIL /MISSING=LISTWISE.

NONPAR CORR VARIABLES=age income /PRINT=SPEARMAN KENDALL /MISSING=PAIRWISE.

* Proximity / distances.
PROXIMITIES age income /MATRIX OUT='/out/dist.sav' /MEASURE=SEUCLID /STANDARDIZE=VARIABLE Z.
```

Chi-square family is under `CROSSTABS /STATISTICS=CHISQ` (Pearson, LR, Fisher, linear-by-linear).

## 5. Regression family (base)

```spss
REGRESSION
  /MISSING LISTWISE
  /STATISTICS COEFF OUTS R ANOVA COLLIN TOL CHANGE ZPP
  /CRITERIA=PIN(.05) POUT(.10)
  /NOORIGIN
  /DEPENDENT income
  /METHOD=ENTER age educ
  /METHOD=STEPWISE jobtime
  /SAVE PRED RESID COOK LEVER
  /SCATTERPLOT=(*ZRESID ,*ZPRED)
  /RESIDUALS HISTOGRAM(ZRESID) NORMPROB(ZRESID).

CURVEFIT VARIABLES=income WITH year
  /MODEL=LINEAR QUADRATIC EXPONENTIAL
  /PRINT ANOVA /PLOT FIT.

PLUM satis BY gender WITH age   /* Ordinal regression */
  /LINK=LOGIT /PRINT=FIT PARAMETER SUMMARY.
```

- Linear/Ordinal/Elastic-Net/Lasso/Ridge dialogs all paste to `REGRESSION`/`PLUM` with `/REGULARIZATION` extras — prefer pasted syntax verbatim.
- `DISCRIMINANT GROUPS=group(1 3) /VARIABLES=x1 x2 /ANALYSIS ALL /PRIORS EQUAL /STATISTICS=TABLE /PLOT=COMBINED.` for classification.
- `KNN` (Nearest Neighbor), `PLS` (Partial Least Squares) are dialog-paste only; keep pasted blocks intact.

## 6. Reduction: FACTOR, CLUSTER

```spss
FACTOR VARIABLES=q1 TO q12
  /MISSING LISTWISE
  /PRINT INITIAL EXTRACTION ROTATION FSCORE
  /CRITERIA MINEIGEN(1) ITERATE(25)
  /EXTRACTION PC
  /ROTATION VARIMAX
  /SAVE REG(ALL)
  /PLOT EIGEN ROTATION.

QUICK CLUSTER age income educ
  /MISSING=LISTWISE
  /CRITERIA=CLUSTER(3) MXITER(10) CONVERGE(0)
  /METHOD=KMEANS(NOUPDATE)
  /SAVE CLUSTER DISTANCE
  /PRINT INITIAL ANOVA CLUSTER DISTAN.

* Hierarchical + TwoStep are dialog-paste (CLUSTER / TWOSTEP CLUSTER); keep pasted syntax.
```

## 7. Nonparametrics, Multiple Response, Reliability, other

```spss
NPAR TESTS
  /K-S(NORMAL)=income
  /M-W= income BY gender(1 2)
  /K-W= income BY dept(1 4)
  /WILCOXON=salbegin WITH salary
  /FRIEDMAN=q1 q2 q3
  /METHOD=EXACT TIMER(5).
NPTESTS ... .  /* newer nonparametric dialogs paste to NPTESTS; keep verbatim */

MULT RESPONSE GROUPS=media 'Media use' (tv radio press (1))
  /FREQUENCIES=media.

RELIABILITY VARIABLES=q1 TO q8
  /SCALE('Satisfaction') ALL
  /MODEL=ALPHA
  /STATISTICS=DESCRIPTIVE SCALE CORR
  /SUMMARY=TOTAL MEANS VARIANCE.

ROC default BY group (1)
  /PLOT=CURVE(REFERENCE)
  /PRINT=SE COORDINATES
  /CRITERIA=CUTOFF(INCLUDE) TESTPOS(LARGE) DISTRIBUTION(FREE) CI(95).
```

- Weighted Kappa, Ratio Statistics (`RATIO STATISTICS`), P-P/Q-Q plots (`PPLOT`), Time-Series Filters — all dialog-paste; keep blocks.
- Exact p-values: add `/METHOD=EXACT TIMER(n)` or `/METHOD=MC CIN(99) SAMPLES(10000)` (Exact Tests module). Monte-Carlo reproducibility: `SET MTINDEX=` first.

## 8. Power, Meta-analysis, Simulation, Geospatial

Dialog-paste only; do not hand-invent. Typical pasted heads to recognise and keep:

- Power: `POWER MEANS ...`, `POWER PROPORTIONS ...`, `POWER CORRELATIONS ...` (precision, N, effect size tabs).
- Meta-analysis (continuous/binary/ES/regression + forest/funnel plots).
- Simulation: `SIMPLAN ... .` then `SIMRUN ... .` (build plan, then run).
- Geospatial: `SPATIAL ASSOCIATION RULES` / `SPATIAL MAPSPEC` family.

## 9. Snippet library (copy-paste starters)

```spss
* Quick profile of every variable.
FREQUENCIES VARIABLES=ALL /FORMAT=NOTABLE /STATISTICS=MINIMUM MAXIMUM MEAN MEDIAN.
DESCRIPTIVES VARIABLES=ALL /STATISTICS=MEAN STDDEV MIN MAX.

* Group comparison bundle.
MEANS TABLES=income BY gender /CELLS=MEAN COUNT STDDEV.
T-TEST GROUPS=gender(1 2) /VARIABLES=income.
ONEWAY income BY dept /STATISTICS=DESCRIPTIVES HOMOGENEITY /POSTHOC=TUKEY ALPHA(0.05).

* Scale quality.
RELIABILITY VARIABLES=q1 TO q8 /SCALE('Q') ALL /MODEL=ALPHA /SUMMARY=TOTAL.
FACTOR VARIABLES=q1 TO q8 /PRINT INITIAL EXTRACTION ROTATION /CRITERIA MINEIGEN(1)
  /EXTRACTION PC /ROTATION VARIMAX /PLOT EIGEN.
```
