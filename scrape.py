import requests
import pandas as pd
import time
import urllib.parse

# Același link
FULL_URL = "https://45bwzj1sgc-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%3B%20JS%20Helper%20(3.16.1)&x-algolia-application-id=45BWZJ1SGC&x-algolia-api-key=YjI3MGU0ZDk2YTgzYmRkYWRlMjIyMjU4NTlmZWVlN2FjN2EzNzA1MjhhZDEyMjdjZWFkMjVlODBhNWI4ZGY3NGFuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3Byb2R1Y3Rpb24lMkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZXJzPSU1QiUyMnljZGNfcHVibGljJTIyJTVEJnZhbGlkVW50aWw9MTc5MjA5NjgyNA%3D%3D"

headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.ycombinator.com",
    "referer": "https://www.ycombinator.com/"
}

# Generăm numele CORECTE ale cohortelor: "Winter 2005", "Summer 2005", etc.
batches = []
for year in range(2005, 2020): # Anii 2005 până la 2019
    batches.extend([f"Winter {year}", f"Summer {year}"])

all_companies = []

for batch in batches:
    print(f"\nCaut companii pentru cohorta: {batch}...")

    # Nicio cohortă din anii aceia nu are mai mult de 200 de companii
    # Așa că iterăm doar 3 pagini (300 companii) pentru fiecare cohortă
    for page_num in range(0, 3):
        # Formatul corect dedus din JSON-ul tău!
        facet_filter = urllib.parse.quote(f'[["batch:{batch}"]]')

        payload = {
            "requests": [
                {
                    "indexName": "YCCompany_production", # Folosim indexul standard
                    "params": f"hitsPerPage=100&page={page_num}&facetFilters={facet_filter}"
                }
            ]
        }

        response = requests.post(FULL_URL, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            hits = data['results'][0]['hits']

            if not hits:
                break # Pagina e goală, trecem la următoarea cohortă

            for company in hits:
                # Extragem în siguranță listele și textele pentru a evita erorile
                tags = company.get("tags") or []
                founders = company.get("founders") or []
                desc = company.get("long_description") or ""
                regions = company.get("regions") or ["Unknown"]

                company_data = {
                    # --- Identificatori (Nu se folosesc la predicție, doar pentru referință) ---
                    "id": company.get("id"),
                    "name": company.get("name"),

                    # --- TARGET VARIABLE ---
                    "status": company.get("status"),

                    # --- Date Categorice Principale ---
                    "batch": company.get("batch_name", "Unknown"),
                    "industry": company.get("industry", "Unknown"),
                    "subindustry": company.get("subindustry", "Unknown"),
                    # Folosim prima regiune din listă (mult mai valid decât location care e gol la anii vechi)
                    "region": regions[0],

                    # --- Date Numerice ---
                    "team_size": company.get("team_size") or 1,
                    "founders_count": len(founders), # Câți fondatori sunt declarați
                    "tags_count": len(tags),
                    "description_length": len(desc),
                    "name_length": len(company.get("name", "")),

                    # --- Booleane Directe (din atributele descoperite de tine) ---
                    "is_hiring": 1 if company.get("isHiring") else 0,
                    "is_nonprofit": 1 if company.get("nonprofit") else 0,
                    "is_top_company": 1 if company.get("top_company") else 0,
                    "is_remote": 1 if company.get("is_remote") else 0,
                    "has_app_video": 1 if company.get("app_video_public") else 0,
                    "has_demo_day_video": 1 if company.get("demo_day_video_public") else 0,
                    "has_app_answers": 1 if company.get("app_answers") else 0,
                    "has_question_answers": 1 if company.get("question_answers") else 0,

                    # --- Prezență Online / Social Media (Missingness ca semnal) ---
                    "has_website": 1 if company.get("website") else 0,
                    "has_linkedin": 1 if company.get("linkedin_url") else 0,
                    "has_twitter": 1 if company.get("twitter_url") else 0,
                    "has_crunchbase": 1 if company.get("cb_url") else 0,
                    "has_github": 1 if company.get("github_url") else 0,

                    # --- Atribute derivate suplimentare (Feature Engineering) ---
                    "is_b2b": 1 if company.get("industry") == "B2B" else 0,
                    "has_co_founders": 1 if len(founders) > 1 else 0
                }
                all_companies.append(company_data)
        else:
            print(f"Eroare: {response.status_code}")
            break

        time.sleep(0.5)

# Salvăm
df = pd.DataFrame(all_companies)

if not df.empty:
    df.to_csv("ycombinator_mature_dataset.csv", index=False)
    print(f"\nScraping complet! S-au extras {len(df)} companii mature.")
    print("\nDistribuția variabilei țintă (Status):")
    print(df['status'].value_counts())
else:
    print("\nNu s-a putut extrage nicio companie.")