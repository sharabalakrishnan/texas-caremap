"""Load the app's data files.

Real data lives in data/processed/ (built by scripts/build_data.py). If the
clinic or uninsured files haven't been built yet, the app falls back to the
small made-up files in data/sample/ and shows a warning, so it still runs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
SAMPLE = ROOT / "data" / "sample"


@dataclass
class AppData:
    clinics: pd.DataFrame
    uninsured: pd.DataFrame
    zips: pd.DataFrame
    counties_geojson: dict
    metadata: dict
    using_sample: bool


def _pick(name: str) -> tuple[Path, bool]:
    real = PROCESSED / name
    if real.exists():
        return real, False
    return SAMPLE / name, True


def load() -> AppData:
    clinics_path, sample_clinics = _pick("clinics_tx.csv")
    unins_path, sample_unins = _pick("county_uninsured_tx.csv")

    str_cols = {"zip": str, "county_fips": str, "site_id": str, "cong_district": str}
    clinics = pd.read_csv(clinics_path, dtype=str_cols, keep_default_na=False)
    clinics["lat"] = pd.to_numeric(clinics["lat"])
    clinics["lon"] = pd.to_numeric(clinics["lon"])

    uninsured = pd.read_csv(unins_path, dtype={"county_fips": str})
    zips = pd.read_csv(PROCESSED / "tx_zips.csv", dtype={"zip": str, "county_fips": str})
    geo = json.loads((PROCESSED / "tx_counties.geojson").read_text(encoding="utf-8"))
    meta_path = PROCESSED / "metadata.json"
    metadata = json.loads(meta_path.read_text()) if meta_path.exists() else {}

    return AppData(
        clinics=clinics, uninsured=uninsured, zips=zips, counties_geojson=geo,
        metadata=metadata, using_sample=sample_clinics or sample_unins,
    )
