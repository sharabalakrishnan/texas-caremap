"""Texas CareMap - find a community health center and coverage options in Texas.

Run locally:   streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Texas CareMap",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="auto",
)

from views import about, coverage_page, finder, gaps_page, home, style  # noqa: E402
from views.common import get_data, sample_banner  # noqa: E402

style.apply()

pages = {
    "home": st.Page(home.render, title="Home", icon=":material/home:", url_path="home", default=True),
    "find": st.Page(finder.render, title="Find a clinic", icon=":material/location_on:", url_path="find"),
    "coverage": st.Page(coverage_page.render, title="Coverage guide", icon=":material/health_and_safety:",
                        url_path="coverage"),
    "gaps": st.Page(gaps_page.render, title="Texas access gaps", icon=":material/map:", url_path="gaps"),
    "about": st.Page(about.render, title="About & privacy", icon=":material/info:", url_path="about"),
}
home.PAGES = pages

nav = st.navigation(list(pages.values()))

with st.sidebar:
    st.caption("In an emergency, call **911**. For a mental health crisis, call or text **988**.")

sample_banner(get_data())
nav.run()
