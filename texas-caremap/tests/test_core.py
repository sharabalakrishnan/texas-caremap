"""Tests for distance math, clinic search, the coverage guide and the gap score.

Run with:  python -m pytest -q
"""

import math

import pandas as pd
import pytest

from caremap import clinics, coverage, gaps, geo

G2026 = {"base": 15960, "per_additional_person": 5680}


# ---------------------------------------------------------------- geo
def test_haversine_zero_distance():
    assert geo.haversine_miles(30.0, -97.0, 30.0, -97.0) == pytest.approx(0.0)


def test_haversine_austin_to_houston():
    # Downtown Austin to downtown Houston is about 146 miles in a straight line.
    d = geo.haversine_miles(30.2672, -97.7431, 29.7604, -95.3698)
    assert 140 < d < 152


def test_haversine_one_degree_latitude():
    # One degree of latitude is about 69 miles anywhere on Earth.
    assert geo.haversine_miles(30, -97, 31, -97) == pytest.approx(69.1, abs=0.2)


def test_haversine_is_symmetric_and_vectorized():
    a = geo.haversine_miles(30, -97, [31, 29], [-97, -96])
    b = geo.haversine_miles([31, 29], [-97, -96], 30, -97)
    assert list(a) == pytest.approx(list(b))


@pytest.mark.parametrize("raw,expected", [
    ("78701", "78701"), (" 78701 ", "78701"), ("78701-1234", "78701"),
    ("787011234", "78701"), ("7870", None), ("abcde", None), ("", None), (None, None),
])
def test_clean_zip(raw, expected):
    assert geo.clean_zip(raw) == expected


def test_nearest_distance_picks_closest():
    d = geo.nearest_distance([30.0], [-97.0], [30.0, 35.0], [-97.1, -97.0])
    assert d[0] == pytest.approx(geo.haversine_miles(30, -97, 30, -97.1))


# ---------------------------------------------------------------- clinic search
@pytest.fixture
def sample_clinics():
    return pd.DataFrame({
        "name": ["Near", "Middle", "Far", "Part-time"],
        "lat": [30.27, 30.40, 31.50, 30.28],
        "lon": [-97.74, -97.74, -97.74, -97.74],
        "hours_per_week": ["40", "50", "45", "10"],
        "site_type": ["Service Delivery Site", "Mobile Van", "Service Delivery Site", "Service Delivery Site"],
    })


def test_search_sorts_by_distance(sample_clinics):
    r = clinics.search(sample_clinics, 30.27, -97.74, radius_miles=200)
    assert list(r["name"]) == ["Near", "Part-time", "Middle", "Far"]
    assert r["distance_miles"].is_monotonic_increasing


def test_search_radius(sample_clinics):
    r = clinics.search(sample_clinics, 30.27, -97.74, radius_miles=15)
    assert "Far" not in set(r["name"])
    assert not r["outside_radius"].any()


def test_search_min_hours_and_type_filters(sample_clinics):
    r = clinics.search(sample_clinics, 30.27, -97.74, radius_miles=200, min_hours=40)
    assert "Part-time" not in set(r["name"])
    r = clinics.search(sample_clinics, 30.27, -97.74, radius_miles=200, site_types=["Mobile Van"])
    assert list(r["name"]) == ["Middle"]


def test_search_never_empty_when_nothing_in_radius(sample_clinics):
    r = clinics.search(sample_clinics, 26.0, -106.0, radius_miles=5)
    assert len(r) == 3
    assert r["outside_radius"].all()


def test_labels():
    assert clinics.distance_label(0.05) == "Less than 0.1 mi"
    assert clinics.distance_label(3.456) == "3.5 mi"
    assert clinics.distance_label(42.4) == "42 mi"
    assert clinics.hours_label("") == "Hours not listed"
    assert clinics.hours_label("40") == "Open about 40 hours a week"


def test_directions_url_is_encoded():
    url = clinics.directions_url({"address": "1700 Golden Ave", "city": "Bay City", "zip": "77414"})
    assert url.startswith("https://www.google.com/maps/dir/?api=1&destination=")
    assert " " not in url


# ---------------------------------------------------------------- coverage
def test_poverty_line_2026():
    assert coverage.poverty_line(1, G2026) == 15960
    assert coverage.poverty_line(4, G2026) == 33000
    assert coverage.poverty_line(8, G2026) == 55720


def test_fpl_percent():
    assert coverage.fpl_percent(33000, 4, G2026) == pytest.approx(100.0)
    assert coverage.fpl_percent(66000, 4, G2026) == pytest.approx(200.0)


def test_bad_inputs_raise():
    with pytest.raises(ValueError):
        coverage.fpl_percent(-1, 2, G2026)
    with pytest.raises(ValueError):
        coverage.poverty_line(0, G2026)


