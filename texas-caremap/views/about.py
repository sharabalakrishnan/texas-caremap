"""Page 4: about the app, its data and privacy."""

import streamlit as st

from caremap import coverage
from views.common import get_data
from views.style import page_header, section


def render():
    d = get_data()
    cfg = coverage.load_programs()
    page_header("About", "About Texas CareMap.")
    st.write(
        "Texas has the highest uninsured rate of any state: 16.7% of residents had no health insurance "
        "in 2024 (U.S. Census Bureau, American Community Survey). Many people don't know that community "
        "health centers will see them regardless of insurance, or that their children may qualify for "
        "free or low-cost coverage. Texas CareMap puts both answers in one place."
    )

    section("What it does")
    st.markdown(
        """
- **Find a clinic**: enter a ZIP code to see the closest federally funded community health center sites.
- **Coverage guide**: answer a few questions to see which programs (Medicaid, CHIP, Healthy Texas Women,
  the Marketplace, Medicare) may be worth applying for.
- **Texas access gaps**: a county-by-county map of where uninsured people live far from care.
"""
    )

    section("Privacy")
    st.markdown(
        """
- No accounts, no sign-in, no tracking.
- ZIP codes and coverage answers are used only to show your results. They are not saved or sent anywhere.
- All clinic and Census data is downloaded ahead of time, so your answers are never sent to another service.
  The clinic map loads street map images from CARTO, which sees only the map area being viewed.
"""
    )

    section("Important limits")
    st.markdown(
        """
- The coverage guide is **not** an eligibility decision. Only the program can decide.
- Clinic hours and services change. Call before you go.
- Distances are straight-line, not driving distance.
- This app does not give medical advice. In an emergency, call 911. For a mental health crisis, call or text 988.
"""
    )

    section("Data sources")
    g = cfg["poverty_guidelines"]
    built = d.metadata.get("built_at", "not yet downloaded")
    st.markdown(
        f"""
| Data | Source | Date |
|---|---|---|
| Health center sites | Health Resources and Services Administration (HRSA), Health Center Locations | Downloaded {built} |
| Uninsured estimates | U.S. Census Bureau, Small Area Health Insurance Estimates | {d.metadata.get('sahie_year', '—')} estimates |
| Poverty guidelines | U.S. Department of Health and Human Services | {g['year']} |
| Program rules | Medicaid.gov eligibility levels, Texas Works Handbook, HealthCare.gov | Checked {cfg['last_reviewed']} |
| ZIP code locations | `zipcodes` Python package | — |
| County boundaries | U.S. Census cartographic boundaries (via Plotly) | — |
"""
    )
