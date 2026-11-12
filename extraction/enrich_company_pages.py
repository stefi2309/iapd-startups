"""
OPTIONAL enrichment: fetch each company's own page (ycombinator.com/companies/<slug>)
to get fields that are NOT in the Algolia search index:
    founders_count, year_founded, has_linkedin, has_twitter, has_facebook,
    has_crunchbase, has_github

Writes data/raw/yc_company_pages.jsonl (one line per company, resumable).
preprocess.py merges it automatically if the file exists.

The page is a React/Inertia app: the company record is embedded as JSON in a
`data-page="..."` attribute. If YC changes the page structure, adjust parse_page().

Usage:  python extraction/enrich_company_pages.py --max-year 2019      (~2,000 requests, ~20 min)
"""
import argparse
import html
import json
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "yc_companies_raw.json"
OUT = ROOT / "data" / "raw" / "yc_company_pages.jsonl"
UA = {"user-agent": "Mozilla/5.0 (academic project, IAPD - UPB)"}


def find_company(obj):
    """Depth-first search for the dict that looks like the company record."""
    if isinstance(obj, dict):
        if "founders" in obj and ("slug" in obj or "name" in obj):
            return obj
        for v in obj.values():
            r = find_company(v)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_company(v)
            if r:
                return r
    return None


def parse_page(text: str) -> dict | None:
    for m in re.finditer(r'data-page="([^"]+)"', text):
        try:
            c = find_company(json.loads(html.unescape(m.group(1))))
        except json.JSONDecodeError:
            continue
        if c:
            yf = c.get("year_founded")
            return {
                "founders_count": len(c.get("founders") or []),
                "year_founded": int(yf) if str(yf or "").isdigit() else None,
                "has_linkedin": int(bool(c.get("linkedin_url"))),
                "has_twitter": int(bool(c.get("twitter_url"))),
                "has_facebook": int(bool(c.get("fb_url"))),
                "has_crunchbase": int(bool(c.get("cb_url"))),
                "has_github": int(bool(c.get("github_url"))),
            }
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-year", type=int, default=2019)
    ap.add_argument("--delay", type=float, default=0.5)
    args = ap.parse_args()

    companies = json.load(open(RAW, encoding="utf-8"))["companies"]
    todo = [c for c in companies
            if re.search(r"\d{4}$", c.get("batch", "")) and int(c["batch"][-4:]) <= args.max_year]
    done = set()
    if OUT.exists():
        done = {json.loads(l)["id"] for l in open(OUT, encoding="utf-8")}
    todo = [c for c in todo if c["id"] not in done]
    print(f"{len(done)} already fetched, {len(todo)} to go")

    s = requests.Session()
    fails = 0
    with open(OUT, "a", encoding="utf-8") as f:
        for i, c in enumerate(todo, 1):
            try:
                r = s.get(f"https://www.ycombinator.com/companies/{c['slug']}", headers=UA, timeout=30)
                rec = parse_page(r.text) if r.ok else None
            except requests.RequestException:
                rec = None
            if rec is None:
                fails += 1
                if fails == 20 and i == 20:
                    raise SystemExit("First 20 pages could not be parsed - the page structure has changed; "
                                     "inspect one page's HTML and update parse_page().")
                continue
            f.write(json.dumps({"id": c["id"], **rec}) + "\n")
            if i % 100 == 0:
                print(f"  {i}/{len(todo)}  (failed: {fails})")
                f.flush()
            time.sleep(args.delay)
    print(f"done, failed: {fails}  -> {OUT}")


if __name__ == "__main__":
    main()
