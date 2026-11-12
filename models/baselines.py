"""
Baseline classifiers for YC start-up outcomes.

Tasks
-----
  exit      : Acquired/Public (1) vs Inactive (0); still-Active companies excluded   [primary]
  survival  : not Inactive (1) vs Inactive (0); all companies                        [secondary]

Feature sets (see extraction/preprocess.py for the A/B/C definitions)
  A        : launch-time features only                    -> the honest question
  A+B      : + web-presence proxies                       -> what the proposal described
  A+B+C    : + current-state features (team size, hiring) -> leakage demonstration only
  text     : TF-IDF of one-liner + description (outcome words removed)

Models: majority-class dummy, Logistic Regression, Random Forest, Gradient Boosting.
Evaluation: 5-fold stratified CV repeated 3x (ROC-AUC, PR-AUC, balanced accuracy, F1),
plus a temporal hold-out (train on cohorts <= 2015, test on 2016-2019).

Usage:  python models/baselines.py
"""
import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, balanced_accuracy_score, f1_score,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore", category=UserWarning)
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "yc_startups_clean.csv"
GROUPS = ROOT / "data" / "processed" / "feature_groups.json"
OUT = ROOT / "docs" / "results"
FIG = ROOT / "docs" / "figures"
SEED = 42
MODEL_COLOR = {"Logistic Regression": "#2a78d6", "Random Forest": "#eb6834", "Gradient Boosting": "#1baf7a"}
SCORING = {"roc_auc": "roc_auc", "pr_auc": "average_precision", "bal_acc": "balanced_accuracy", "f1": "f1"}

BLUE, ORANGE, AQUA, TEXT2, GRID, SURFACE = "#2a78d6", "#eb6834", "#1baf7a", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                     "axes.edgecolor": GRID, "axes.labelcolor": TEXT2, "xtick.color": TEXT2, "ytick.color": TEXT2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "axes.axisbelow": True, "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
                     "axes.titlelocation": "left"})


def preprocessor(num, cat, scale):
    num_steps = [("impute", SimpleImputer(strategy="median"))] + ([("scale", StandardScaler())] if scale else [])
    tr = [("num", Pipeline(num_steps), num)]
    if cat:
        # rare levels (< 15 companies) are pooled into one 'infrequent' column
        tr.append(("cat", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=15,
                                        sparse_output=False), cat))
    return ColumnTransformer(tr)


def models(num, cat):
    return {
        "Dummy (majority)": Pipeline([("prep", preprocessor(num, cat, False)),
                                      ("clf", DummyClassifier(strategy="prior"))]),
        "Logistic Regression": Pipeline([("prep", preprocessor(num, cat, True)),
                                         ("clf", LogisticRegression(C=0.3, class_weight="balanced", max_iter=3000))]),
        "Random Forest": Pipeline([("prep", preprocessor(num, cat, False)),
                                   ("clf", RandomForestClassifier(n_estimators=500, min_samples_leaf=5, max_features="sqrt",
                                                                  class_weight="balanced", n_jobs=-1, random_state=SEED))]),
        "Gradient Boosting": Pipeline([("prep", preprocessor(num, cat, False)),
                                       ("clf", HistGradientBoostingClassifier(learning_rate=0.05, max_iter=300, max_depth=4,
                                                                              min_samples_leaf=20, l2_regularization=1.0,
                                                                              class_weight="balanced", early_stopping=False,
                                                                              random_state=SEED))]),
    }


def text_model():
    return Pipeline([("prep", ColumnTransformer([("tfidf", TfidfVectorizer(min_df=5, max_df=0.5, ngram_range=(1, 2),
                                                                         stop_words="english", sublinear_tf=True), "text")])),
                     ("clf", LogisticRegression(C=1.0, class_weight="balanced", max_iter=3000))])


