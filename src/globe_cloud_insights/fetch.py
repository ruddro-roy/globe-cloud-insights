"""Data acquisition from the GLOBE API.

Implements a reproducible pipeline that retrieves GLOBE Observer Clouds
protocol data for a configurable date range, with local caching to avoid
redundant network requests.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import requests

from globe_cloud_insights.config import (
    GLOBE_API_BASE,
    GLOBE_END_DATE,
    GLOBE_PROTOCOL,
    GLOBE_START_DATE,
    RAW_DIR,
)

logger = logging.getLogger(__name__)

# ── Public helpers ───────────────────────────────────────────────────────────


def build_api_url(
    protocol: str = GLOBE_PROTOCOL,
    start_date: str = GLOBE_START_DATE,
    end_date: str = GLOBE_END_DATE,
    geojson: bool = True,
    sample: bool = False,
) -> str:
    """Return a fully-qualified GLOBE API URL for the given parameters."""
    params = (
        f"protocols={protocol}"
        f"&startdate={start_date}"
        f"&enddate={end_date}"
        f"&geojson={'TRUE' if geojson else 'FALSE'}"
        f"&sample={'TRUE' if sample else 'FALSE'}"
    )
    return f"{GLOBE_API_BASE}?{params}"


def _checksum(path: Path) -> str:
    """Return the SHA-256 hex digest of *path*."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _date_range_chunks(
    start: str, end: str, chunk_days: int = 7
) -> list[tuple[str, str]]:
    """Split a date range into chunks to stay under the GLOBE 1M-row limit."""
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    chunks: list[tuple[str, str]] = []
    while s < e:
        chunk_end = min(s + timedelta(days=chunk_days), e)
        chunks.append((s.isoformat(), chunk_end.isoformat()))
        s = chunk_end
    return chunks


def _features_to_records(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten GeoJSON features into flat dicts suitable for a DataFrame."""
    rows: list[dict[str, Any]] = []
    for feat in features:
        props = dict(feat.get("properties", {}))
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates", [None, None])
        if isinstance(coords, list) and len(coords) >= 2:
            props["longitude"] = coords[0]
            props["latitude"] = coords[1]
        else:
            props["longitude"] = None
            props["latitude"] = None
        rows.append(props)
    return rows


# ── Main fetch function ─────────────────────────────────────────────────────


def fetch_globe_data(
    start_date: str = GLOBE_START_DATE,
    end_date: str = GLOBE_END_DATE,
    output_dir: Path | None = None,
    chunk_days: int = 7,
    timeout: int = 120,
    force: bool = False,
) -> pd.DataFrame:
    """Download GLOBE Clouds observations and return a combined DataFrame.

    Parameters
    ----------
    start_date, end_date : str
        ISO-8601 date strings bounding the query.
    output_dir : Path, optional
        Directory for cached CSV output (defaults to ``data/raw/``).
    chunk_days : int
        Number of days per API request chunk.
    timeout : int
        HTTP request timeout in seconds.
    force : bool
        Re-download even if a cached file exists.

    Returns
    -------
    pd.DataFrame
        Raw observation records.
    """
    output_dir = output_dir or RAW_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "globe_clouds_2022.csv"

    # Short-circuit if cache exists
    if csv_path.exists() and not force:
        logger.info("Cached file found at %s — loading from disk.", csv_path)
        return pd.read_csv(csv_path)

    chunks = _date_range_chunks(start_date, end_date, chunk_days)
    all_records: list[dict[str, Any]] = []

    for i, (s, e) in enumerate(chunks, 1):
        url = build_api_url(start_date=s, end_date=e, geojson=True, sample=False)
        logger.info("Fetching chunk %d/%d: %s → %s", i, len(chunks), s, e)
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()

        features = payload.get("features", [])
        records = _features_to_records(features)
        all_records.extend(records)
        logger.info("  ↳ %d records retrieved.", len(records))

    df = pd.DataFrame(all_records)
    df.to_csv(csv_path, index=False)
    logger.info(
        "Saved %d total records to %s (sha256: %s)",
        len(df),
        csv_path,
        _checksum(csv_path),
    )
    return df
