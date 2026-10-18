"""Texas access gaps: where are uninsured people far from a community health center?

For every county we compute three measures:

  1. uninsured_pct          - share of people under 65 without insurance (Census SAHIE),
                              with its 90% confidence interval
  2. median_miles           - typical straight-line distance from a ZIP code in the
                              county to the nearest health center site
  3. sites_per_10k          - health center sites per 10,000 uninsured residents

The Access Gap Score (0-100) averages each county's percentile rank on the three
measures, oriented so that 100 means "worst access" on all three. Percentile
ranks keep one measure with big numbers (like distance) from drowning out the
others, and they are easy to explain: a score of 90 means the county is worse
off than about 90% of Texas counties on average.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .geo import nearest_distance

# ZIP types that stand for places people live (UNIQUE ZIPs are single big
# businesses or agencies, like the IRS center in Austin).
RESIDENTIAL_ZIP_TYPES = {"STANDARD", "PO BOX"}


def zip_distances(zips: pd.DataFrame, clinics: pd.DataFrame) -> pd.DataFrame:
    """Each residential ZIP code with the distance to its nearest health center site."""
    z = zips[zips["zip_type"].isin(RESIDENTIAL_ZIP_TYPES)].copy()
    z["nearest_miles"] = nearest_distance(z["lat"], z["lon"], clinics["lat"], clinics["lon"])
    return z


def percentile_rank(values: pd.Series, higher_is_worse: bool = True) -> pd.Series:
    """Percentile rank from 0 to 100. Ties share the average rank."""
    ranked = values.rank(pct=True, method="average")
    if not higher_is_worse:
        ranked = values.mul(-1).rank(pct=True, method="average")
    return ranked * 100


def county_table(clinics: pd.DataFrame, uninsured: pd.DataFrame, zips: pd.DataFrame) -> pd.DataFrame:
    """One row per county with the three measures and the Access Gap Score."""
    unins = uninsured.copy()
    unins["county_fips"] = unins["county_fips"].astype(str).str.zfill(5)

    sites = (
        clinics.assign(county_fips=clinics["county_fips"].astype(str).str.zfill(5))
        .groupby("county_fips").size().rename("sites")
    )
    dist = zip_distances(zips, clinics)
    dist["county_fips"] = dist["county_fips"].astype(str).str.zfill(5)
    miles = dist.groupby("county_fips")["nearest_miles"].median().rename("median_miles")

    t = unins.set_index("county_fips").join(sites).join(miles)
    t["sites"] = t["sites"].fillna(0).astype(int)
    t["sites_per_10k"] = np.where(
        t["uninsured_count"] > 0, t["sites"] / t["uninsured_count"] * 10_000, np.nan
    )

    moe = pd.to_numeric(t.get("uninsured_pct_moe"), errors="coerce")
    t["ci_low"] = (t["uninsured_pct"] - moe).clip(lower=0)
    t["ci_high"] = t["uninsured_pct"] + moe
    # Flag estimates whose 90% interval is wide compared to the estimate itself.
    t["less_certain"] = moe > 0.25 * t["uninsured_pct"]

    parts = pd.DataFrame({
        "rate": percentile_rank(t["uninsured_pct"], higher_is_worse=True),
        "distance": percentile_rank(t["median_miles"], higher_is_worse=True),
        "supply": percentile_rank(t["sites_per_10k"], higher_is_worse=False),
    })
    t["gap_score"] = parts.mean(axis=1, skipna=True).round(1)
    t = t.join(parts.add_prefix("rank_"))
    return t.reset_index().sort_values("gap_score", ascending=False, kind="mergesort").reset_index(drop=True)


def state_summary(table: pd.DataFrame, clinics: pd.DataFrame) -> dict:
    """Headline numbers for the whole state."""
    no_site = table[table["sites"] == 0]
    total_uninsured = table["uninsured_count"].sum()
    return {
        "sites": int(len(clinics)),
        "counties": int(len(table)),
        "counties_without_site": int(len(no_site)),
        "uninsured_total": int(total_uninsured),
        "uninsured_in_counties_without_site": int(no_site["uninsured_count"].sum()),
        "share_uninsured_without_site": float(no_site["uninsured_count"].sum() / total_uninsured) if total_uninsured else 0.0,
        "median_county_miles": float(table["median_miles"].median()),
    }


def district_table(clinics: pd.DataFrame) -> pd.DataFrame:
    """Health center sites in each Texas congressional district."""
    d = clinics.copy()
    d["cong_district"] = pd.to_numeric(d["cong_district"], errors="coerce")
    d = d.dropna(subset=["cong_district"])
    out = d.groupby("cong_district").agg(
        sites=("name", "size"),
        organizations=("organization", "nunique"),
        rural_sites=("rural", lambda s: int((s.astype(str).str.upper() == "Y").sum())),
    )
    out.index = out.index.astype(int)
    return out.reset_index().rename(columns={"cong_district": "district"})
