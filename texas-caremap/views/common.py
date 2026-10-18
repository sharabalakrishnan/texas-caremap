"""Shared helpers for the app's pages."""

import streamlit as st

from caremap import data as data_module
from caremap import gaps

# Sequential blue ramp (light -> dark) for maps of magnitude.
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
BLUE = "#2a78d6"


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
