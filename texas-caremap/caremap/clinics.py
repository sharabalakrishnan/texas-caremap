"""Clinic search: find health center sites near a ZIP code."""

from __future__ import annotations

import urllib.parse

import pandas as pd

from .geo import haversine_miles


def search(clinics: pd.DataFrame, lat: float, lon: float, radius_miles: float = 25,
           min_hours: float = 0, site_types: list[str] | None = None,
           limit: int = 25) -> pd.DataFrame:
    """Return clinics within `radius_miles`, closest first.

    Filters:
      min_hours   - only sites open at least this many hours a week
      site_types  - only these HRSA site types (None means all)
    If nothing is inside the radius, the closest few sites are returned anyway,
    flagged with `outside_radius=True`, so a rural search never comes back empty.
    """
    df = clinics.copy()
    df["distance_miles"] = haversine_miles(lat, lon, df["lat"].to_numpy(), df["lon"].to_numpy())

    if min_hours:
        hours = pd.to_numeric(df["hours_per_week"], errors="coerce")
        df = df[hours.fillna(0) >= min_hours]
    if site_types:
        df = df[df["site_type"].isin(site_types)]

    df = df.sort_values(["distance_miles", "name"], kind="mergesort")
    inside = df[df["distance_miles"] <= radius_miles]
    if not inside.empty:
        result = inside.head(limit).copy()
        result["outside_radius"] = False
    else:
        result = df.head(3).copy()
        result["outside_radius"] = True
    return result.reset_index(drop=True)


def directions_url(row) -> str:
    """Google Maps directions link built from the clinic's street address."""
    destination = f"{row['address']}, {row['city']}, TX {row['zip']}"
    return "https://www.google.com/maps/dir/?api=1&destination=" + urllib.parse.quote(destination)


def listing_url(row) -> str:
    """Google Maps listing for this clinic (shows phone, hours and website)."""
    query = f"{row['name']}, {row['address']}, {row['city']}, TX {row['zip']}"
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(query)


def hours_label(value) -> str:
    try:
        hours = float(value)
    except (TypeError, ValueError):
        return "Hours not listed"
    if hours <= 0:
        return "Hours not listed"
    return f"Open about {hours:g} hours a week"


def distance_label(miles: float) -> str:
    if miles < 0.1:
        return "Less than 0.1 mi"
    if miles < 10:
        return f"{miles:.1f} mi"
    return f"{miles:.0f} mi"
