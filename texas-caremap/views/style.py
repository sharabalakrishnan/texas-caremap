"""Visual style: a calm, Apple-like look layered on top of Streamlit.

System fonts (San Francisco on Apple devices, Inter elsewhere), generous white
space, soft rounded cards, pill buttons, and Texas flag colors: navy blue, white and red. Everything is plain
CSS, so the app's logic doesn't change.
"""

import html

import streamlit as st

INK = "#1d1d1f"
SECONDARY = "#6e6e73"
BLUE = "#002868"      # Texas flag blue
RED = "#BF0A30"       # Texas flag red
SURFACE = "#f5f5f7"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
  --ink: {INK};
  --secondary: {SECONDARY};
  --blue: {BLUE};
  --red: {RED};
  --blue-tint: #e8edf7;
  --red-tint: #fbe9ed;
  --surface: {SURFACE};
  --hairline: rgba(0, 0, 0, 0.08);
  --font: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", Inter,
          "Helvetica Neue", Arial, sans-serif;
}}

html, body, .stApp, .stMarkdown, .stCaption, p, li, label, h1, h2, h3, h4, button, input, select, textarea,
[data-testid="stSidebarNav"] span, [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] *:not([class*="material"]),
[data-testid="stCaptionContainer"] *, [data-testid="stWidgetLabel"] * {{
  font-family: var(--font) !important;
  -webkit-font-smoothing: antialiased;
}}
/* Keep Streamlit's icon font for icons */
html body [data-testid="stIconMaterial"][data-testid], html body .material-symbols-rounded.material-symbols-rounded {{
  font-family: "Material Symbols Rounded" !important;
}}

/* Page frame: centered, tight, airy */
[data-testid="stHeader"] {{ background: rgba(255, 255, 255, 0.72); backdrop-filter: saturate(180%) blur(20px); }}
.stApp::before {{
  content: ""; position: fixed; top: 0; left: 0; right: 0; height: 5px; z-index: 1000001;
  background: linear-gradient(90deg, var(--blue) 0 33.3%, #ffffff 33.3% 66.6%, var(--red) 66.6% 100%);
  box-shadow: 0 1px 0 var(--hairline);
}}
[data-testid="stDecoration"], [data-testid="stToolbar"] [data-testid="stToolbarActions"],
[data-testid="stAppDeployButton"], #MainMenu, footer {{ display: none !important; }}
.block-container, [data-testid="stMainBlockContainer"] {{
  max-width: 1040px; padding-top: 2.5rem; padding-bottom: 4rem;
}}

/* Type */
h1, h2, h3, h4 {{ color: var(--ink); letter-spacing: -0.022em; }}
h1 {{ font-weight: 700 !important; }}
p, li, label, .stMarkdown {{ color: var(--ink); }}
[data-testid="stCaptionContainer"], .stCaption {{ color: var(--secondary) !important; }}
a {{ color: var(--blue); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

.stApp .tc-eyebrow {{ color: var(--red); text-transform: uppercase; letter-spacing: 0.06em; font-size: 0.85rem !important; font-size: 0.95rem; font-weight: 600; margin: 0 0 0.35rem; }}
.stApp .tc-title {{ font-size: clamp(2rem, 4.6vw, 3rem); line-height: 1.07; font-weight: 700;
             letter-spacing: -0.03em; color: var(--ink); margin: 0 0 0.75rem; }}
.stApp .tc-sub {{ font-size: clamp(1.05rem, 1.7vw, 1.3rem); line-height: 1.45; color: var(--secondary);
           max-width: 46rem; margin: 0 0 2rem; }}
.stApp .tc-section {{ font-size: 1.6rem; line-height: 1.2; font-weight: 700; letter-spacing: -0.02em; margin: 2.5rem 0 0.75rem; color: var(--ink); }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: var(--surface); border-right: 1px solid var(--hairline); }}
[data-testid="stSidebarNav"] a, [data-testid="stSidebarNavLink"] {{ border-radius: 10px; }}
[data-testid="stSidebarNav"] a[aria-current="page"], [data-testid="stSidebarNavLink"][aria-current="page"] {{
  background: var(--blue-tint) !important; box-shadow: inset 3px 0 0 var(--red);
}}
[data-testid="stSidebarNav"] a[aria-current="page"] span {{ color: var(--blue) !important; font-weight: 600; }}
[data-testid="stSidebarNav"] span, [data-testid="stSidebarNavLink"] span {{ font-weight: 500; color: var(--ink); }}

/* Cards: bordered containers, forms, expanders, metrics */
/* A card is the bordered container holding an element tagged .tc-card.
   Newer Streamlit: the bordered block is stVerticalBlock itself.
   Older Streamlit: a stVerticalBlockBorderWrapper around it. */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .tc-card),
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] .tc-card),
[data-testid="stForm"] {{
  border: 1px solid var(--hairline) !important; border-radius: 18px !important;
  background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.04);
}}
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .tc-card) {{ padding: 1.25rem 1.35rem 1.1rem !important; }}
[data-testid="stForm"] {{ padding: 1.4rem 1.5rem 1.2rem; }}
[data-testid="stExpander"] details {{ border: 1px solid var(--hairline); border-radius: 14px; }}
[data-testid="stMetric"] {{
  background: var(--surface); border-radius: 18px; padding: 1.1rem 1.2rem;
}}
[data-testid="stMetricLabel"] p {{ color: var(--secondary); font-size: 0.9rem; font-weight: 500; }}
[data-testid="stMetricValue"] {{ color: var(--ink); font-weight: 700; letter-spacing: -0.02em;
  font-size: clamp(1.5rem, 2.4vw, 2rem) !important; }}
