"""Distance math and ZIP code lookup."""

from __future__ import annotations

import numpy as np
import pandas as pd

EARTH_RADIUS_MILES = 3958.8


def haversine_miles(lat1, lon1, lat2, lon2):
    """Great-circle distance in miles between points given in degrees.

    Works on single numbers or numpy arrays (arrays broadcast against each
    other), so one call can measure from one ZIP code to every clinic.
    """
    lat1, lon1, lat2, lon2 = (np.radians(np.asarray(v, dtype=float)) for v in (lat1, lon1, lat2, lon2))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_MILES * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def clean_zip(text: str) -> str | None:
    """Turn user input like ' 78701-1234 ' into '78701'. Returns None if it isn't a ZIP code."""
    if text is None:
        return None
    digits = "".join(ch for ch in str(text) if ch.isdigit())
    if len(digits) == 9:  # ZIP+4 typed without the dash
        digits = digits[:5]
    if len(digits) != 5:
        return None
    return digits


def lookup_zip(zip_code: str, zips: pd.DataFrame) -> dict | None:
    """Find a Texas ZIP code's center point. Returns None if it isn't in Texas."""
    match = zips.loc[zips["zip"] == zip_code]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def nearest_distance(points_lat, points_lon, targets_lat, targets_lon, chunk: int = 500) -> np.ndarray:
    """For each point, the distance in miles to the nearest target.

    Done in chunks so a few thousand points x a thousand targets stays light on memory.
    """
    points_lat = np.asarray(points_lat, dtype=float)
    points_lon = np.asarray(points_lon, dtype=float)
    t_lat = np.asarray(targets_lat, dtype=float)[None, :]
    t_lon = np.asarray(targets_lon, dtype=float)[None, :]
    out = np.empty(len(points_lat))
    for start in range(0, len(points_lat), chunk):
        stop = start + chunk
        d = haversine_miles(points_lat[start:stop, None], points_lon[start:stop, None], t_lat, t_lon)
        out[start:stop] = d.min(axis=1)
    return out
