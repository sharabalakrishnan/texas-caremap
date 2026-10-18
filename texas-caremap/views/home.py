"""Home: what the app does, in one screen."""

import streamlit as st

from views.common import get_county_table, get_data
from views.style import page_header

# Filled in by app.py so the tiles can link to the other pages.
PAGES: dict = {}

TILES = [
    ("find", "Near you", "Find a clinic",
     "Enter a ZIP code to see the closest community health centers, with hours and directions."),
    ("coverage", "In a minute", "Coverage guide",
     "Answer a few questions to see which programs, like Medicaid or CHIP, may fit your family."),
    ("gaps", "Statewide", "Texas access gaps",
     "A county-by-county map of where uninsured Texans live far from care."),
]


def render():
    d = get_data()
    table = get_county_table()

    page_header(
        "Texas CareMap",
        "Care is closer than you think.",
        "Community health centers see everyone, with or without insurance, and charge less "
        "when your income is low. Find one near you and the coverage that fits your family.",
    )

    cols = st.columns(3, gap="medium")
    for col, (key, kicker, title, body) in zip(cols, TILES):
        with col, st.container(border=True):
            st.markdown(
                f'<div class="tc-card tc-tile-kicker">{kicker}</div>'
                f'<div class="tc-tile-title">{title}</div>'
                f'<div class="tc-tile-body">{body}</div>',
                unsafe_allow_html=True,
            )
            if key in PAGES:
                st.page_link(PAGES[key], label="Open")

    st.write("")
    s1, s2, s3 = st.columns(3, gap="medium")
    no_site = int((table["sites"] == 0).sum())
    for col, value, label in (
        (s1, f"{len(d.clinics):,}", "community health center sites in Texas"),
        (s2, "16.7%", "of Texans were uninsured in 2024, the highest rate of any state"),
        (s3, f"{no_site}", f"of {len(table)} counties have no health center site"),
    ):
        col.markdown(f'<div class="tc-stat">{value}</div><div class="tc-stat-label">{label}</div>',
                     unsafe_allow_html=True)

    st.write("")
    st.caption("Sources: HRSA health center data and U.S. Census Bureau estimates. "
               "Uninsured rate from the 2024 American Community Survey. "
               "In an emergency, call 911. For a mental health crisis, call or text 988.")