[data-testid="stMetricLabel"] p {{ white-space: normal !important; }}

/* Inputs */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="base-input"] {{
  border-radius: 12px !important; background: var(--surface) !important; border-color: transparent !important;
}}

/* Buttons: pills */
.stButton button, [data-testid="stFormSubmitButton"] button, [data-testid="stLinkButton"] a,
[data-testid="stDownloadButton"] button, [data-testid="stPageLink"] a {{
  border-radius: 980px !important; font-weight: 500 !important; padding: 0.5rem 1.15rem !important;
  transition: background 0.2s ease, transform 0.1s ease;
}}
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"], .stButton button[kind="primary"] {{
  background: var(--blue) !important; border: none !important; color: #fff !important; min-width: 7rem;
}}
[data-testid="stLinkButton"] a {{
  background: var(--blue-tint) !important; border: none !important; color: var(--blue) !important;
}}
[data-testid="stLinkButton"] a:hover {{ background: #d9e1f2 !important; text-decoration: none; }}
[data-testid="stLinkButton"] a *, [data-testid="stLinkButton"] a p {{ color: var(--blue) !important; font-weight: 500; }}
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"] *, .stButton button[kind="primary"] * {{ color: #fff !important; }}
.stButton button:active, [data-testid="stLinkButton"] a:active {{ transform: scale(0.98); }}

[data-testid="stPageLink"] a {{ padding-left: 0 !important; background: transparent !important; }}
[data-testid="stPageLink"] a span, [data-testid="stPageLink"] a p {{ color: var(--blue) !important; font-weight: 500; }}
[data-testid="stPageLink"] a:hover {{ background: transparent !important; }}

/* Alerts: soft */
[data-testid="stAlert"], [data-testid="stAlertContainer"] {{ border-radius: 14px !important; border: none !important; }}

/* Clinic card details */
.stApp .tc-card-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; }}
.stApp .tc-card-name {{ font-size: 1.12rem; font-weight: 600; letter-spacing: -0.01em; color: var(--ink); }}
.stApp .tc-pill {{ background: var(--blue-tint); color: var(--blue); border-radius: 980px; padding: 0.2rem 0.7rem;
            font-size: 0.9rem; font-weight: 600; white-space: nowrap; }}
.stApp .tc-org {{ color: var(--secondary); font-size: 0.88rem; margin: 0.15rem 0 0.6rem; }}
.stApp .tc-line {{ color: var(--ink); font-size: 0.98rem; margin: 0; }}
.stApp .tc-meta {{ color: var(--secondary); font-size: 0.88rem; margin: 0.2rem 0 0.4rem; }}