def task_data(df, task):
    if task == "exit":
        d = df[df["target_exit"].notna()].copy()
        return d, d["target_exit"].astype(int)
    return df.copy(), df["target_survival"].astype(int)


def run_cv(df, groups):
    A = groups["A_launch_num"], groups["A_launch_cat"]
    sets = {"A": A,
            "A+B": (A[0] + groups["B_presence_num"], A[1]),
            "A+B+C": (A[0] + groups["B_presence_num"] + groups["C_current_num"], A[1])}
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=SEED)
    rows = []
    for task in ["exit", "survival"]:
        d, y = task_data(df, task)
        for fs, (num, cat) in sets.items():
            for name, pipe in models(num, cat).items():
                if name.startswith("Dummy") and fs != "A":
                    continue
                r = cross_validate(pipe, d[num + cat], y, cv=cv, scoring=SCORING, n_jobs=1)
                rows.append({"task": task, "features": fs, "model": name, "n": len(d), "pos_rate": round(y.mean(), 3),
                             **{f"{k}": r[f"test_{k}"].mean() for k in SCORING},
                             "roc_auc_std": r["test_roc_auc"].std()})
                print(f"{task:9s} {fs:6s} {name:20s} AUC={rows[-1]['roc_auc']:.3f}±{rows[-1]['roc_auc_std']:.3f} "
                      f"balAcc={rows[-1]['bal_acc']:.3f}")
        r = cross_validate(text_model(), d[["text"]], y, cv=cv, scoring=SCORING)
        rows.append({"task": task, "features": "text (B)", "model": "TF-IDF + LogReg", "n": len(d), "pos_rate": round(y.mean(), 3),
                     **{k: r[f"test_{k}"].mean() for k in SCORING}, "roc_auc_std": r["test_roc_auc"].std()})
        print(f"{task:9s} text   TF-IDF + LogReg      AUC={rows[-1]['roc_auc']:.3f}")
    return pd.DataFrame(rows), sets


def temporal_holdout(df, sets):
    """Train on older cohorts, test on newer ones (closer to a real forecasting setting)."""
    rows = []
    for task in ["exit", "survival"]:
        d, y = task_data(df, task)
        tr, te = d["batch_year"] <= 2015, d["batch_year"] >= 2016
        for fs in ["A", "A+B"]:
            num, cat = sets[fs]
            for name, pipe in models(num, cat).items():
                pipe.fit(d.loc[tr, num + cat], y[tr])
                p = pipe.predict_proba(d.loc[te, num + cat])[:, 1]
                rows.append({"task": task, "features": fs, "model": name, "n_train": int(tr.sum()), "n_test": int(te.sum()),
                             "roc_auc": roc_auc_score(y[te], p), "pr_auc": average_precision_score(y[te], p),
                             "bal_acc": balanced_accuracy_score(y[te], p >= 0.5), "f1": f1_score(y[te], p >= 0.5)})
    return pd.DataFrame(rows)


