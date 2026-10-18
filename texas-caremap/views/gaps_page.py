"""Page 3: where in Texas are uninsured people far from a health center?"""

import plotly.express as px
import streamlit as st

from caremap import county_map, gaps
from views.common import GAP_BAR, GAP_RAMP, get_county_table, get_data
from views.style import page_header, section

METRICS = {
    "Access Gap Score": ("gap_score", "Score (0-100, higher = worse access)", ".0f"),
    "Percent uninsured": ("uninsured_pct", "Percent uninsured, under 65", ".1f"),
    "Distance to nearest site": ("median_miles", "Median miles to nearest site", ".1f"),
    "Sites per 10,000 uninsured": ("sites_per_10k", "Sites per 10,000 uninsured people", ".2f"),
}


def render():
    d = get_data()
    table = get_county_table()
    summary = gaps.state_summary(table, d.clinics)
    year = d.metadata.get("sahie_year", "the latest")

    page_header("Texas access gaps", "Where care is hardest to reach.",
                "Where uninsured Texans live far from a community health center, across all 254 counties.")
    st.caption(f"Combines HRSA's list of health center sites with U.S. Census uninsured estimates ({year}).")

    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Health center sites", f"{summary['sites']:,}")
    t2.metric(f"Counties without a site (of {summary['counties']})", f"{summary['counties_without_site']}")
    t3.metric("Uninsured living there", f"{summary['uninsured_in_counties_without_site']:,}",
              help=f"{summary['share_uninsured_without_site']:.1%} of uninsured Texans under 65")
    t4.metric("Typical miles to a site", f"{summary['median_county_miles']:.0f}",
              help="Median across counties of each county's median ZIP-code distance")

    if hasattr(st, "segmented_control"):
        choice = st.segmented_control("Color the map by", list(METRICS), default="Access Gap Score")
    else:  # older Streamlit versions
        choice = st.radio("Color the map by", list(METRICS), horizontal=True)
    col, label, fmt = METRICS[choice or "Access Gap Score"]
    fig = county_map.figure(
        table, d.counties_geojson, col, GAP_RAMP, value_format=fmt,
        hover_cols={"gap_score": "Gap score", "uninsured_pct": "% uninsured",
                    "median_miles": "Miles to nearest site", "sites": "Sites",
                    "sites_per_10k": "Sites per 10k uninsured"},
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption(f"{label}. Each color holds about the same number of counties; darker purple means a higher value. "
               "Hover over (or tap) a county for details.")

    section("Counties with the biggest access gaps")
    top = table.head(15).iloc[::-1]
    bar = px.bar(top, x="gap_score", y="county", orientation="h", text="gap_score",
                 labels={"gap_score": "Access Gap Score", "county": ""},
                 hover_data={"uninsured_pct": ":.1f", "median_miles": ":.1f", "sites": True})
    bar.update_traces(marker_color=GAP_BAR, texttemplate="%{text:.0f}", textposition="outside",
                      cliponaxis=False)
    bar.update_layout(height=460, margin=dict(l=0, r=30, t=10, b=0), xaxis=dict(range=[0, 105], showgrid=False),
                      paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", bargap=0.35)
    st.plotly_chart(bar, use_container_width=True, config={"displayModeBar": False})

    section("All counties")
    show = table[["county", "gap_score", "uninsured_pct", "ci_low", "ci_high", "less_certain",
                  "uninsured_count", "sites", "sites_per_10k", "median_miles"]]
    st.dataframe(
        show, hide_index=True, use_container_width=True,
        column_config={
            "county": "County",
            "gap_score": st.column_config.ProgressColumn("Gap score", min_value=0, max_value=100, format="%.0f"),
            "uninsured_pct": st.column_config.NumberColumn("% uninsured", format="%.1f"),
            "ci_low": st.column_config.NumberColumn("90% low", format="%.1f"),
            "ci_high": st.column_config.NumberColumn("90% high", format="%.1f"),
            "less_certain": st.column_config.CheckboxColumn("Wide interval",
                                                            help="The estimate's margin of error is over a quarter of its value."),
            "uninsured_count": st.column_config.NumberColumn("Uninsured people", format="%d"),
            "sites": "Sites",
            "sites_per_10k": st.column_config.NumberColumn("Sites per 10k uninsured", format="%.2f"),
            "median_miles": st.column_config.NumberColumn("Miles to nearest site", format="%.1f"),
        },
    )
    st.download_button("Download this table (CSV)", show.to_csv(index=False).encode(),
                       "texas_access_gaps.csv", "text/csv")

    with st.expander("How the Access Gap Score works"):
        st.markdown(
            """
For each county, the score combines three measures:

1. **Percent uninsured** (people under 65, Census Small Area Health Insurance Estimates). Higher is worse.
2. **Distance to care**: for every home ZIP code in the county, the straight-line distance to the nearest
   health center site, then the median across those ZIP codes. Higher is worse.
3. **Supply**: health center sites per 10,000 uninsured residents. Lower is worse.

Each measure is turned into a **percentile rank** from 0 to 100 among Texas's 254 counties, pointed so that
100 is the worst. The score is the average of the three ranks. Ranks keep any one measure (like miles, which
can be in the hundreds) from outweighing the others.

**Uncertainty.** Census estimates for small counties come with wide margins of error. The table shows each
county's 90% confidence interval and flags counties where the margin of error is more than a quarter of the
estimate, so a high score there should be read with care.

**Limits.** Distances are straight-line, not driving. ZIP code centers stand in for where people live.
Sites differ in size and services, so one site is not the same as one clinic's worth of capacity.
"""
        )

    section("Health center sites by congressional district")
    st.caption("From the district listed for each site in HRSA's data.")
    st.dataframe(
        gaps.district_table(d.clinics), hide_index=True, use_container_width=True,
        column_config={"district": st.column_config.NumberColumn("District", format="TX-%d"),
                       "sites": "Sites", "organizations": "Health center organizations",
                       "rural_sites": "Rural sites"},
    )