/* Home tiles */
.stApp .tc-tile-kicker {{ color: var(--secondary); font-size: 0.85rem; font-weight: 600; text-transform: uppercase;
                   letter-spacing: 0.04em; margin-bottom: 0.4rem; }}
.stApp .tc-tile-title {{ font-size: 1.45rem; font-weight: 700; letter-spacing: -0.02em; color: var(--ink); margin: 0 0 0.4rem; }}
.stApp .tc-tile-body {{ color: var(--secondary); font-size: 1rem; line-height: 1.45; }}
@media (min-width: 900px) {{ .stApp .tc-tile-body {{ min-height: 5.9em; }} }}
.stApp .tc-stat {{ font-size: 2.2rem; font-weight: 700; letter-spacing: -0.03em; color: var(--blue); line-height: 1.1; }}
.stApp .tc-stat-label {{ color: var(--secondary); font-size: 0.95rem; }}

@media (max-width: 640px) {{
  .block-container, [data-testid="stMainBlockContainer"] {{ padding-top: 1.5rem; }}
  [data-testid="stForm"] {{ padding: 1rem; }}
}}
</style>
"""


def apply() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    sub = f'<p class="tc-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f'<p class="tc-eyebrow">{html.escape(eyebrow)}</p>'
        f'<h1 class="tc-title">{html.escape(title)}</h1>{sub}',
        unsafe_allow_html=True,
    )


def section(title: str) -> None:
    st.markdown(f'<p class="tc-section">{html.escape(title)}</p>', unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Bold Texas theme: navy banner, navy sidebar, red actions, colored card edges.
# Added on top of the base style above, so later rules win.
BOLD_CSS = """
<style>
/* Thicker flag stripe */
.stApp::before { height: 8px !important; }