@pytest.mark.parametrize("fpl,limit,expected", [
    (100, 133, coverage.LIKELY), (125, 133, coverage.CHECK), (143, 133, coverage.CHECK),
    (144, 133, coverage.UNLIKELY),
])
def test_compare_to_limit_bands(fpl, limit, expected):
    assert coverage.compare_to_limit(fpl, limit) == expected


def statuses(g):
    return {s.key: s.status for s in g.suggestions}


def test_low_income_child_gets_medicaid_not_chip():
    g = coverage.guide(coverage.Household(age=8, household_size=4, yearly_income=30000))
    s = statuses(g)
    assert s["children_medicaid"] == coverage.LIKELY
    assert s["chip"] == coverage.UNLIKELY


def test_middle_income_child_gets_chip():
    # 180% FPL for a family of 4 is above children's Medicaid (133%) but under CHIP (201%).
    g = coverage.guide(coverage.Household(age=10, household_size=4, yearly_income=33000 * 1.8))
    s = statuses(g)
    assert s["children_medicaid"] == coverage.UNLIKELY
    assert s["chip"] == coverage.LIKELY


def test_infant_has_higher_medicaid_limit():
    income = 33000 * 1.7  # 170% FPL
    baby = statuses(coverage.guide(coverage.Household(age=0, household_size=4, yearly_income=income)))
    teen = statuses(coverage.guide(coverage.Household(age=15, household_size=4, yearly_income=income)))
    assert baby["children_medicaid"] == coverage.LIKELY
    assert teen["children_medicaid"] == coverage.UNLIKELY


def test_childless_adult_below_poverty_is_in_coverage_gap():
    g = coverage.guide(coverage.Household(age=30, household_size=1, yearly_income=9000))
    assert g.coverage_gap
    assert statuses(g)["marketplace"] == coverage.UNLIKELY
    assert statuses(g)["health_centers"] == coverage.LIKELY


def test_adult_in_subsidy_range():
    g = coverage.guide(coverage.Household(age=30, household_size=1, yearly_income=30000))
    assert not g.coverage_gap
    assert statuses(g)["marketplace"] == coverage.LIKELY


def test_job_coverage_blocks_marketplace_credits():
    g = coverage.guide(coverage.Household(age=30, household_size=1, yearly_income=30000, has_job_coverage=True))
    assert statuses(g)["marketplace"] == coverage.UNLIKELY


def test_pregnancy_and_htw():
    preg = statuses(coverage.guide(coverage.Household(age=25, household_size=2, yearly_income=30000,
                                                      pregnant=True, female=True)))
    assert preg["pregnancy_medicaid"] == coverage.LIKELY
    assert preg["healthy_texas_women"] == coverage.UNLIKELY
    htw = statuses(coverage.guide(coverage.Household(age=25, household_size=2, yearly_income=30000, female=True)))
    assert htw["healthy_texas_women"] == coverage.LIKELY


def test_htw_teen_note_and_age_limits():
    g = coverage.guide(coverage.Household(age=16, household_size=3, yearly_income=27320 * 2.03, female=True))
    assert "healthy_texas_women" in statuses(g)
    assert any("parent or guardian" in n for n in g.notes)
    older = coverage.guide(coverage.Household(age=50, household_size=1, yearly_income=10000, female=True))
    assert "healthy_texas_women" not in statuses(older)


def test_senior_gets_medicare():
    g = coverage.guide(coverage.Household(age=70, household_size=2, yearly_income=40000))
    assert statuses(g)["medicare"] == coverage.LIKELY
    assert "marketplace" not in statuses(g)


def test_health_centers_always_listed_and_sorted_last_among_likely():
    g = coverage.guide(coverage.Household(age=8, household_size=4, yearly_income=30000))
    likely = [s.key for s in g.by_status(coverage.LIKELY)]
    assert likely[-1] == "health_centers"


def test_limit_income_matches_threshold():
    g = coverage.guide(coverage.Household(age=10, household_size=4, yearly_income=30000))
    med = next(s for s in g.suggestions if s.key == "children_medicaid")
    assert med.limit_income == pytest.approx(33000 * 1.33)


def test_programs_file_is_consistent():
    cfg = coverage.load_programs()
    g = cfg["poverty_guidelines"]
    assert g["year"] >= 2026
    for key in ("children_medicaid", "chip", "pregnancy_medicaid", "healthy_texas_women",
                "parent_medicaid", "marketplace", "medicare", "health_centers"):
        p = cfg["programs"][key]
        assert p["name"] and p.get("info_url", "").startswith("https://")


