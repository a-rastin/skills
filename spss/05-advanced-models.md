# 05 — Advanced Models (Regression → Survival → Forecasting → Segmentation)

Source docs: Advanced Statistics, Regression, Categories, Complex Samples, Exact Tests, Bootstrapping, Missing Values, Data Preparation, Forecasting, Neural Network, Decision Trees, Conjoint, Direct Marketing, Custom Tables (survey_sample.sav).

All commands assume an active dataset. Dialog path given per section; `Paste` emits valid syntax — keep pasted blocks verbatim and only change variable names/values.

## Table of contents

1. Regression module (LOGISTIC, NOMREG, PROBIT, QUANTILE, NLR, WLS, 2SLS)
2. GLM / MIXED / GENLIN (Advanced Statistics core)
3. Loglinear / Survival (HILOGLINEAR, GENLOG, SURVIVAL, KM, COXREG, SURVREG)
4. Categories / optimal scaling (CATREG, CATPCA, OVERALS, CORRESPONDENCE, PROXSCAL, PREFSCAL)
5. Complex Samples (CSPLAN + CS*)
6. Exact Tests + Bootstrapping wrappers
7. Missing Values (MVA + Multiple Imputation)
8. Forecasting / Time Series (TSMODEL, TSAPPLY, SEASON, SPECTRA, TCM)
9. Segmentation: Trees, Neural Networks, Conjoint, Direct Marketing
10. Data Preparation procedures (VALIDATE, ADP, DETECTANOMALY, Optimal Binning)

---

## 1. Regression module

```spss
* Binary logistic (case-level fit, stepwise, classification).
LOGISTIC REGRESSION VARIABLES=default
  /METHOD=FSTEP(LR) age income employ
  /CONTRAST (gender)=Indicator(1)
  /PRINT=SUMMARY CI(95)
  /CRITERIA=PIN(.05) POUT(.10) ITERATE(20) CUT(.5)
  /SAVE=PRED PGROUP RESID
  /CLASSPLOT.

* Multinomial (subpopulation fit; use for 3+ categories or matched designs).
NOMREG satis (BASE=LAST ORDER=ASCENDING) WITH age BY gender
  /CRITERIA CIN(95) DELTA(0) MXITER(100)
  /MODEL
  /STEPWISE=PIN(.05) POUT(.1)
  /PRINT=FIT PARAMETER SUMMARY LRT CPS MFI.

PROBIT dose OF n WITH logdose
  /LOG NONE  /* or LOG — dose transform */
  /MODEL PROBIT  /* or LOGIT */
  /PRINT FREQ CI
  /CRITERIA ITERATE(50).

* Quantile (median etc., robust to skew).
QUANTILE REGRESSION income WITH age educ
  /MODEL ...
  /QUANTILE=0.5
  /CRITERIA ...
  /SAVE PRED.

* Nonlinear / weighted / instrumental.
NLR y WITH x1 x2
  /PRED b0 + b1*EXP(-b2*x1)
  /SAVE PRED RESID
  /CRITERIA ITERATE(100).
WLSREG y WITH x1 x2 /WEIGHT=wvar /POWER RANGE(-2,2,0.5).
2SLS y WITH x1 /INSTRUMENTS z1 z2.
```

Categorical coding appendix (`Regression > Categorical Coding Schemes`): `Indicator, Simple, Deviation, Difference, Helmert, Repeated, Polynomial` — set via `/CONTRAST (var)=Scheme(ref)`. Correlated/repeated binary outcomes → `GENLIN` GEE instead of `LOGISTIC`.

## 2. GLM / MIXED / GENLIN

