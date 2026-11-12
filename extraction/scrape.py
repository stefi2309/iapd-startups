"""
Scraper for the Y Combinator company directory (https://www.ycombinator.com/companies).

The directory page is a front-end over an Algolia index (YCCompany_production).
We query that index directly, one batch (cohort) at a time, and save the *raw*
records as JSON. Feature engineering is done separately in preprocess.py, so the
raw data can be re-processed without scraping again.

Usage
-----
    python extraction/scrape.py                      # all batches -> data/raw/yc_companies_raw.json
    python extraction/scrape.py --key <KEY>          # if reading the key from the page fails

Notes
-----
* The Algolia search key on the YC page is a *secured* key with an expiry date
  (validUntil). Hard-coding it breaks the script once it expires, so we read the
  current key from the directory page's HTML on every run.
* Algolia returns at most 1000 hits per query; no YC batch has more than ~400
  companies, so filtering by batch keeps every query well under that limit.
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

APP_ID = "45BWZJ1SGC"
INDEX = "YCCompany_production"
DIRECTORY_URL = "https://www.ycombinator.com/companies"

HEADERS = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.ycombinator.com",
    "referer": "https://www.ycombinator.com/",
    "user-agent": "Mozilla/5.0 (academic project, IAPD - UPB)",
}

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "raw" / "yc_companies_raw.json"


def get_algolia_key(session: requests.Session) -> str:
    """Read the current (time-limited) public search key from the directory page."""
    html = session.get(DIRECTORY_URL, headers={"user-agent": HEADERS["user-agent"]}, timeout=30).text
    # The page embeds: window.AlgoliaOpts = {"app":"45BWZJ1SGC","key":"..."};
    m = re.search(r'AlgoliaOpts\s*=\s*(\{.*?\})', html)
    if m:
        return json.loads(m.group(1))["key"]
    # Fallback: any long base64 blob that decodes to a secured-key payload
    m = re.search(r'"key"\s*:\s*"([A-Za-z0-9+/=]{100,})"', html)
    if m:
        return m.group(1)
    raise RuntimeError("Could not find the Algolia key in the YC page. "
                       "Open the page in a browser, DevTools > Network, filter 'algolia', "
                       "copy x-algolia-api-key and pass it with --key.")


def algolia_query(session, key, params: str) -> dict:
    url = f"https://{APP_ID.lower()}-dsn.algolia.net/1/indexes/*/queries"
    qs = {"x-algolia-application-id": APP_ID, "x-algolia-api-key": key}
    payload = {"requests": [{"indexName": INDEX, "params": params}]}
    r = session.post(url, params=qs, headers=HEADERS, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["results"][0]


def list_batches(session, key) -> list[str]:
    """Ask Algolia for every value of the 'batch' facet (e.g. 'Winter 2012')."""
    res = algolia_query(session, key, "hitsPerPage=0&facets=%5B%22batch%22%5D&maxValuesPerFacet=1000")
    return sorted(res["facets"]["batch"].keys())


def scrape_official(key: str | None) -> list[dict]:
    s = requests.Session()
    key = key or get_algolia_key(s)
    batches = list_batches(s, key)
    print(f"{len(batches)} batches found")
    companies = {}
    for batch in batches:
        page = 0
        while True:
            ff = requests.utils.quote(json.dumps([[f"batch:{batch}"]]))
            res = algolia_query(s, key, f"hitsPerPage=1000&page={page}&facetFilters={ff}")
            for hit in res["hits"]:
                hit.pop("_highlightResult", None)
                companies[hit["id"]] = hit          # dedupe on id
            if page + 1 >= res.get("nbPages", 1):
                break
            page += 1
            time.sleep(0.3)
        print(f"  {batch:<14} {res['nbHits']:4d} companies")
        time.sleep(0.3)
    return list(companies.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", help="Algolia search key (optional, normally read from the page)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    data = scrape_official(args.key)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    meta = {"source": "official", "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"), "n": len(data)}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "companies": data}, f, ensure_ascii=False)
    print(f"Saved {len(data)} companies -> {args.out}")


if __name__ == "__main__":
    sys.exit(main())
