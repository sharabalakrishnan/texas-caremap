"""Visual style: a calm, Apple-like look layered on top of Streamlit.

System fonts (San Francisco on Apple devices, Inter elsewhere), generous white
space, soft rounded cards, pill buttons and one accent blue. Everything is plain
CSS, so the app's logic doesn't change.
"""

import html

import streamlit as st

INK = "#1d1d1f"
SECONDARY = "#6e6e73"
BLUE = "#0071e3"
SURFACE = "#f5f5f7"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
  --ink: {INK};
  --secondary: {SECONDARY};
  --blue: {BLUE};
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

.stApp .tc-eyebrow {{ color: var(--blue); font-size: 0.95rem; font-weight: 600; margin: 0 0 0.35rem; }}
.stApp .tc-title {{ font-size: clamp(2rem, 4.6vw, 3rem); line-height: 1.07; font-weight: 700;
             letter-spacing: -0.03em; color: var(--ink); margin: 0 0 0.75rem; }}
.stApp .tc-sub {{ font-size: clamp(1.05rem, 1.7vw, 1.3rem); line-height: 1.45; color: var(--secondary);
           max-width: 46rem; margin: 0 0 2rem; }}
.stApp .tc-section {{ font-size: 1.6rem; line-height: 1.2; font-weight: 700; letter-spacing: -0.02em; margin: 2.5rem 0 0.75rem; color: var(--ink); }}

/* Sidebar */
[data-testid="stSidebar"] {{ background: var(--surface); border-right: 1px solid var(--hairline); }}
[data-testid="stSidebarNav"] a, [data-testid="stSidebarNavLink"] {{ border-radius: 10px; }}
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
  background: var(--surface) !important; border: none !important; color: var(--blue) !important;
}}
[data-testid="stLinkButton"] a:hover {{ background: #e8e8ed !important; text-decoration: none; }}
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
.stApp .tc-pill {{ background: var(--surface); color: var(--ink); border-radius: 980px; padding: 0.2rem 0.7rem;
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
.stApp .tc-stat {{ font-size: 2.2rem; font-weight: 700; letter-spacing: -0.03em; color: var(--ink); line-height: 1.1; }}
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