```spss
* Multivariate + repeated measures.
GLM y1 y2 BY group WITH age
  /METHOD=SSTYPE(3)
  /POSTHOC=group(TUKEY)
  /EMMEANS=TABLES(group) WITH(age=MEAN) COMPARE ADJ(BONFERRONI)
  /PRINT=DESCRIPTIVE HOMOGENEITY
  /DESIGN=group age group*age.
GLM score1 score2 score3 BY treat
  /WSFACTOR=time 3 Polynomial
  /MEASURE=score
  /METHOD=SSTYPE(3)
  /EMMEANS=TABLES(treat*time)
  /DESIGN=treat.

VARCOMP y BY a b /RANDOM=a b /METHOD=REML.
MIXED y BY group WITH time
  /FIXED=group time group*time | SSTYPE(3)
  /RANDOM=INTERCEPT time | SUBJECT(id) COVTYPE(UN)
  /REPEATED=time | SUBJECT(id) COVTYPE(AR1)
  /METHOD=REML
  /EMMEANS=TABLES(group*time)
  /SAVE=PRED RESID.
GENLIN y BY group WITH age
  /MODEL group age group*age DISTRIBUTION=NORMAL LINK=IDENTITY
  /CRITERIA ...
  /REPEATED SUBJECT=id WITHINSUBJECT=time CORRTYPE=AR1  /* GEE variant */
  /EMMEANS TABLES=group.
```

Covariance structures menu: `UN, AR1, CS, VC, DIAG, ARH1, CSH, TOEP...`; estimation `ML/REML`, df `Satterthwaite/Kenward-Roger`. Bayesian ANOVA/loglinear/repeated dialogs paste `BAYES ...` blocks — keep verbatim.

## 3. Loglinear / Survival

```spss
HILOGLINEAR a b c
  /METHOD=BACKWARD
  /CRITERIA MAXSTEPS(10) P(.05) ITERATION(20)
  /PRINT=FREQ RESID ADJUSTED
  /PLOT=RESID.
GENLOG a b c
  /MODEL=POISSON
  /PRINT=FREQ RESID ADJUSTED
  /DESIGN=a b c a*b.
SURVIVAL TABLE=time BY group(1 2)
  /STATUS=event(1)
  /INTERVAL=THRU 60 BY 5
  /PRINT TABLE.
KM time BY group
  /STATUS=event(1)
  /PRINT TABLE MEAN
  /PLOT SURVIVAL HAZARD
  /COMPARE OVERALL POOLED.
COXREG time WITH age
  /STATUS=event(1)
  /CATEGORICAL=gender
  /METHOD=ENTER age gender
  /PRINT=CI(95)
  /PLOT SURVIVAL.
SURVREG RECURRENT endTime WITH age BY female
  /MODEL SUBJECT=patID FRAILTY=GAMMA DISTRIBUTION=WEIBULL
  /ESTIMATION HCONVERGE=1e-12 PCONVERGE=0 FCONVERGE=0 MAXITER(100)
  /STATUS VARIABLE=sideEffect FAILURE=1 RIGHT=0
  /PREDICT SURVIVAL HAZARD
  /FUNCTIONPLOT SURVIVAL HAZARD PLOTBY(female).
```

Time-dependent Cox uses a `COMPUTE TIME PROGRAM` segment — paste from dialog, do not hand-write. AFT distributions: `WEIBULL LOG_NORMAL LOG_LOGISTIC`; frailty: `GAMMA INV_GAUSSIAN`. Kernel Ridge Regression dialogs (Linear/RBF/Polynomial/Sigmoid/Chi2/Cosine/Laplacian + CV folds) are paste-only.

## 4. Categories (optimal scaling)

All require positive-integer category codes — `AUTORECODE` strings/fractionals first; inspect transformation plots to choose scaling level.

```spss
* CATREG / CATPCA / OVERALS / CORRESPONDENCE / PROXSCAL are heavily dialog-driven.
* Keep pasted syntax verbatim; only adjust ANALYSIS scaling, DISCRETIZATION, PLOT.
* Typical pasted heads you will see and must preserve:
* CATREG VARIABLES=... /ANALYSIS ... /DISCRETIZATION ... /MISSING ... /REGULARIZATION ...
* CATPCA VARIABLES=... /ANALYSIS ... /DISCRETIZATION ... /MISSING ... /PRINT ... /PLOT ...
* CORRESPONDENCE TABLE=... /DIMENSION=2 /NORMALIZATION=SYMMETRICAL /PLOT=BIPLOT.
```

Scaling levels: `NOMINAL ORDINAL NUMERIC` (+ spline variants); regularisation for high-dimensional CATREG; `SAVE` rootnames create quantified variables.

