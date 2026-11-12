# Clasificarea traiectoriei start-up-urilor de tehnologie (Y Combinator)

Predicting whether a Y Combinator start-up ends up **exiting** (acquired / IPO) or **failing** (inactive),
using only information available from the public YC directory and classical ML models.

Data source: <https://www.ycombinator.com/companies>

## Repository structure

```
extraction/
  scrape.py                  crawl the YC directory (Algolia index behind the page) -> data/raw/
  enrich_company_pages.py    OPTIONAL: per-company pages -> founders, year founded, social links
  preprocess.py              cleaning, filtering, feature engineering -> data/processed/
  eda.py                     descriptive statistics + figures -> docs/
models/
  baselines.py               Dummy, Logistic Regression, Random Forest, Gradient Boosting (+ TF-IDF text model)
data/
  raw/yc_companies_raw.json            all 6,387 YC companies, raw records
  processed/yc_startups_clean.csv      2,034 mature companies (batches 2005–2019) x 87 columns
  processed/feature_groups.json        feature lists per group (A / B / C)
docs/
  figures/                   charts for the presentation
  results/                   descriptives.md, cv_results.csv, temporal_holdout_results.csv, results_summary.md
```

## Reproduce

```bash
pip install -r requirements.txt
python extraction/scrape.py                 # official source (reads a fresh Algolia key from the page)
python extraction/enrich_company_pages.py   # optional, ~20 min
python extraction/preprocess.py             # --max-year 2019 by default
python extraction/eda.py
python models/baselines.py                  # ~4 min
```

## 1. Data acquisition

The directory page is a front-end for an Algolia index (`YCCompany_production`). `scrape.py`:

* reads the current public search key from the page (the key is time-limited: a hard-coded key stops working once it expires);
* lists all batches via the `batch` facet and queries each batch separately (Algolia caps a query at 1,000 hits);
* de-duplicates on `id` and stores the raw records unchanged, so feature engineering can be redone without crawling again.

The raw file in `data/raw/` was scraped from the official source on 2026-11-11 (`"source": "official"` in its `meta` field).

Result: **6,387 companies, 29 raw attributes** (name, one-liner, description, batch, status, industry, sub-industry,
tags, regions, locations, team size, website, logo, top-company flag, hiring flag, stage, YC partner, demo-day video, …).

## 2. Cleaning & filtering

| Step | Effect |
|---|---|
| De-duplicate on `id`, then `slug` | 0 duplicates |
| Keep **mature cohorts** (batch ≤ 2019, ≥ 7 years old) | 2,034 companies |
| Drop unparsable batches (`Unspecified`) | 1 |
| Normalise text, merge duplicated tags (`E-Commerce`/`E-commerce`) | |
| Rare categories (< 15 companies) pooled into "infrequent" (done inside the CV pipeline) | |
| Missing `team_size` kept as NaN (not replaced by 1), median-imputed inside the pipeline | |
| Near-constant features (> 99.5 % one value) removed | `region_oceania` |
| Outcome words (“acquired”, “was”, “shut down”, “IPO”…) removed from text before TF-IDF | |

### Targets
* **exit** (primary): Acquired + Public = 1 (557) vs Inactive = 0 (657); still-Active companies excluded → 1,214 companies, 46 % positive
* **survival** (secondary): everything except Inactive = 1 → 2,034 companies, 68 % positive

### Feature groups: what was known *when*
The directory shows each company **as it is today**, so some attributes reveal the outcome. Features are grouped by when the information exists:

| Group | Features | Use |
|---|---|---|
| **A – launch-time** (56) | batch year & season, industry, sub-industry, country, macro-region, Bay Area / NYC, # locations, # tags, 30 top tags (multi-hot), non-profit, demo-day / application video, name length | honest model |
| **B – web presence** (14) | has website, website TLD, has logo, has description, description length, one-liner length, # former names, YC partner listed | proxy, reported separately |
| **C – current state** (5) | team size, hiring now, YC “top company”, stage = Growth, remote | **leakage, demo only** |

Example: *no* inactive company is “hiring now” or a “top company”; median current team size is 2 for inactive vs 27 for active companies.

## 3. Baseline results (5-fold stratified CV, repeated 3×)

**Exit vs failure, ROC-AUC**

| Features | Dummy | Logistic Regression | Random Forest | Gradient Boosting |
|---|---|---|---|---|
| A (launch-time) | 0.50 | 0.645 | **0.660** | 0.641 |
| A + B (+ web presence) | – | 0.720 | **0.731** | 0.718 |
| A + B + C (leaky) | – | 0.773 | 0.785 | 0.778 |
| text only (TF-IDF + LR) | | 0.658 | | |

Temporal hold-out (train on 2005–2015, test on 2016–2019), Random Forest: AUC 0.65 (A), 0.70 (A+B).
Full tables: `docs/results/results_summary.md`.

**Takeaways**
* Launch-time information alone gives a modest but real signal (AUC ≈ 0.66). Predicting start-up outcomes is hard.
* The most useful launch-time features are industry and sub-industry, batch year, name length and the SaaS, fintech and analytics tags. B2B and fintech companies exit more often than consumer, healthcare and industrials. Later cohorts have a lower exit share; they have had less time to be acquired.
* Web-presence features add ~0.07 AUC, but mostly because dead companies stop maintaining their profiles (missing logo/website). That reflects what happened afterwards, not something knowable at launch.

## 4. Next steps (Phase 2)
* Run `enrich_company_pages.py`: founders count, year founded (years before YC), social links
* Hyper-parameter tuning (nested CV), calibration, threshold selection
* Additional models: SVM, k-NN, XGBoost/LightGBM; text embeddings of the one-liner
* Survival analysis framing (time-to-event, accounts for censoring of recent cohorts)
* SHAP explanations
