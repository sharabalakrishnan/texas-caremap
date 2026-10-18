"""Build the data files Texas CareMap needs.

Run from the project folder:

    python scripts/build_data.py            # build everything
    python scripts/build_data.py --only clinics uninsured

Sources (all public, no API key needed):
  * Health center sites  - HRSA Health Center Locations map service (official HRSA ArcGIS API)
  * Uninsured estimates  - U.S. Census Bureau Small Area Health Insurance Estimates (SAHIE)
  * ZIP code centroids   - the `zipcodes` Python package (offline)
  * County boundaries    - Plotly's public US county GeoJSON (Census cartographic boundaries)

Outputs go to data/processed/. The app reads only those files, so it never
calls an outside service while someone is using it.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed"

HRSA_LAYER = (
    "https://gisportal.hrsa.gov/server/rest/services/udsmapper/"
    "HealthCenterLocations/MapServer/0/query"
)
SAHIE_URL = (
    "https://www2.census.gov/programs-surveys/sahie/datasets/time-series/"
    "estimates-acs/sahie-{year}-csv.zip"
)
COUNTY_GEOJSON = (
    "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
)
TX_FIPS = "48"
# Rough bounding box for Texas, used to throw out bad coordinates.
TX_BOUNDS = {"lat": (25.5, 36.7), "lon": (-106.8, -93.3)}
USER_AGENT = "TexasCareMap/1.0 (student project; data build script)"


def fetch(url: str, retries: int = 3) -> bytes:
    """Download a URL, retrying a few times on network hiccups."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - report any network failure
            last_error = exc
            print(f"  attempt {attempt} failed: {exc}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"Could not download {url}: {last_error}")


def in_texas(lat: float, lon: float) -> bool:
    return (
        TX_BOUNDS["lat"][0] <= lat <= TX_BOUNDS["lat"][1]
        and TX_BOUNDS["lon"][0] <= lon <= TX_BOUNDS["lon"][1]
    )


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {len(rows):,} rows -> {path.relative_to(ROOT)}")


# --------------------------------------------------------------------------
# County boundaries (also gives us the official county name -> FIPS lookup)
# --------------------------------------------------------------------------
def build_counties() -> dict:
    print("County boundaries")
    data = json.loads(fetch(COUNTY_GEOJSON))
    features = [f for f in data["features"] if f["properties"]["STATE"] == TX_FIPS]
    geo = {"type": "FeatureCollection", "features": features}
    path = OUT / "tx_counties.geojson"
    path.write_text(json.dumps(geo, separators=(",", ":")), encoding="utf-8")
    print(f"  wrote {len(features)} counties -> {path.relative_to(ROOT)}")
    if len(features) != 254:
        print("  WARNING: Texas has 254 counties; check the boundary file.")
    return geo


def county_lookup() -> dict[str, str]:
    """Map a normalized county name ('el paso') to its 5-digit FIPS code."""
    path = OUT / "tx_counties.geojson"
    if not path.exists():
        build_counties()
    geo = json.loads(path.read_text(encoding="utf-8"))
    return {
        normalize_county(f["properties"]["NAME"]): f["id"] for f in geo["features"]
    }


def normalize_county(name: str) -> str:
    name = (name or "").strip().lower()
    for suffix in (" county", " parish"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.replace(".", "").replace(" ", "")


# --------------------------------------------------------------------------
# ZIP code centroids
# --------------------------------------------------------------------------
def point_in_ring(lat: float, lon: float, ring: list) -> bool:
    """Ray-casting test: is the point inside this polygon ring of [lon, lat] pairs?"""
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def county_for_point(lat: float, lon: float, geo: dict) -> str:
    """Return the FIPS code of the county containing a point, or '' if none."""
    for feat in geo["features"]:
        geom = feat["geometry"]
        polygons = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polygons:
            if point_in_ring(lat, lon, poly[0]) and not any(point_in_ring(lat, lon, hole) for hole in poly[1:]):
                return feat["id"]
    return ""


def build_zips() -> None:
    print("ZIP code centroids")
    try:
        import zipcodes  # offline package
    except ImportError:
        raise SystemExit(
            "The 'zipcodes' package isn't installed for this Python.\n"
            f"Install it with:  {sys.executable} -m pip install zipcodes"
        )

    fips = county_lookup()
    geo = json.loads((OUT / "tx_counties.geojson").read_text(encoding="utf-8"))
    by_fips = {f["id"]: f["properties"]["NAME"] for f in geo["features"]}
    rows = []
    for z in zipcodes.filter_by(state="TX"):
        try:
            lat, lon = float(z["lat"]), float(z["long"])
        except (TypeError, ValueError):
            continue
        if not in_texas(lat, lon):
            continue
        code = fips.get(normalize_county(z["county"])) or county_for_point(lat, lon, geo)
        rows.append(
            {
                "zip": z["zip_code"],
                "city": z["city"],
                "county": by_fips.get(code, z["county"].replace(" County", "")),
                "county_fips": code,
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "zip_type": z["zip_code_type"],
            }
        )
    write_csv(OUT / "tx_zips.csv", rows, list(rows[0].keys()))


# --------------------------------------------------------------------------
# HRSA health center service delivery sites
# --------------------------------------------------------------------------
HRSA_FIELDS = [
    "SITE_NM", "SITE_ADDRESS", "SITE_CITY", "SITE_ZIP_CD", "SITE_STATE_ABBR",
    "COUNTY_NM", "HCC_TYP_DESC", "TOT_OPER_HR_PER_WEEK", "HCC_OPER_SCHD_DESC",
    "HCC_CLND_SCHD_DIM_DESC", "GRANTEE_NM", "RURAL_IND", "CONG_DIST_NUM",
    "CONG_DIST_NM", "BPHC_SITE_NUM", "X", "Y",
]


def build_clinics(page_size: int = 1000) -> None:
    print("Health center sites (HRSA)")
    fips = county_lookup()
    features, offset = [], 0
    while True:
        params = {
            "where": "SITE_STATE_ABBR='TX'",
            "outFields": ",".join(HRSA_FIELDS),
            "outSR": "4326",
            "returnGeometry": "true",
            "orderByFields": "OBJECTID",
            "resultOffset": str(offset),
            "resultRecordCount": str(page_size),
            "f": "json",
        }
        url = HRSA_LAYER + "?" + urllib.parse.urlencode(params)
        page = json.loads(fetch(url))
        if "error" in page:
            raise RuntimeError(f"HRSA service error: {page['error']}")
        batch = page.get("features", [])
        features.extend(batch)
        print(f"  fetched {len(features):,} sites so far")
        if not batch or not page.get("exceededTransferLimit"):
            break
        offset += len(batch)

    rows, seen, dropped = [], set(), 0
    for feat in features:
        a = feat.get("attributes", {})
        g = feat.get("geometry") or {}
        lon = g.get("x", a.get("X"))
        lat = g.get("y", a.get("Y"))
        try:
            lat, lon = float(lat), float(lon)
        except (TypeError, ValueError):
            dropped += 1
            continue
        if not in_texas(lat, lon):
            dropped += 1
            continue
        key = (str(a.get("SITE_NM", "")).strip().lower(), str(a.get("SITE_ADDRESS", "")).strip().lower())
        if key in seen:  # the same site can appear under more than one grant
            continue
        seen.add(key)
        county = str(a.get("COUNTY_NM") or "").strip()
        hours = a.get("TOT_OPER_HR_PER_WEEK")
        rows.append(
            {
                "site_id": a.get("BPHC_SITE_NUM") or "",
                "name": str(a.get("SITE_NM") or "").strip(),
                "organization": str(a.get("GRANTEE_NM") or "").strip(),
                "address": str(a.get("SITE_ADDRESS") or "").strip(),
                "city": str(a.get("SITE_CITY") or "").strip(),
                "zip": str(a.get("SITE_ZIP_CD") or "").strip()[:5],
                "county": county.replace(" County", ""),
                "county_fips": fips.get(normalize_county(county), ""),
                "site_type": str(a.get("HCC_TYP_DESC") or "").strip(),
                "hours_per_week": "" if hours in (None, "") else hours,
                "schedule": str(a.get("HCC_OPER_SCHD_DESC") or "").strip(),
                "season": str(a.get("HCC_CLND_SCHD_DIM_DESC") or "").strip(),
                "rural": str(a.get("RURAL_IND") or "").strip(),
                "cong_district": str(a.get("CONG_DIST_NUM") or "").strip(),
                "lat": round(lat, 6),
                "lon": round(lon, 6),
            }
        )
    if not rows:
        raise RuntimeError("No Texas health center sites were returned.")
    print(f"  kept {len(rows):,} unique sites, dropped {dropped} with bad coordinates")
    missing = sum(1 for r in rows if not r["county_fips"])
    if missing:
        print(f"  note: {missing} sites have a county name that did not match a FIPS code")
    write_csv(OUT / "clinics_tx.csv", rows, list(rows[0].keys()))


# --------------------------------------------------------------------------
# Census SAHIE uninsured estimates (county level, all ages under 65)
# --------------------------------------------------------------------------
def build_uninsured(year: int | None = None) -> int:
    print("Uninsured estimates (Census SAHIE)")
    years = [year] if year else list(range(datetime.now().year - 1, 2019, -1))
    raw, used_year = None, None
    for y in years:
        try:
            raw = fetch(SAHIE_URL.format(year=y), retries=1)
            used_year = y
            break
        except RuntimeError:
            print(f"  {y} file not available, trying an earlier year")
    if raw is None:
        raise RuntimeError("Could not download any SAHIE file.")

    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        name = next(n for n in zf.namelist() if n.lower().endswith(".csv"))
        text = zf.read(name).decode("latin-1")

    rows = parse_sahie(text)
    write_csv(OUT / "county_uninsured_tx.csv", rows, list(rows[0].keys()))
    print(f"  using {used_year} estimates")
    return used_year


def parse_sahie(text: str) -> list[dict]:
    """Pull the Texas county rows (all ages under 65, all incomes) out of a SAHIE CSV.

    SAHIE files start with several lines of notes before the header row, and
    values are padded with spaces, so we search for the header and strip
    everything.
    """
    lines = text.splitlines()

    def is_header(line: str) -> bool:
        # The notes at the top describe each column ("statefips   2 unique fips code..."),
        # so the real header is the comma-separated line whose fields include these names.
        fields = {f.strip().strip('"').lower() for f in line.split(",")}
        return {"statefips", "countyfips", "geocat"} <= fields

    start = next((i for i, ln in enumerate(lines) if is_header(ln)), None)
    if start is None:
        preview = "\n".join(lines[:15])
        raise RuntimeError(
            "Could not find the column header row in the SAHIE file. First lines were:\n" + preview
        )
    reader = csv.DictReader(lines[start:])
    reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
    needed = {"statefips", "countyfips", "geocat", "agecat", "racecat", "sexcat", "iprcat", "nui", "pctui"}
    missing = needed - set(reader.fieldnames)
    if missing:
        raise RuntimeError(
            f"SAHIE file layout changed. Missing columns: {sorted(missing)}. "
            f"Columns found: {reader.fieldnames}"
        )

    def num(value):
        value = (value or "").strip()
        try:
            return float(value)
        except ValueError:
            return None

    rows = []
    for r in reader:
        r = {k: (v or "").strip() for k, v in r.items() if k}
        if r.get("statefips", "").zfill(2) != TX_FIPS:
            continue
        if r.get("geocat") != "50":  # 50 = county, 40 = state
            continue
        if any(r.get(k) != "0" for k in ("agecat", "racecat", "sexcat", "iprcat")):
            continue
        pct, moe = num(r.get("pctui")), num(r.get("pctui_moe"))
        nui = num(r.get("nui"))
        if pct is None or nui is None:
            continue
        rows.append(
            {
                "county_fips": TX_FIPS + r["countyfips"].zfill(3),
                "county": r.get("county_name", "").replace(" County", ""),
                "year": r.get("year", ""),
                "uninsured_count": int(nui),
                "uninsured_pct": pct,
                "uninsured_pct_moe": moe if moe is not None else "",
            }
        )
    if len(rows) < 250:
        raise RuntimeError(f"Expected 254 Texas counties in SAHIE file, found {len(rows)}.")
    return rows


# --------------------------------------------------------------------------
def write_metadata(sahie_year: int | None) -> None:
    meta_path = OUT / "metadata.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    meta["built_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if sahie_year:
        meta["sahie_year"] = sahie_year
    meta["sources"] = {
        "clinics": "HRSA Health Center Locations map service (gisportal.hrsa.gov)",
        "uninsured": "U.S. Census Bureau, Small Area Health Insurance Estimates (SAHIE)",
        "zips": "zipcodes Python package (ZIP code centroids)",
        "counties": "Plotly US county GeoJSON (Census cartographic boundaries)",
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


STEPS = ["counties", "zips", "clinics", "uninsured"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", nargs="+", choices=STEPS, help="build only these pieces")
    parser.add_argument("--sahie-year", type=int, help="force a SAHIE year (default: newest available)")
    parser.add_argument("--all", action="store_true",
                        help="also rebuild the ZIP and county files (they ship with the project)")
    args = parser.parse_args(argv)
    if args.only:
        steps = args.only
    elif args.all:
        steps = STEPS
    else:
        # The ZIP and county files are included with the project, so normally
        # only the clinic and Census data need downloading. Rebuild any that are missing.
        steps = ["clinics", "uninsured"]
        if not (OUT / "tx_counties.geojson").exists():
            steps.insert(0, "counties")
        if not (OUT / "tx_zips.csv").exists():
            steps.insert(1 if "counties" in steps else 0, "zips")
    OUT.mkdir(parents=True, exist_ok=True)

    sahie_year = None
    if "counties" in steps:
        build_counties()
    if "zips" in steps:
        build_zips()
    if "clinics" in steps:
        build_clinics()
    if "uninsured" in steps:
        sahie_year = build_uninsured(args.sahie_year)
    write_metadata(sahie_year)
    print("Done. Start the app with:  streamlit run app.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