## 5. Complex Samples

Two-stage workflow — plan first, analyse second. Never use `WEIGHT CASES` for design adjustment here.

```spss
* Sampling wizard + analysis prep emit CSPLAN blocks; keep them verbatim.
* Analysis procedures all take /PLAN FILE=.
CSDESCRIPTIVES
  /PLAN FILE='/out/my.csplan'
  /SUMMARY VARIABLES=income
  /MEAN /SE /CIN(95).
CSTABULATE
  /PLAN FILE='/out/my.csplan'
  /TABLES VARIABLES=gender BY inccat
  /CELLS POPSIZE TABLEPCT /STATISTICS SE CIN.
CSGLM income BY gender WITH age
  /PLAN FILE='/out/my.csplan'
  /MODEL gender age gender*age
  /STATISTICS SE CIN DEFF.
CSLOGISTIC default (HIGH) WITH age BY gender
  /PLAN FILE='/out/my.csplan'
  /MODEL age gender
  /ODDSRATIOS FACTOR=[gender] /STATISTICS SE CIN.
CSORDINAL satis WITH age BY gender /PLAN FILE='/out/my.csplan' /MODEL ...
CSCOXREG time WITH age /PLAN FILE='/out/my.csplan' /STATUS=event(1) ...
```

Sampling methods: `PPS-WR/WOR, systematic, sequential, SRS, unequal`. Estimation: `WR/WOR equal/unequal`. Designs store strata/cluster/stage weights in `.csplan/.csaplan`.

## 6. Exact Tests + Bootstrapping

```spss
* Exact or Monte Carlo p-values (Exact Tests module).
CROSSTABS TABLES=a BY b /STATISTICS=CHISQ /METHOD=EXACT TIMER(5).
NPAR TESTS /K-W=y BY g(1 3) /METHOD=EXACT TIMER(5).
NPAR TESTS /J-T=y BY g(1 4) /METHOD=MC CIN(99) SAMPLES(10000).
SET MTINDEX=12345.   /* reproducible Monte Carlo / bootstrap seed */

* Bootstrap wrapper goes BEFORE the analysis command.
BOOTSTRAP
  /SAMPLING METHOD=SIMPLE
  /VARIABLES TARGET=y INPUT=x1 x2
  /CRITERIA CILEVEL=95 CITYPE=PERCENTILE NSAMPLES=1000
  /MISSING USERMISSING=EXCLUDE.
REGRESSION /DEPENDENT y /METHOD=ENTER x1 x2.
```

Bootstrap facts: B resamples of size N with replacement; needs ≥1000 samples for percentile/BCa; disables charts; forces listwise deletion; incompatible with MI datasets and fractional weights; regression-only `SAMPLING RESIDUAL/WILD` is syntax-only.

## 7. Missing Values

```spss
* Diagnose first.
MVA VARIABLES=age income educ
  /MPATTERN /DPATTERN /TPATTERN DESCRIBE
  /TTEST /MISMATCH /TABULATE
  /EM(TOLERANCE=0.001 CONVERGENCE=0.0001 ITERATIONS=25).

* Multiple imputation: patterns → impute → analyse pooled.
MULTIPLE IMPUTATION age income educ
  /IMPUTE METHOD=FCS MAXITER=10 NIMPUTATIONS=5
  /CONSTRAINTS ...
  /OUTFILE IMPUTATIONS='/out/imputed.sav'.
* Then run any MI-aware procedure; output pools + per-imputation + original (Imputation__ 0=original).
```

`EM` vs single `REGRESSION` imputation inside `MVA` is for exploration; production missing-data work uses Multiple Imputation (FCS/monotone, Linear/PMM for scale vars, `MAXMODELPARAM`, interaction terms).

## 8. Forecasting / Time Series