def importance_and_roc(df, sets):
    d, y = task_data(df, "exit")
    num, cat = sets["A+B"]
    X = d[num + cat]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=SEED)

    fig, ax = plt.subplots(figsize=(5.8, 5))
    for name, pipe in [(k, v) for k, v in models(num, cat).items() if not k.startswith("Dummy")]:
        col = MODEL_COLOR[name]
        pipe.fit(Xtr, ytr)
        p = pipe.predict_proba(Xte)[:, 1]
        fpr, tpr, _ = roc_curve(yte, p)
        ax.plot(fpr, tpr, color=col, lw=2, label=f"{name}  AUC={roc_auc_score(yte, p):.2f}")
        if name == "Random Forest":
            rf = pipe
    ax.plot([0, 1], [0, 1], color=TEXT2, ls="--", lw=1, label="Chance  AUC=0.50")
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
    ax.set_title("ROC – exit vs failure (features A+B, 25% hold-out)")
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "06_roc_exit.png", dpi=180); plt.close(fig)

    pi = permutation_importance(rf, Xte, yte, scoring="roc_auc", n_repeats=20, random_state=SEED, n_jobs=-1)
    imp = pd.DataFrame({"feature": X.columns, "importance": pi.importances_mean, "std": pi.importances_std})
    imp = imp.sort_values("importance", ascending=False)
    imp.to_csv(OUT / "permutation_importance_rf_exit.csv", index=False)
    top = imp.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(top["feature"], top["importance"], xerr=top["std"], color=BLUE, height=0.6,
            error_kw={"ecolor": TEXT2, "lw": 1})
    ax.grid(axis="y", visible=False); ax.set_xlabel("drop in ROC-AUC when feature is shuffled")
    ax.set_title("Random Forest – permutation importance (exit task)")
    fig.tight_layout(); fig.savefig(FIG / "07_feature_importance_rf.png", dpi=180); plt.close(fig)

    lr = models(num, cat)["Logistic Regression"].fit(X, y)
    names = lr.named_steps["prep"].get_feature_names_out()
    coef = pd.Series(lr.named_steps["clf"].coef_[0], index=names).sort_values()
    coef.rename("coef").to_csv(OUT / "logreg_coefficients_exit.csv")
    return imp


def plot_ablation(res):
    sub = res[(res["task"] == "exit") & res["model"].isin(["Logistic Regression", "Random Forest", "Gradient Boosting"])]
    piv = sub.pivot(index="features", columns="model", values="roc_auc").reindex(["A", "A+B", "A+B+C"])[list(MODEL_COLOR)]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    w = 0.26
    for i, (m, col) in enumerate(MODEL_COLOR.items()):
        b = ax.bar(np.arange(3) + (i - 1) * w, piv[m], width=w - 0.03, color=col, label=m)
        ax.bar_label(b, fmt="%.2f", fontsize=8, color=TEXT2, padding=2)
    ax.axhline(0.5, color=TEXT2, ls="--", lw=1); ax.text(0.5, 0.51, "chance", color=TEXT2, fontsize=9, ha="center")
    ax.set_xticks(range(3)); ax.set_xticklabels(["A: launch-time", "A+B: + web presence", "A+B+C: + current state\n(leakage)"])
    ax.set_ylim(0.4, 1.02); ax.set_ylabel("ROC-AUC (5-fold CV ×3)"); ax.grid(axis="x", visible=False)
    ax.set_title("Exit vs failure – how much each feature group adds")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False)
    fig.tight_layout(); fig.savefig(FIG / "08_ablation_feature_groups.png", dpi=180); plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    df["text"] = df["text"].fillna("")
    groups = json.load(open(GROUPS))

    res, sets = run_cv(df, groups)
    res.round(4).to_csv(OUT / "cv_results.csv", index=False)
    plot_ablation(res)

    tmp = temporal_holdout(df, sets)
    tmp.round(4).to_csv(OUT / "temporal_holdout_results.csv", index=False)
    print("\nTemporal hold-out (train <=2015, test 2016-2019):\n", tmp.round(3).to_string(index=False))

    imp = importance_and_roc(df, sets)
    print("\nTop features (RF permutation importance, exit task):\n", imp.head(12).round(4).to_string(index=False))

    with open(OUT / "results_summary.md", "w", encoding="utf-8") as f:
        f.write("# Baseline results\n\n## Cross-validation (5-fold stratified, repeated 3x)\n\n")
        f.write(res.round(3).to_markdown(index=False) + "\n\n")
        f.write("## Temporal hold-out (train <= 2015, test 2016-2019)\n\n" + tmp.round(3).to_markdown(index=False) + "\n\n")
        f.write("## Top 15 features – RF permutation importance (exit, A+B)\n\n" + imp.head(15).round(4).to_markdown(index=False) + "\n")
    print(f"\nresults -> {OUT}")


if __name__ == "__main__":
    main()
