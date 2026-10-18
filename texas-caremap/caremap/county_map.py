"""Draw a Texas county map with plain Plotly shapes.

Plotly's built-in geographic charts download a world outline from the
internet every time they load, which fails on networks that block it (like
some school Wi-Fi). This module draws each county's boundary as a filled
shape on ordinary x/y axes instead, so the map needs no outside files.

Counties are grouped into equal-count classes (quantiles), each drawn in one
step of a light-to-dark color ramp. Quantile classes give every color about the
same number of counties, so the map shows rank order clearly even when a few
counties have extreme values.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go

MID_LATITUDE = 31.0  # middle of Texas; used to keep the map from looking stretched


def _rings(geometry: dict):
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    for poly in polygons:
        yield poly[0]  # outer ring only; Texas counties have no meaningful holes


def class_breaks(values: pd.Series, n_classes: int) -> np.ndarray:
    """Quantile break points, with duplicates removed when many values tie."""
    qs = np.linspace(0, 1, n_classes + 1)
    return np.unique(np.nanquantile(values.to_numpy(dtype=float), qs))


def assign_class(values: pd.Series, breaks: np.ndarray) -> pd.Series:
    if len(breaks) < 2:
        return pd.Series(0, index=values.index)
    idx = np.searchsorted(breaks, values.to_numpy(dtype=float), side="right") - 1
    return pd.Series(np.clip(idx, 0, len(breaks) - 2), index=values.index)


def figure(table: pd.DataFrame, geojson: dict, column: str, ramp: list[str],
           value_format: str = ".1f", hover_cols: dict | None = None,
           missing_color: str = "#e6e6e3", height: int = 560) -> go.Figure:
    t = table.set_index("county_fips")
    values = pd.to_numeric(t[column], errors="coerce")
    breaks = class_breaks(values.dropna(), len(ramp))
    n_bins = max(len(breaks) - 1, 1)
    # Spread the available colors across however many classes survived ties.
    colors = [ramp[round(i * (len(ramp) - 1) / max(n_bins - 1, 1))] for i in range(n_bins)]
    classes = assign_class(values.fillna(-math.inf), breaks)
    classes[values.isna()] = -1

    fig = go.Figure()
    for cls in [-1] + list(range(n_bins)):
        xs, ys = [], []
        for feat in geojson["features"]:
            fips = feat["id"]
            if fips not in t.index or classes.get(fips, -1) != cls:
                continue
            for ring in _rings(feat["geometry"]):
                xs.extend(p[0] for p in ring)
                ys.extend(p[1] for p in ring)
                xs.append(None)
                ys.append(None)
        if not xs:
            continue
        if cls == -1:
            name, color = "No data", missing_color
        else:
            low, high = breaks[cls], breaks[cls + 1]
            name, color = f"{low:{value_format}} – {high:{value_format}}", colors[cls]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines", fill="toself", fillcolor=color,
            line=dict(color="white", width=0.6), name=name, hoverinfo="skip",
            legendrank=1000 - cls,
        ))

    # Invisible points at county centers carry the hover text.
    centers = []
    for feat in geojson["features"]:
        if feat["id"] not in t.index:
            continue
        pts = np.array([p for ring in _rings(feat["geometry"]) for p in ring], dtype=float)
        centers.append((feat["id"], pts[:, 0].mean(), pts[:, 1].mean()))
    c = pd.DataFrame(centers, columns=["county_fips", "x", "y"]).set_index("county_fips").join(t)
    hover_cols = hover_cols or {column: column}
    lines = [f"<b>{name}</b>" for name in c["county"]]
    for col, label in hover_cols.items():
        vals = c[col]
        for i, v in enumerate(vals):
            if isinstance(v, (int, float, np.floating, np.integer)) and not pd.isna(v):
                text = f"{v:,.0f}" if col in ("sites", "uninsured_count") else f"{v:,.1f}"
            else:
                text = "—" if pd.isna(v) else str(v)
            lines[i] += f"<br>{label}: {text}"
    fig.add_trace(go.Scatter(
        x=c["x"], y=c["y"], mode="markers", marker=dict(size=14, opacity=0),
        hovertext=lines, hoverinfo="text", showlegend=False,
    ))

    fig.update_xaxes(visible=False, scaleanchor="y", scaleratio=math.cos(math.radians(MID_LATITUDE)))
    fig.update_yaxes(visible=False)
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="v", x=0.0, y=0.02, xanchor="left", yanchor="bottom",
                    bgcolor="rgba(255,255,255,0.85)", font=dict(size=12)),
        hoverlabel=dict(bgcolor="white", font=dict(color="#1d2430")),
        dragmode=False,
    )
    return fig
