"""
Raw YC records (data/raw/yc_companies_raw.json) -> clean modelling table
(data/processed/yc_startups_clean.csv) + feature-group definitions
(data/processed/feature_groups.json).

Steps
-----
1. Load, de-duplicate (id, then slug), normalise empty strings / placeholders.
2. Keep *mature* cohorts only (batch year <= --max-year, default 2019) so every
   company has had >= 7 years to fail, exit or survive.
3. Build targets:
     target_exit      1 = Acquired / Public, 0 = Inactive, NaN = still Active
     target_survival  1 = not Inactive,      0 = Inactive
4. Engineer features and split them into three groups by *when the information
   exists*, which is what decides whether a feature leaks the outcome:
     A  launch      - known at Demo Day (cohort, sector, location, tags, name, YC media)
     B  presence    - profile/web-presence signals; maintained over time, so they are
                      *proxies* of being alive (website, logo, description, rebrands)
     C  current     - describe the company today (team size, hiring, top-company badge,
                      stage, remote policy). Excluded from honest models; used only to
                      demonstrate leakage.
5. Drop near-constant numeric columns and print a data-quality report.
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "yc_companies_raw.json"
PAGES = ROOT / "data" / "raw" / "yc_company_pages.jsonl"   # optional, from enrich_company_pages.py
OUT_DIR = ROOT / "data" / "processed"

N_TOP_TAGS = 30
BAY_AREA = {"San Francisco", "Palo Alto", "Mountain View", "San Mateo", "Menlo Park", "Redwood City",
            "Oakland", "Berkeley", "San Jose", "Sunnyvale", "Santa Clara", "Burlingame",
            "South San Francisco", "Los Altos", "Emeryville", "Cupertino", "Foster City"}
MACRO_REGIONS = ["America / Canada", "Europe", "South Asia", "Latin America", "Southeast Asia",
                 "Africa", "Middle East and North Africa", "East Asia", "Oceania"]
# words in descriptions that directly reveal the outcome (removed before text modelling)
OUTCOME_WORDS = r"\b(acquired|acquisition|acquires|shut|shutdown|closed|defunct|no longer|was|were|" \
                r"formerly|merged|ipo|nyse|nasdaq|public company|went public|sold to|exited)\b"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def load_raw(path: Path) -> pd.DataFrame:
    obj = json.load(open(path, encoding="utf-8"))
    df = pd.DataFrame(obj["companies"] if isinstance(obj, dict) else obj)
    print(f"raw records: {len(df)}  (source={obj.get('meta', {}).get('source') if isinstance(obj, dict) else '?'})")
    return df


def clean(df: pd.DataFrame, max_year: int) -> pd.DataFrame:
    n0 = len(df)
    df = df.drop_duplicates("id").drop_duplicates("slug")
    print(f"duplicates removed: {n0 - len(df)}")

    for c in ["name", "one_liner", "long_description", "website", "all_locations", "industry",
              "subindustry", "batch", "status", "stage", "partners"]:
        df[c] = df[c].fillna("").astype(str).str.strip()
    for c in ["tags", "regions", "industries", "former_names"]:
        df[c] = df[c].apply(lambda v: v if isinstance(v, list) else [])
    df["tags"] = df["tags"].apply(lambda ts: sorted({t.strip().replace("E-Commerce", "E-commerce") for t in ts}))

    m = df["batch"].str.extract(r"^(Winter|Summer|Spring|Fall) (\d{4})$")
    df["batch_season"], df["batch_year"] = m[0], pd.to_numeric(m[1])
    unparsed = df["batch_year"].isna().sum()
    df = df[df["batch_year"].notna() & (df["batch_year"] <= max_year)].copy()
    df["batch_year"] = df["batch_year"].astype(int)
    print(f"kept mature cohorts <= {max_year}: {len(df)}  (dropped {unparsed} with unparsable batch e.g. 'Unspecified')")

    df = df[df["status"].isin(["Active", "Inactive", "Acquired", "Public"])].copy()
    return df


def build_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    f = pd.DataFrame(index=df.index)
    f["id"], f["name"], f["slug"], f["batch"], f["status"] = df["id"], df["name"], df["slug"], df["batch"], df["status"]

    # ---- targets
    f["target_exit"] = df["status"].map({"Acquired": 1, "Public": 1, "Inactive": 0})  # NaN for Active
    f["target_survival"] = (df["status"] != "Inactive").astype(int)

    A_num, A_cat, B_num, C_num = [], [], [], []

    # ---- A: launch-time
    f["batch_year"] = df["batch_year"]; A_num.append("batch_year")
    f["is_winter_batch"] = (df["batch_season"] == "Winter").astype(int); A_num.append("is_winter_batch")
    f["industry"] = df["industry"].replace("", "Unspecified"); A_cat.append("industry")
    f["subindustry"] = df["subindustry"].str.split("->").str[-1].str.strip().replace("", "Unspecified"); A_cat.append("subindustry")

    countries = df["regions"].apply(lambda r: next((x for x in r if x not in MACRO_REGIONS and "Remote" not in x), "Unspecified"))
    f["country"] = countries; A_cat.append("country")
    f["is_usa"] = (countries == "United States of America").astype(int); A_num.append("is_usa")
    for reg in MACRO_REGIONS:
        col = "region_" + slug(reg)
        f[col] = df["regions"].apply(lambda r: int(reg in r))
        A_num.append(col)
    city = df["all_locations"].str.split(";").str[0].str.split(",").str[0].str.strip()
    f["city"] = city.replace("", "Unspecified")
    f["is_bay_area"] = city.isin(BAY_AREA).astype(int); A_num.append("is_bay_area")
    f["is_nyc"] = (city == "New York City").astype(int); A_num.append("is_nyc")
    f["n_locations"] = df["all_locations"].apply(lambda s: len([x for x in s.split(";") if x.strip()])); A_num.append("n_locations")

    f["tags_count"] = df["tags"].apply(len); A_num.append("tags_count")
    f["n_industries"] = df["industries"].apply(len); A_num.append("n_industries")
    top_tags = pd.Series([t for ts in df["tags"] for t in ts]).value_counts().head(N_TOP_TAGS).index
    for t in top_tags:
        col = "tag_" + slug(t)
        f[col] = df["tags"].apply(lambda ts: int(t in ts))
        A_num.append(col)
    f["tags"] = df["tags"].apply("|".join)

    f["is_nonprofit"] = df["nonprofit"].fillna(False).astype(int); A_num.append("is_nonprofit")
    f["has_demo_day_video"] = df["demo_day_video_public"].fillna(False).astype(int); A_num.append("has_demo_day_video")
    f["has_app_video"] = df["app_video_public"].fillna(False).astype(int); A_num.append("has_app_video")
    f["has_question_answers"] = df["question_answers"].fillna(False).astype(bool).astype(int); A_num.append("has_question_answers")

    f["name_length"] = df["name"].str.len(); A_num.append("name_length")
    f["name_words"] = df["name"].str.split().apply(len); A_num.append("name_words")
    f["name_has_digit"] = df["name"].str.contains(r"\d").astype(int); A_num.append("name_has_digit")

    # ---- B: profile / web presence (proxies of being alive)
    f["has_website"] = (df["website"] != "").astype(int); B_num.append("has_website")
    tld = df["website"].str.lower().str.extract(r"https?://[^/]+\.([a-z]+)(?:[/:?#]|$)")[0]
    for t in ["com", "io", "co", "ai", "org"]:
        f[f"tld_{t}"] = (tld == t).astype(int); B_num.append(f"tld_{t}")
    f["has_logo"] = (~df["small_logo_thumb_url"].fillna("").str.contains("missing")
                     & (df["small_logo_thumb_url"].fillna("") != "")).astype(int); B_num.append("has_logo")
    f["has_location"] = (df["all_locations"] != "").astype(int); B_num.append("has_location")
    f["n_former_names"] = df["former_names"].apply(len); B_num.append("n_former_names")
    f["one_liner_len"] = df["one_liner"].str.len(); B_num.append("one_liner_len")
    f["description_len_log"] = np.log1p(df["long_description"].str.len()); B_num.append("description_len_log")
    f["description_words"] = df["long_description"].str.split().apply(len); B_num.append("description_words")
    f["has_description"] = (df["long_description"] != "").astype(int); B_num.append("has_description")
    f["has_partner"] = (~df["partners"].isin(["", "Unspecified"])).astype(int); B_num.append("has_partner")
    text = (df["one_liner"] + ". " + df["long_description"]).str.lower()
    f["text"] = text.str.replace(OUTCOME_WORDS, " ", regex=True).str.replace(r"\s+", " ", regex=True)

    # ---- C: current state (leaky)
    f["team_size"] = pd.to_numeric(df["team_size"], errors="coerce")  # keep NaN, do not invent 1
    f["team_size_log"] = np.log1p(f["team_size"]); C_num.append("team_size_log")
    f["is_hiring"] = df["isHiring"].fillna(False).astype(int); C_num.append("is_hiring")
    f["is_top_company"] = df["top_company"].fillna(False).astype(int); C_num.append("is_top_company")
    f["stage_growth"] = (df["stage"] == "Growth").astype(int); C_num.append("stage_growth")
    f["is_remote"] = df["regions"].apply(lambda r: int(any("Remote" in x for x in r))); C_num.append("is_remote")

    # ---- optional enrichment from individual company pages
    if PAGES.exists():
        pages = pd.read_json(PAGES, lines=True).set_index("id")
        for col in ["founders_count", "year_founded"]:
            if col in pages:
                f[col] = f["id"].map(pages[col]); A_num.append(col)
        if "year_founded" in f:
            f["years_before_yc"] = (f["batch_year"] - f["year_founded"]).clip(lower=0)
            A_num.append("years_before_yc"); A_num.remove("year_founded")
        for col in ["has_linkedin", "has_twitter", "has_facebook", "has_crunchbase", "has_github"]:
            if col in pages:
                f[col] = f["id"].map(pages[col]); B_num.append(col)
        print(f"merged company-page enrichment for {f['id'].isin(pages.index).sum()} companies")

    # ---- drop near-constant numeric features
    groups = {"A_launch_num": A_num, "A_launch_cat": A_cat, "B_presence_num": B_num, "C_current_num": C_num}
    dropped = []
    for g, cols in groups.items():
        if g.endswith("_num"):
            keep = []
            for c in cols:
                top_share = f[c].value_counts(normalize=True, dropna=False).iloc[0]
                (dropped if (f[c].nunique() <= 1 or top_share > 0.995) else keep).append(c)
            groups[g] = keep
    print(f"near-constant features dropped: {dropped or 'none'}")
    return f, groups


def report(f: pd.DataFrame, groups: dict):
    feats = sum(groups.values(), [])
    print(f"\nfinal dataset: {len(f)} companies x {len(feats)} model features "
          f"({len(groups['A_launch_num']) + len(groups['A_launch_cat'])} launch, "
          f"{len(groups['B_presence_num'])} presence, {len(groups['C_current_num'])} current)")
    print("\nstatus:\n" + f["status"].value_counts().to_string())
    print(f"\ntarget_exit: {f['target_exit'].notna().sum()} labelled, positive rate {f['target_exit'].mean():.3f}")
    print(f"target_survival: positive rate {f['target_survival'].mean():.3f}")
    miss = f[feats].isna().mean()
    print("\nmissing values in features:\n" + (miss[miss > 0].to_string() if (miss > 0).any() else "none"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=RAW)
    ap.add_argument("--max-year", type=int, default=2019)
    args = ap.parse_args()

    df = clean(load_raw(args.raw), args.max_year)
    f, groups = build_features(df)
    report(f, groups)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    f.to_csv(OUT_DIR / "yc_startups_clean.csv", index=False)
    json.dump(groups, open(OUT_DIR / "feature_groups.json", "w"), indent=2)
    print(f"\nsaved -> {OUT_DIR / 'yc_startups_clean.csv'}")


if __name__ == "__main__":
    main()
