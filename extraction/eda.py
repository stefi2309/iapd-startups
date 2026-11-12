"""
Descriptive statistics + figures for the Phase 1 presentation.
Reads data/processed/yc_startups_clean.csv, writes docs/figures/*.png and docs/results/descriptives.md
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "yc_startups_clean.csv"
FIG = ROOT / "docs" / "figures"
RES = ROOT / "docs" / "results"

# validated categorical palette (fixed order) + text tokens
STATUS_ORDER = ["Active", "Acquired", "Inactive", "Public"]
STATUS_COLOR = dict(zip(STATUS_ORDER, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]))
BLUE, TEXT, TEXT2, GRID, SURFACE = "#2a78d6", "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": TEXT2, "xtick.color": TEXT2, "ytick.color": TEXT2,
    "text.color": TEXT, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=180)
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True); RES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA)
    groups = json.load(open(ROOT / "data" / "processed" / "feature_groups.json"))

    # 1. status distribution
    counts = df["status"].value_counts().reindex(STATUS_ORDER)
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    bars = ax.bar(counts.index, counts.values, color=[STATUS_COLOR[s] for s in counts.index], width=0.6)
    ax.bar_label(bars, labels=[f"{v}  ({v / len(df):.0%})" for v in counts.values], padding=3, color=TEXT2)
    ax.set_title(f"Company status today (YC 2005–2019, n={len(df)})"); ax.grid(axis="x", visible=False)
    ax.set_ylabel("companies"); ax.set_ylim(0, counts.max() * 1.15)
    save(fig, "01_status_distribution.png")

    # 2. outcome mix per cohort year (100% stacked)
    ct = pd.crosstab(df["batch_year"], df["status"]).reindex(columns=STATUS_ORDER, fill_value=0)
    share = ct.div(ct.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    bottom = 0
    for s in STATUS_ORDER:
        ax.bar(share.index, share[s], bottom=bottom, color=STATUS_COLOR[s], label=s, width=0.8,
               edgecolor=SURFACE, linewidth=1.5)
        bottom = bottom + share[s]
    for x, n in ct.sum(axis=1).items():
        ax.text(x, 1.02, str(n), ha="center", fontsize=8, color=TEXT2)
    ax.set_title("Outcome mix by cohort year (numbers above = companies in cohort)")
    ax.set_ylim(0, 1.08); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_xticks(share.index); ax.tick_params(axis="x", rotation=45); ax.grid(axis="x", visible=False)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.18), frameon=False)
    save(fig, "02_outcome_by_year.png")

    # 3. exit rate (Acquired/Public among resolved companies) by industry
    lab = df[df["target_exit"].notna()]
    g = lab.groupby("industry")["target_exit"].agg(["mean", "size"]).query("size >= 15").sort_values("mean")
    fig, ax = plt.subplots(figsize=(7.5, 4))
    bars = ax.barh(g.index, g["mean"], color=BLUE, height=0.6)
    ax.bar_label(bars, labels=[f"{m:.0%}  (n={n})" for m, n in zip(g["mean"], g["size"])], padding=3, color=TEXT2, fontsize=9,
                 bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1))
    ov = lab["target_exit"].mean()
    ax.axvline(ov, color=TEXT2, ls="--", lw=1, zorder=0)
    ax.text(ov, -0.9, f" overall {ov:.0%}", color=TEXT2, fontsize=9, va="center")
    ax.set_ylim(-1.2, len(g) - 0.5)
    ax.set_xlim(0, 1); ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.grid(axis="y", visible=False)
    ax.set_title("Exit rate by industry (exited / (exited + dead))")
    save(fig, "03_exit_rate_by_industry.png")

    # 4. leakage: share of companies with a flag, by status
    flags = {"is_hiring": "Hiring now", "is_top_company": "YC 'Top company'", "stage_growth": "Stage = Growth",
             "has_website": "Has website", "has_logo": "Has logo", "has_description": "Has description",
             "tag_saas": "Tag: SaaS", "is_bay_area": "Bay Area"}
    rates = df.groupby("status")[list(flags)].mean().reindex(STATUS_ORDER).T.rename(index=flags)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    w = 0.2
    for i, s in enumerate(STATUS_ORDER):
        ax.bar([x + (i - 1.5) * w for x in range(len(rates))], rates[s], width=w - 0.02, color=STATUS_COLOR[s], label=s)
    ax.set_xticks(range(len(rates))); ax.set_xticklabels(rates.index, fontsize=9)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.grid(axis="x", visible=False)
    for x in (2.5, 5.5):
        ax.axvline(x, color=GRID, lw=1.2)
    ax.text(1, 1.05, "C · current state (leaky)", ha="center", color=TEXT2, fontsize=9)
    ax.text(4, 1.05, "B · web presence (proxy)", ha="center", color=TEXT2, fontsize=9)
    ax.text(6.5, 1.05, "A · launch-time", ha="center", color=TEXT2, fontsize=9)
    ax.set_ylim(0, 1.12); ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False)
    ax.set_title("Why feature timing matters: share of companies with each attribute, by status")
    save(fig, "04_leakage_check.png")

    # 5. top tags
    tags = df["tags"].fillna("").str.split("|").explode()
    top = tags[tags != ""].value_counts().head(15).sort_values()
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    bars = ax.barh(top.index, top.values, color=BLUE, height=0.6)
    ax.bar_label(bars, padding=3, color=TEXT2, fontsize=9); ax.grid(axis="y", visible=False)
    ax.set_title("Most frequent tags (of 2,034 companies)")
    save(fig, "05_top_tags.png")

    # descriptives table
    feats = groups["A_launch_num"] + groups["B_presence_num"] + groups["C_current_num"]
    desc = df[feats].describe().T[["mean", "std", "min", "50%", "max"]].round(3)
    desc.insert(0, "group", ["A launch"] * len(groups["A_launch_num"]) + ["B presence"] * len(groups["B_presence_num"])
                + ["C current"] * len(groups["C_current_num"]))
    cats = pd.DataFrame({c: [df[c].nunique(), df[c].value_counts().index[0], f"{df[c].value_counts(normalize=True).iloc[0]:.0%}"]
                         for c in groups["A_launch_cat"] + ["city"]}, index=["levels", "most common", "share"]).T
    with open(RES / "descriptives.md", "w", encoding="utf-8") as f:
        f.write(f"# Dataset descriptives\n\n{len(df)} companies, YC batches 2005–2019, "
                f"{len(feats) + len(groups['A_launch_cat'])} model features\n\n")
        f.write("## Status\n\n" + counts.to_frame("n").assign(share=lambda d: (d.n / d.n.sum()).round(3)).to_markdown() + "\n\n")
        f.write("## Categorical features\n\n" + cats.to_markdown() + "\n\n")
        f.write("## Numeric / binary features\n\n" + desc.to_markdown() + "\n")
    print(f"figures -> {FIG}\ndescriptives -> {RES / 'descriptives.md'}")


if __name__ == "__main__":
    main()