```spss
DATE YEAR 2015 MONTH 1.   /* or Analyze > Time Series > Define Dates */
TSMODEL
  /MODEL ...              /* keep pasted Expert-Modeler / ARIMA / Exponential Smoothing blocks */
  /AUXILIARY SEASONLENGTH=12
  /OUTFILE MODEL='/out/tsmodel.xml'.
TSAPPLY
  /MODEL FILE='/out/tsmodel.xml'
  /SAVE PREDICTED(Pred) LCL(LCL) UCL(UCL).
SEASON VARIABLES=sales /PERIODICITY=12 /MODEL=ADDITIVE.
SPECTRA VARIABLES=sales /WINDOW=H mentions...
```

Stats to report: stationary R², R², RMSE/MAE/MAPE/MaxAE/MaxAPE, normalised BIC, Ljung-Box Q, ACF/PACF, outlier types (additive/level-shift/...). Temporal Causal Models (`Create TCM → TCM Forecasting → Scenarios`) and 5000-SKU batch re-estimation are dialog flows — keep pasted `TSMODEL/TSAPPLY` blocks.

## 9. Segmentation

**Decision Trees (`TREE`, dialog-paste):**

- Methods: `CHAID` (multiway, alpha merge/split), `Exhaustive CHAID`, `CRT` (binary, Gini/Twoing impurity, importance chart), `QUEST` (fast unbiased, α=.05).
- Growth: max depth (auto 3 CHAID, 5 CRT/QUEST), min parent/child sizes, interval bins (default 10), pruning by risk SE (default 1; 0 = min risk), surrogates, costs/profits/priors, validation (k-fold ≤25 or split-sample).
- Keep pasted `TREE ... .` verbatim; save node/predicted/probability; export PMML/SQL scoring rules.

**Neural Networks (`MLP`/`RBF`, dialog-paste, needs option):**

- `Analyze > Neural Networks > Multilayer Perceptron / Radial Basis Function`. Example data `bankloan.sav` (default), telecom segmentation.
- Tabs: Partitions (train/test/holdout — case order matters), Architecture (auto vs custom, MLP 1–2 hidden layers, RBF hidden units), Training (MLP: batch/online/mini-batch, scaled-conjugate-gradient/gradient-descent, epochs, stopping), Output/charts, Save (predicted, pseudo-probabilities), Export XML/PMML (no split-file).
- Rescaling and one-of-N coding are training-data-based; keep pasted blocks.

**Conjoint (syntax-only, no GUI):**

```spss
ORTHOPLAN ... .              /* generate orthogonal design → CPLAN.SAV */
PLANCARDS ... .              /* print data-collection cards */
CONJOINT PLAN='CPLAN.SAV' /DATA='RUGRANKS.SAV'
  /RANK=RANK1 TO RANK22 /SUBJECT=ID
  /FACTORS=PACKAGE BRAND (DISCRETE) PRICE (LINEAR LESS)
           SEAL (LINEAR MORE) MONEY (LINEAR MORE)
  /PRINT=SUMMARYONLY  /* or ALL / SIMULATION */
  /PLOT=ALL
  /UTILITY='RUGUTIL.SAV'.
```

`/DATA=*` uses active dataset; `/PLAN=*` uses active plan. Factor models: `DISCRETE, LINEAR MORE/LESS, IDEAL, ANTIIDEAL`. `/SEQUENCE`, `/RANK`, `/SCORE` variants for rank/score/sequence data.

**Direct Marketing (wizard-only, no syntax):** RFM Analysis (transactions → 1 row/customer; Nested vs Independent 5×5×5 binning, scores 111–555, formula `(R*100)+(F*10)+M`), Cluster, Prospect Profiles, Postal-Code Rates, Propensity, Control-Package Test. Drive via wizards; save binned scores to a new dataset.

## 10. Data Preparation procedures

```spss
VALIDATE DATA VARIABLES=age income
  /RULES=...                /* from Define Rules step; cross-variable logic allowed */
  /OUTPUT ... .
ADP ... .                   /* Automated Prep: dates, measurement, quality, rescale, select/construct, XML names */
DETECTANOMALY ... .         /* peer-group anomaly index + impact; randomise order-sensitive data */
* Optimal Binning: Transform > Optimal Binning (supervised by guide var) — keep pasted block with cutpoints.
```

Validate → ADP → Anomaly → Binning is the recommended pre-model cleaning chain.
