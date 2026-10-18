"""Page 1: find community health centers near a Texas ZIP code."""

import html
import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from caremap import clinics as clinic_search
from caremap import geo
from views.common import data_date, get_data
from views.style import page_header, section

FINDER_URL = "https://findahealthcenter.hrsa.gov/"


def render():
    d = get_data()
    page_header("Find a clinic", "A health center near you.",
                "Community health centers see everyone, with or without insurance. "
                "If your income is low, you pay a reduced fee based on what you earn.")

    with st.form("search"):
        c1, c2 = st.columns([2, 3])
        zip_text = c1.text_input("Your ZIP code", max_chars=10, placeholder="78701")
        radius = c2.select_slider("How far can you travel?", options=[5, 10, 25, 50, 100],
                                  value=25, format_func=lambda m: f"{m} miles")
        with st.expander("More filters"):
            full_time = st.checkbox("Only show sites open 40 or more hours a week")
            types = sorted(t for t in d.clinics["site_type"].dropna().unique() if t)
            chosen = st.multiselect("Kind of site", types, placeholder="All kinds of sites")
        submitted = st.form_submit_button("Search", type="primary")

    st.caption("We don't save the ZIP codes you search.")

    if not submitted and "last_zip" not in st.session_state:
        return
    if submitted:
        st.session_state["last_zip"] = zip_text
    zip_code = geo.clean_zip(st.session_state["last_zip"])

    if zip_code is None:
        st.warning("Please enter a 5-digit ZIP code, like 78701.")
        return
    place = geo.lookup_zip(zip_code, d.zips)
    if place is None:
        st.warning(f"{zip_code} doesn't look like a Texas ZIP code. This app covers Texas only.")
        st.link_button("Search health centers nationwide (HRSA)", FINDER_URL)
        return

    results = clinic_search.search(
        d.clinics, place["lat"], place["lon"], radius_miles=radius,
        min_hours=40 if full_time else 0, site_types=chosen or None,
    )
    if results.empty:
        st.info("No sites match those filters. Try removing a filter.")
        return

    if results["outside_radius"].all():
        st.warning(
            f"No health center sites within {radius} miles of {zip_code}. "
            f"Here are the closest ones anyway."
        )
    else:
        section(f"{len(results)} site{'s' if len(results) != 1 else ''} within {radius} miles of "
                f"{place['city']} ({zip_code})")

    show_map(place, results)

    st.caption(
        "Distances are in a straight line, so driving distance will be longer. "
        "Call before you go to check hours and services. " + data_date(d)
    )
    for _, row in results.iterrows():
        clinic_card(row)
    st.caption(f"Official source: [HRSA Find a Health Center]({FINDER_URL}), which also lists "
               "each center's services.")


def map_zoom(place, results: pd.DataFrame, pixels: int = 360) -> float:
    """Zoom level that keeps every result on screen, centered on the user's ZIP code.

    These maps (MapLibre) show 360 degrees of longitude across 512 pixels at zoom 0,
    and each zoom step doubles that. We size the view so the farthest result fits inside
    `pixels` (a phone-width map), with some padding.
    """
    lat0 = math.radians(float(place["lat"]))
    d_lat = (results["lat"] - place["lat"]).abs().max()
    d_lon = ((results["lon"] - place["lon"]).abs() * math.cos(lat0)).max()
    needed = max(d_lat, d_lon, 0.01) * 2 * 1.35          # degrees across, with padding
    zoom = math.log2(360 * pixels * math.cos(lat0) / (512 * needed))
    return float(min(max(zoom, 4), 14))


def show_map(place, results: pd.DataFrame):
    hover = [
        f"<b>{r['name']}</b><br>{r['address']}, {r['city']}<br>"
        f"{clinic_search.distance_label(r['distance_miles'])} · {clinic_search.hours_label(r['hours_per_week'])}"
        for _, r in results.iterrows()
    ]
    # Newer Plotly uses Scattermap (MapLibre); older versions only have Scattermapbox.
    # Both use free CARTO street tiles, so no account or key is needed.
    new_api = hasattr(go, "Scattermap")
    Trace = go.Scattermap if new_api else go.Scattermapbox
    fig = go.Figure()
    fig.add_trace(Trace(
        lat=[place["lat"]], lon=[place["lon"]], mode="markers", name=f"Your ZIP code ({place['zip']})",
        marker=dict(size=14, color="#1d2430"), hovertext=[f"Center of ZIP {place['zip']}"], hoverinfo="text",
    ))
    fig.add_trace(Trace(
        lat=results["lat"], lon=results["lon"], mode="markers", name="Health center sites",
        marker=dict(size=13, color="#2a78d6", opacity=0.9), hovertext=hover, hoverinfo="text",
    ))
    view = dict(style="carto-positron", zoom=map_zoom(place, results),
                center=dict(lat=float(place["lat"]), lon=float(place["lon"])))
    fig.update_layout(
        height=400, margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(orientation="h", x=0, y=1, xanchor="left", yanchor="bottom",
                    bgcolor="rgba(255,255,255,0)"),
        hoverlabel=dict(bgcolor="white", font=dict(color="#1d2430")),
        **({"map": view} if new_api else {"mapbox": view}),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "scrollZoom": False})
    st.caption("Dark dot: the center of your ZIP code. Blue dots: health center sites. "
               "Map tiles © CARTO, © OpenStreetMap contributors.")


def clinic_card(row):
    esc = lambda v: html.escape(str(v or ""))  # noqa: E731
    details = [clinic_search.hours_label(row.get("hours_per_week"))]
    for extra in ("site_type", "schedule"):
        value = str(row.get(extra) or "").strip()
        if value and value.lower() != "unknown":
            details.append(value)
    org = row.get("organization") or ""
    org_html = (f'<p class="tc-org">{esc(org.title() if org.isupper() else org)}</p>'
                if org and org != row["name"] else '<div style="height:0.5rem"></div>')
    with st.container(border=True):
        st.markdown(
            f'<div class="tc-card tc-card-head"><span class="tc-card-name">{esc(row["name"])}</span>'
            f'<span class="tc-pill">{esc(clinic_search.distance_label(row["distance_miles"]))}</span></div>'
            f'{org_html}'
            f'<p class="tc-line">{esc(row["address"])}, {esc(row["city"])}, TX {esc(row["zip"])}</p>'
            f'<p class="tc-meta">{esc(" · ".join(details))}</p>',
            unsafe_allow_html=True,
        )
        b1, b2, _ = st.columns([1, 1, 2])
        b1.link_button("Directions", clinic_search.directions_url(row), use_container_width=True)
        b2.link_button("Phone & hours", clinic_search.listing_url(row), use_container_width=True,
                       help="Opens this clinic's Google Maps listing with its phone number, hours and website.")
