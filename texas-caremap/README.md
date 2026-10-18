# Texas CareMap

**Find a low-cost community health center near you, see which coverage programs may fit your family, and see where in Texas uninsured people live far from care.**

Texas has the highest uninsured rate of any state (16.7% in 2024, U.S. Census Bureau American Community Survey). Many uninsured Texans don't know that community health centers see everyone regardless of insurance, or that their children may qualify for free or low-cost coverage. Texas CareMap puts both answers in one place, and adds a statewide map that shows where the gaps are.

Built for the 2026 Congressional App Challenge.

---

## Features

| Screen | What it does |
|---|---|
| **Home** | A short overview with links to each tool and three headline numbers. |
| **Find a clinic** | Enter a ZIP code and travel distance. See the nearest federally funded health center sites on a map and as cards with distance, hours, and directions. Rural searches never come back empty: if nothing is in range, the closest sites are shown anyway. |
| **Coverage guide** | Answer a few questions (age, household size, income). The app compares your income to each program's published limit and sorts Medicaid, CHIP, Healthy Texas Women, the Marketplace, and Medicare into *worth applying*, *close to the limit*, and *probably not*. It flags Texas's coverage gap. It never claims to decide eligibility. |
| **Texas access gaps** | A county map and ranking built from an original **Access Gap Score** combining uninsured rate, distance to the nearest site, and sites per uninsured resident, with Census confidence intervals. Also counts sites by congressional district. |
| **About & privacy** | Data sources and dates, limits, and privacy. |

**Privacy:** no accounts, no tracking, nothing saved. All data is downloaded ahead of time, so ZIP codes and income answers are never sent to another service.

---

## Quick start

Requires Python 3.10 or newer.

```bash
pip install -r requirements.txt
python scripts/build_data.py      # downloads real HRSA + Census data (about 1 minute)
python -m pytest -q               # run the tests
streamlit run app.py              # open http://localhost:8501
```

Without step 2, the app still runs on made-up sample data and shows a red "Sample data" banner.

---

## How it works

### 1. Clinic search (`caremap/geo.py`, `caremap/clinics.py`)
- Each ZIP code is turned into a latitude/longitude using a ZIP centroid table.
- The **haversine formula** measures the great-circle distance from that point to every health center site at once (vectorized with NumPy).
- Results are filtered by radius, hours per week, and site type, then sorted by distance. If no site is inside the radius, the three closest are returned and flagged.

### 2. Coverage guide (`caremap/coverage.py`, `data/programs.json`)
- Income is converted to a **percentage of the federal poverty level** using the 2026 HHS poverty guidelines (\$15,960 for one person plus \$5,680 per additional person).
- A rules engine compares that percentage with each program's limit. Results within 10 points of a limit are labeled "close to the limit" because programs count income in their own ways (monthly income, deductions).
- Rules include: children's Medicaid limits that change with age, CHIP above Medicaid, Healthy Texas Women only for women 15-44 who aren't pregnant and aren't already on Medicaid or CHIP, Marketplace tax credits only from 100% to 400% FPL, and detection of Texas's coverage gap (adults under 100% FPL without children).
- All limits live in one JSON file with a source and review date, so they can be updated each January without touching code.

### 3. Access Gap Score (`caremap/gaps.py`)
For each of Texas's 254 counties:
1. **Percent uninsured** under 65 (Census SAHIE), with its 90% confidence interval.
2. **Distance to care**: the median, across the county's residential ZIP codes, of the distance to the nearest site.
3. **Supply**: sites per 10,000 uninsured residents.

Each measure becomes a percentile rank (0-100, pointed so 100 is worst), and the score is their average. Counties whose margin of error is more than a quarter of the estimate are flagged as less certain.

### 4. Offline county map (`caremap/county_map.py`)
Plotly's built-in geographic maps download a world outline from the internet each time they load, which fails on networks that block it. This app draws every county boundary as a filled shape on plain axes, groups counties into equal-count color classes, and corrects the east-west stretch for Texas's latitude, so the map works with no outside downloads.

---

## Data sources

| Data | Source |
|---|---|
| Health center sites | HRSA Health Center Locations map service (`gisportal.hrsa.gov`), official API |
| Uninsured estimates | U.S. Census Bureau, Small Area Health Insurance Estimates (SAHIE), newest year available |
| Poverty guidelines | U.S. Department of Health and Human Services, 2026 |
| Program income limits | Medicaid.gov eligibility levels (Texas); Texas Works Handbook W-110 (Healthy Texas Women); HealthCare.gov |
| ZIP code locations | `zipcodes` Python package |
| County boundaries | U.S. Census cartographic boundaries (via Plotly's public GeoJSON) |

---

## Project structure

```
app.py                  Streamlit entry point and navigation
views/                  One file per screen
caremap/
  geo.py                Haversine distance, ZIP lookup, nearest-site search
  clinics.py            Clinic search and labels
  coverage.py           Coverage rules engine
  gaps.py               County measures and Access Gap Score
  county_map.py         Offline county map
  data.py               Loads data files (falls back to sample data)
data/
  programs.json         Program rules, limits, sources, review date
  processed/            Real data built by scripts/build_data.py
  sample/               Made-up data for testing only
scripts/
  build_data.py         Downloads and cleans HRSA + Census data
  make_sample_data.py   Makes the sample data
tests/                  67 automated tests (pytest)
```

## Testing

```bash
python -m pytest -q
```

Tests cover distance math against known distances, ZIP input cleaning, search filters and the rural fallback, every coverage rule (including edge cases at each limit), the gap score, the data parsers, the offline map, and each app screen end to end.

## Limits

- The coverage guide is a guide, not an eligibility decision.
- Distances are straight-line, not driving.
- Clinic hours and services change; the app tells users to call first.
- The app does not give medical advice.
