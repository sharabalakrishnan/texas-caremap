"""Shared helpers for the app's pages."""

import streamlit as st

from caremap import data as data_module
from caremap import gaps

# Sequential blue ramp (light -> dark) for maps of magnitude.
BLUE_RAMP = ["#dbe4f4", "#b3c6e8", "#86a4d8", "#5a80c4", "#335ea9", "#163f86", "#002868"]
# Politically neutral ramp for data maps: light lavender -> deep purple.
# (Red and blue county maps look like election maps, so data maps avoid them.)
GAP_RAMP = ["#bba6dc", "#a088cf", "#8669bf", "#6c4daa", "#53368e", "#3b236c"]
GAP_BAR = "#6c4daa"
BLUE = "#002868"   # Texas flag blue
RED = "#BF0A30"    # Texas flag red


@st.cache_resource(show_spinner="Loading Texas data...")
def get_data():
    return data_module.load()


@st.cache_data(show_spinner="Measuring distances across Texas...")
def get_county_table():
    d = get_data()
    return gaps.county_table(d.clinics, d.uninsured, d.zips)


def sample_banner(d) -> None:
    if d.using_sample:
        missing = [label for name, label in (("clinics_tx.csv", "clinic"), ("county_uninsured_tx.csv", "Census uninsured"))
                   if not (data_module.PROCESSED / name).exists()]
        st.error(
            f"**Sample data.** The {' and '.join(missing)} data shown is made up for testing. "
            "Run `python scripts/build_data.py` to download the real HRSA and Census data.",
            icon="⚠️",
        )


def data_date(d) -> str:
    built = d.metadata.get("built_at")
    return f"Data downloaded {built}." if built else ""