# ---------------------------------------------------------------- gaps
def test_percentile_rank_direction():
    s = pd.Series([1, 2, 3, 4])
    assert list(gaps.percentile_rank(s, True)) == [25, 50, 75, 100]
    assert list(gaps.percentile_rank(s, False)) == [100, 75, 50, 25]


def test_county_table_scores_worst_county_highest():
    clin = pd.DataFrame({"county_fips": ["48001", "48001", "48003"], "lat": [31.0, 31.01, 32.0],
                         "lon": [-95.0, -95.01, -102.0], "name": ["a", "b", "c"]})
    unins = pd.DataFrame({"county_fips": ["48001", "48003", "48005"], "county": ["A", "B", "C"],
                          "uninsured_count": [1000, 5000, 3000], "uninsured_pct": [10.0, 20.0, 30.0],
                          "uninsured_pct_moe": [1.0, 2.0, 10.0]})
    zips = pd.DataFrame({"zip": ["1", "2", "3"], "county_fips": ["48001", "48003", "48005"],
                         "lat": [31.0, 32.0, 34.0], "lon": [-95.0, -102.0, -99.0],
                         "zip_type": ["STANDARD"] * 3})
    t = gaps.county_table(clin, unins, zips)
    assert t.iloc[0]["county_fips"] == "48005"          # no sites, farthest, highest rate
    assert t.iloc[0]["sites"] == 0
    assert bool(t.set_index("county_fips").loc["48005", "less_certain"])
    assert t["gap_score"].between(0, 100).all()
    s = gaps.state_summary(t, clin)
    assert s["counties_without_site"] == 1
    assert s["uninsured_in_counties_without_site"] == 3000


def test_unique_zips_are_ignored_for_distance():
    clin = pd.DataFrame({"lat": [30.0], "lon": [-97.0]})
    zips = pd.DataFrame({"zip": ["1", "2"], "county_fips": ["48001", "48001"], "lat": [30.0, 33.0],
                         "lon": [-97.0, -97.0], "zip_type": ["STANDARD", "UNIQUE"]})
    d = gaps.zip_distances(zips, clin)
    assert list(d["zip"]) == ["1"]
    assert math.isclose(d["nearest_miles"].iloc[0], 0.0, abs_tol=1e-9)


def test_htw_not_suggested_when_teen_gets_childrens_medicaid():
    # A 16-year-old at 121% FPL fits Children's Medicaid, so Healthy Texas Women doesn't apply.
    g = coverage.guide(coverage.Household(age=16, household_size=4, yearly_income=40000, female=True))
    s = statuses(g)
    assert s["children_medicaid"] == coverage.LIKELY
    assert s["healthy_texas_women"] == coverage.UNLIKELY


def test_htw_suggested_for_teen_above_childrens_limits():
    # 203% FPL: above CHIP's 201% limit but at Healthy Texas Women's 204.2% limit.
    g = coverage.guide(coverage.Household(age=17, household_size=4, yearly_income=33000 * 2.03, female=True))
    s = statuses(g)
    assert s["chip"] != coverage.LIKELY
    assert s["healthy_texas_women"] == coverage.CHECK


# ---------------------------------------------------------------- county map
def test_county_map_builds_without_network():
    from caremap import county_map
    geojson = {"type": "FeatureCollection", "features": [
        {"id": f"4800{i}", "geometry": {"type": "Polygon", "coordinates": [[[-100 + i, 30], [-99 + i, 30],
                                                                           [-99 + i, 31], [-100 + i, 30]]]}}
        for i in range(1, 6)]}
    table = pd.DataFrame({"county_fips": [f"4800{i}" for i in range(1, 6)], "county": list("ABCDE"),
                          "gap_score": [10, 20, 30, 40, None]})
    fig = county_map.figure(table, geojson, "gap_score", ["#cde2fb", "#6da7ec", "#256abf"])
    names = [t.name for t in fig.data if t.name]
    assert "No data" in names
    assert len(fig.data) >= 3


def test_class_breaks_handle_ties():
    from caremap import county_map
    b = county_map.class_breaks(pd.Series([0, 0, 0, 0, 5]), 4)
    assert list(b) == sorted(set(b))


def test_pregnancy_medicaid_replaces_marketplace_credits():
    g = coverage.guide(coverage.Household(age=25, household_size=2, yearly_income=30000, female=True, pregnant=True))
    s = statuses(g)
    assert s["pregnancy_medicaid"] == coverage.LIKELY
    assert s["marketplace"] == coverage.UNLIKELY


def test_listing_url_includes_name_and_address():
    url = clinics.listing_url({"name": "Lone Star Clinic", "address": "1 Main St", "city": "Austin", "zip": "78701"})
    assert url.startswith("https://www.google.com/maps/search/?api=1&query=")
    assert "Lone%20Star%20Clinic" in url and " " not in url