/* Navy sidebar with white text */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #002868 0%, #0b3a8c 100%) !important; border-right: none !important; }
[data-testid="stSidebar"] * { color: #ffffff !important; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * { color: rgba(255,255,255,0.78) !important; }
[data-testid="stSidebarNav"] a:hover, [data-testid="stSidebarNavLink"]:hover { background: rgba(255,255,255,0.10) !important; }
[data-testid="stSidebarNav"] a[aria-current="page"], [data-testid="stSidebarNavLink"][aria-current="page"] {
  background: rgba(255,255,255,0.16) !important; box-shadow: inset 4px 0 0 #BF0A30 !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] span { color: #ffffff !important; font-weight: 700 !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2) !important; }

/* Page banner */
.stApp .tc-hero {
  position: relative; overflow: hidden; border-radius: 24px; padding: 2.2rem 2.2rem 2rem; margin: 0.5rem 0 2rem;
  background: linear-gradient(120deg, #002868 0%, #0d47a1 62%, #1565c0 100%); color: #fff;
  box-shadow: 0 12px 32px rgba(0, 40, 104, 0.25);
}
.stApp .tc-hero::after {   /* lone star */
  content: "★"; position: absolute; right: 1.6rem; top: 50%; transform: translateY(-50%);
  font-size: clamp(5rem, 13vw, 10rem); line-height: 1; color: rgba(255,255,255,0.10); pointer-events: none;
}
.stApp .tc-hero::before {  /* red band along the bottom */
  content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 6px; background: #BF0A30;
}
.stApp .tc-hero .tc-eyebrow {
  display: inline-block; background: #BF0A30; color: #fff !important; padding: 0.28rem 0.75rem; border-radius: 980px;
  font-size: 0.78rem !important; letter-spacing: 0.08em; margin-bottom: 0.9rem;
}
.stApp .tc-hero .tc-title { color: #ffffff !important; max-width: 85%; }
.stApp .tc-hero .tc-sub { color: rgba(255,255,255,0.88) !important; margin-bottom: 0; max-width: 80%; }

/* Section headings: navy with a red underline bar */
.stApp .tc-section { color: #002868 !important; }
.stApp .tc-section::after { content: ""; display: block; width: 44px; height: 4px; border-radius: 4px; background: #BF0A30; margin-top: 0.45rem; }

/* Main action buttons: red */
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"], .stButton button[kind="primary"] {
  background: #BF0A30 !important; box-shadow: 0 4px 14px rgba(191, 10, 48, 0.30);
}
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"]:hover, .stButton button[kind="primary"]:hover { background: #a1082a !important; }

/* Search / question form: blue top edge */
[data-testid="stForm"] { border-top: 5px solid #002868 !important; }

/* Cards: navy left edge, red distance badge */
[data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .tc-card),
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] > [data-testid="element-container"] .tc-card) {
  border-left: 5px solid #002868 !important;
}
.stApp .tc-pill { background: #fbe9ed !important; color: #BF0A30 !important; }
.stApp .tc-card-name { color: #002868 !important; }

/* Home tiles: alternate blue / red / blue tops */
[data-testid="stColumn"]:nth-child(odd) [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .tc-tile-kicker) {
  border-left: 1px solid rgba(0,0,0,0.08) !important; border-top: 6px solid #002868 !important;
}
[data-testid="stColumn"]:nth-child(even) [data-testid="stVerticalBlock"]:has(> [data-testid="stElementContainer"] .tc-tile-kicker) {
  border-left: 1px solid rgba(0,0,0,0.08) !important; border-top: 6px solid #BF0A30 !important;
}
.stApp .tc-tile-kicker { color: #BF0A30 !important; }
.stApp .tc-tile-title { color: #002868 !important; }

/* Headline numbers: blue, red, blue */
[data-testid="stColumn"]:nth-child(even) .tc-stat { color: #BF0A30 !important; }

/* Number tiles: tinted with a colored top */
[data-testid="stMetric"] { background: #eef3fb !important; border-top: 4px solid #002868; }
[data-testid="stColumn"]:nth-child(even) [data-testid="stMetric"] { background: #fdf0f3 !important; border-top-color: #BF0A30; }
[data-testid="stMetricValue"] { color: #002868 !important; }
[data-testid="stColumn"]:nth-child(even) [data-testid="stMetricValue"] { color: #BF0A30 !important; }


/* Faint Texas flag watermark behind the page */
[data-testid="stAppViewContainer"], [data-testid="stMain"], section.main {
  background-image: url("data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20viewBox%3D%220%200%20300%20200%22%20preserveAspectRatio%3D%22xMidYMid%20slice%22%3E%3Cg%20opacity%3D%220.06%22%3E%3Crect%20x%3D%220%22%20y%3D%220%22%20width%3D%22100%22%20height%3D%22200%22%20fill%3D%22%23002868%22/%3E%3Crect%20x%3D%22100%22%20y%3D%22100%22%20width%3D%22200%22%20height%3D%22100%22%20fill%3D%22%23BF0A30%22/%3E%3C/g%3E%3Cpolygon%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.55%22%20points%3D%2250%2C62%2059%2C89%2088%2C89%2065%2C106%2073%2C133%2050%2C117%2027%2C133%2035%2C106%2012%2C89%2041%2C89%22/%3E%3C/svg%3E") !important;
  background-repeat: no-repeat !important;
  background-attachment: fixed !important;
  background-position: center center !important;
  background-size: cover !important;
}
[data-testid="stMain"] [data-testid="stAppViewContainer"], [data-testid="stMain"] section.main { background-image: none !important; }
@media (max-width: 640px) {
  [data-testid="stAppViewContainer"], [data-testid="stMain"], section.main { background-size: cover !important; background-position: 20% center !important; }
}

/* Charts sit on white cards, so the flag watermark never shows behind data */
[data-testid="stPlotlyChart"] { background: #ffffff; border-radius: 18px; padding: 0.5rem; box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.04); }

@media (max-width: 640px) {
  .stApp .tc-hero { padding: 1.5rem 1.3rem 1.4rem; border-radius: 18px; }
  .stApp .tc-hero .tc-title, .stApp .tc-hero .tc-sub { max-width: 100%; }
}
</style>
"""

_base_apply = apply


def apply() -> None:  # noqa: F811 - extends the base style
    _base_apply()
    st.markdown(BOLD_CSS, unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str = "") -> None:  # noqa: F811 - banner version
    sub = f'<p class="tc-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f'<div class="tc-hero"><p class="tc-eyebrow">{html.escape(eyebrow)}</p>'
        f'<h1 class="tc-title">{html.escape(title)}</h1>{sub}</div>',
        unsafe_allow_html=True,
    )
