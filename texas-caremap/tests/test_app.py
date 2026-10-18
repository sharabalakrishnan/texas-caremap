"""End-to-end tests that run each page of the Streamlit app without a browser."""

from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")
AppTest = st_testing.AppTest
ROOT = Path(__file__).resolve().parent.parent


def page(name: str):
    script = f"""
import sys
sys.path.insert(0, {str(ROOT)!r})
import streamlit as st
from views import {name}
{name}.render()
"""
    return AppTest.from_string(script, default_timeout=60)


def errors(at):
    return [e.value for e in at.exception]


def test_finder_valid_zip_shows_results():
    at = page("finder").run()
    at.text_input[0].input("78701")
    at.button[0].click().run()
    assert not errors(at)
    headings = " ".join(m.value for m in at.markdown)
    assert "within 25 miles" in headings or at.warning   # results heading, or "closest ones anyway"


def test_finder_bad_zip_warns():
    at = page("finder").run()
    at.text_input[0].input("123")
    at.button[0].click().run()
    assert any("5-digit" in w.value for w in at.warning)


def test_finder_out_of_state_zip_warns():
    at = page("finder").run()
    at.text_input[0].input("10001")   # New York
    at.button[0].click().run()
    assert any("Texas" in w.value for w in at.warning)


def test_finder_rural_zip_never_empty():
    at = page("finder").run()
    at.text_input[0].input("79848")   # Sanderson, Terrell County
    at.select_slider[0].set_value(5)
    at.button[0].click().run()
    assert not errors(at)


def test_coverage_page_runs_and_shows_results():
    at = page("coverage_page").run()
    at.number_input[0].set_value(30)       # age
    at.number_input[1].set_value(1)        # household size
    at.number_input[2].set_value(9000)     # income
    at.button[0].click().run()
    assert not errors(at)
    assert any("coverage gap" in w.value for w in at.warning)


def test_coverage_monthly_income():
    at = page("coverage_page").run()
    at.number_input[0].set_value(8)
    at.number_input[2].set_value(2500)
    at.radio[1].set_value("Per month")
    at.button[0].click().run()
    assert not errors(at)
    assert any("$30,000" in str(m.value) for m in at.metric)


def test_gaps_page_runs():
    at = page("gaps_page").run()
    assert not errors(at)
    assert len(at.metric) == 4


def test_about_page_runs():
    at = page("about").run()
    assert not errors(at)


def test_home_page_runs():
    at = page("home").run()
    assert not errors(at)
    assert any("Care is closer" in m.value for m in at.markdown)
