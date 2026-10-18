"""Make SAMPLE (made-up) clinic and uninsured files for testing.

These are NOT real clinics. They let the app and the tests run before the
real data has been downloaded with scripts/build_data.py. The app shows a
warning banner whenever it is using these files.
"""

import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "sample"
rng = random.Random(42)

zips = list(csv.DictReader(open(ROOT / "data/processed/tx_zips.csv", encoding="utf-8")))
geo = json.loads((ROOT / "data/processed/tx_counties.geojson").read_text(encoding="utf-8"))
counties = {f["id"]: f["properties"]["NAME"] for f in geo["features"]}
standard = [z for z in zips if z["zip_type"] == "STANDARD"]

OUT.mkdir(parents=True, exist_ok=True)
clinic_rows = []
for i in range(1, 161):
    z = rng.choice(standard)
    clinic_rows.append({
        "site_id": f"SAMPLE{i:04d}",
        "name": f"Sample Clinic {i:03d} (not real)",
        "organization": f"Sample Health Organization {rng.randint(1, 40)}",
        "address": f"{rng.randint(100, 9999)} Example St",
        "city": z["city"],
        "zip": z["zip"],
        "county": z["county"],
        "county_fips": z["county_fips"],
        "site_type": rng.choice(["Service Delivery Site"] * 6 + ["Mobile Van", "School-Based"]),
        "hours_per_week": rng.choice([20, 32, 40, 45, 50, 60]),
        "schedule": "Full-Time",
        "season": "Year-Round",
        "rural": rng.choice(["Y", "N", "N"]),
        "cong_district": str(rng.randint(1, 38)),
        "lat": round(float(z["lat"]) + rng.uniform(-0.03, 0.03), 5),
        "lon": round(float(z["lon"]) + rng.uniform(-0.03, 0.03), 5),
    })
with open(OUT / "clinics_tx.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(clinic_rows[0]))
    w.writeheader()
    w.writerows(clinic_rows)

unins_rows = []
for fips, name in sorted(counties.items()):
    pct = round(rng.uniform(9, 32), 1)
    unins_rows.append({
        "county_fips": fips, "county": name, "year": "SAMPLE",
        "uninsured_count": rng.randint(200, 90000), "uninsured_pct": pct,
        "uninsured_pct_moe": round(rng.uniform(0.6, 4.5), 1),
    })
with open(OUT / "county_uninsured_tx.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(unins_rows[0]))
    w.writeheader()
    w.writerows(unins_rows)

print(f"Wrote {len(clinic_rows)} sample clinics and {len(unins_rows)} sample counties to {OUT}")
