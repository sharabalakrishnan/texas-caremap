"""Tests for the data build script's parsing helpers (no network needed)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build_data  # noqa: E402

SAHIE_HEADER = ("version,year,statefips,countyfips,geocat,agecat,racecat,sexcat,iprcat,NIPR,nipr_moe,"
                "NUI,nui_moe,NIC,nic_moe,PCTUI,pctui_moe,PCTIC,pctic_moe,state_name,county_name")


def sahie_line(state, county, geocat="50", agecat="0", iprcat="0", nui="1000", pct="20.5", moe="1.2",
               name="Travis County"):
    return (f"x, 2024,{state:>3},{county:>4},{geocat},{agecat:>2},0,0,{iprcat},5000,10,{nui:>7},50,"
            f"4000,40,{pct},{moe},79.5,1.2,Texas,{name}")


def make_file(rows):
    notes = ["Small Area Health Insurance Estimates",
             "statefips       2 unique fips code for each state",
             "countyfips      3 unique fips code for each county within a state",
             "geocat          2 geography category: 40 state, 50 county", ""]
    return "\n".join(notes + [SAHIE_HEADER] + rows)


def test_parse_sahie_keeps_only_texas_county_totals():
    rows = [sahie_line("48", str(i)) for i in range(1, 256, 1)][:254]
    rows += [
        sahie_line("48", "453", agecat="1"),        # different age group -> dropped
        sahie_line("48", "453", iprcat="3"),        # income subgroup -> dropped
        sahie_line("48", "0", geocat="40"),         # state row -> dropped
        sahie_line("6", "37", name="Los Angeles County"),  # California -> dropped
    ]
    out = build_data.parse_sahie(make_file(rows))
    assert len(out) == 254
    first = out[0]
    assert first["county_fips"] == "48001"
    assert first["county"] == "Travis"
    assert first["uninsured_count"] == 1000
    assert first["uninsured_pct"] == 20.5
    assert first["uninsured_pct_moe"] == 1.2


def test_parse_sahie_rejects_changed_layout():
    text = "notes\nstatefips,countyfips,geocat,something_else\n48,1,50,2"
    with pytest.raises(RuntimeError, match="layout changed"):
        build_data.parse_sahie(text)


def test_parse_sahie_rejects_too_few_counties():
    with pytest.raises(RuntimeError, match="Expected 254"):
        build_data.parse_sahie(make_file([sahie_line("48", "1")]))


@pytest.mark.parametrize("raw,expected", [
    ("El Paso County", "elpaso"), ("DeWitt", "dewitt"), ("De Witt County", "dewitt"), ("McLennan", "mclennan"),
])
def test_normalize_county(raw, expected):
    assert build_data.normalize_county(raw) == expected


def test_point_in_polygon():
    square = [[-98, 30], [-96, 30], [-96, 32], [-98, 32], [-98, 30]]
    assert build_data.point_in_ring(31, -97, square)
    assert not build_data.point_in_ring(33, -97, square)


def test_in_texas_bounds():
    assert build_data.in_texas(30.27, -97.74)      # Austin
    assert not build_data.in_texas(40.7, -74.0)    # New York


def test_build_clinics_parses_hrsa_pages(tmp_path, monkeypatch):
    """Simulate two pages from the HRSA map service and check the cleaned output."""
    import csv
    import json

    def feature(i, name, county="Travis County", x=-97.74, y=30.27, address=None):
        return {"attributes": {"SITE_NM": name, "SITE_ADDRESS": address or f"{i} Main St",
                               "SITE_CITY": "Austin", "SITE_ZIP_CD": "78701-1234", "COUNTY_NM": county,
                               "HCC_TYP_DESC": "Service Delivery Site", "TOT_OPER_HR_PER_WEEK": 40,
                               "HCC_OPER_SCHD_DESC": "Full-Time", "HCC_CLND_SCHD_DIM_DESC": "Year-Round",
                               "GRANTEE_NM": "Org", "RURAL_IND": "N", "CONG_DIST_NUM": "37",
                               "BPHC_SITE_NUM": f"BPS-{i}", "X": x, "Y": y},
                "geometry": {"x": x, "y": y}}

    pages = [
        {"features": [feature(1, "A"), feature(2, "B"), feature(1, "A")], "exceededTransferLimit": True},
        {"features": [feature(3, "C", county="De Witt"), feature(4, "Bad", x=0, y=0)]},
    ]
    calls = []
    monkeypatch.setattr(build_data, "fetch", lambda url, retries=3: (calls.append(url), json.dumps(pages[len(calls) - 1]).encode())[1])
    monkeypatch.setattr(build_data, "OUT", tmp_path)
    monkeypatch.setattr(build_data, "ROOT", tmp_path.parent)
    monkeypatch.setattr(build_data, "county_lookup", lambda: {"travis": "48453", "dewitt": "48123"})
    build_data.build_clinics()

    rows = list(csv.DictReader(open(tmp_path / "clinics_tx.csv", encoding="utf-8")))
    assert [r["name"] for r in rows] == ["A", "B", "C"]      # duplicate and bad-coordinate rows removed
    assert rows[0]["zip"] == "78701" and rows[0]["county"] == "Travis"
    assert rows[2]["county_fips"] == "48123"
    assert "resultOffset=3" in calls[1]                          # second page starts after the first


def test_parse_sahie_reports_missing_header():
    with pytest.raises(RuntimeError, match="Could not find the column header"):
        build_data.parse_sahie("statefips   2 unique fips code for each state\nno header here")
