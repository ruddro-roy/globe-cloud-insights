"""Data cleaning and quality-assurance pipeline.

Transforms raw GLOBE Clouds CSV data into a tidy, analysis-ready Parquet
dataset with documented provenance.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from globe_cloud_insights.config import (
    CLEAN_PARQUET_PATH,
    RAW_CSV_PATH,
)

logger = logging.getLogger(__name__)


# ── Schema definition ────────────────────────────────────────────────────────

SCHEMA: dict[str, dict[str, Any]] = {
    "observation_id": {
        "dtype": "str",
        "description": "Unique identifier for each observation",
    },
    "measured_at": {
        "dtype": "datetime64[ns]",
        "description": "UTC timestamp of the observation",
    },
    "latitude": {
        "dtype": "float64",
        "description": "Latitude in decimal degrees (WGS 84)",
    },
    "longitude": {
        "dtype": "float64",
        "description": "Longitude in decimal degrees (WGS 84)",
    },
    "country_name": {
        "dtype": "str",
        "description": "Country where the observation was made",
    },
    "sky_condition": {
        "dtype": "category",
        "description": "Reported sky condition (e.g. Clear, Scattered, Overcast)",
    },
    "cloud_cover_pct": {
        "dtype": "float64",
        "description": "Estimated cloud cover percentage (0-100)",
    },
    "cloud_types": {
        "dtype": "str",
        "description": "Comma-separated list of cloud genera observed",
    },
    "cloud_opacity": {
        "dtype": "str",
        "description": "Reported cloud opacity (Transparent, Thin, Opaque)",
    },
    "surface_condition": {
        "dtype": "str",
        "description": "Reported surface condition at observation site",
    },
}


def get_schema_markdown() -> str:
    """Return a Markdown table documenting the cleaned dataset schema."""
    lines = ["| Column | Type | Description |", "| --- | --- | --- |"]
    for col, meta in SCHEMA.items():
        lines.append(f"| `{col}` | {meta['dtype']} | {meta['description']} |")
    return "\n".join(lines)


# ── Column mapping helpers ───────────────────────────────────────────────────

_COLUMN_MAP: dict[str, str] = {
    # Common GLOBE API field names → our clean names
    "pid": "observation_id",
    "protocol": "_drop_protocol",
    "measuredDate": "measured_at",
    "publishedDate": "_drop_published",
    "countryName": "country_name",
    "countryCode": "_drop_cc",
    "organizationName": "_drop_org",
    "siteName": "_drop_site",
    "siteId": "_drop_site_id",
    "data": "_data_blob",
}


def _sky_condition_to_pct(cond: str | None) -> float | None:
    """Map a GLOBE sky-condition label to an approximate cloud-cover %."""
    mapping = {
        "Clear": 0.0,
        "Few": 15.0,
        "Isolated": 25.0,
        "Scattered": 40.0,
        "Broken": 70.0,
        "Overcast": 95.0,
        "Obscured": 100.0,
    }
    if cond and isinstance(cond, str):
        return mapping.get(cond.strip().title())
    return None


def _extract_nested(row: pd.Series) -> pd.Series:
    """Pull sky_condition, cloud_types, etc. from nested data blobs."""
    blob = row.get("_data_blob")
    sky = None
    cloud_types_list: list[str] = []
    opacity = None
    surface = None

    if isinstance(blob, dict):
        sky_data = blob.get("sky_conditions") or blob.get("skyConditions") or {}
        if isinstance(sky_data, dict):
            sky = sky_data.get("value") or sky_data.get("sky_condition")
            opacity = sky_data.get("cloudOpacity") or sky_data.get("opacity")
            surface = sky_data.get("surfaceCondition") or sky_data.get("surface")

        cloud_data = blob.get("clouds") or blob.get("cloudTypes") or []
        if isinstance(cloud_data, list):
            for item in cloud_data:
                if isinstance(item, dict):
                    ct = item.get("type") or item.get("cloudType") or ""
                    if ct:
                        cloud_types_list.append(ct)
                elif isinstance(item, str):
                    cloud_types_list.append(item)

    elif isinstance(blob, str):
        # Already a flat string — treat as sky condition
        sky = blob

    return pd.Series(
        {
            "sky_condition": sky,
            "cloud_types": ", ".join(cloud_types_list) if cloud_types_list else None,
            "cloud_opacity": opacity,
            "surface_condition": surface,
        }
    )


# ── Main cleaning pipeline ──────────────────────────────────────────────────


def clean_data(
    raw_path: Path | None = None,
    output_path: Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Clean raw GLOBE data and save a Parquet file.

    Parameters
    ----------
    raw_path : Path, optional
        Path to the raw CSV (defaults to ``data/raw/globe_clouds_2022.csv``).
    output_path : Path, optional
        Path for the cleaned Parquet (defaults to ``data/processed/...parquet``).

    Returns
    -------
    tuple[pd.DataFrame, dict]
        The cleaned DataFrame and a provenance metadata dict.
    """
    raw_path = raw_path or RAW_CSV_PATH
    output_path = output_path or CLEAN_PARQUET_PATH

    logger.info("Loading raw data from %s", raw_path)
    df = pd.read_csv(raw_path, low_memory=False)
    n_raw = len(df)
    logger.info("Raw records: %d", n_raw)

    # ── Rename columns ───────────────────────────────────────────────────
    df = df.rename(columns=_COLUMN_MAP)

    # ── Ensure lat/lon exist ─────────────────────────────────────────────
    for col in ("latitude", "longitude"):
        if col not in df.columns:
            df[col] = None

    # ── Extract nested data if present ───────────────────────────────────
    if "_data_blob" in df.columns:
        # Try to parse JSON strings
        def _try_json(x):
            if isinstance(x, str):
                try:
                    import json

                    return json.loads(x)
                except (json.JSONDecodeError, ValueError):
                    return x
            return x

        df["_data_blob"] = df["_data_blob"].apply(_try_json)
        nested = df.apply(_extract_nested, axis=1)
        for col in nested.columns:
            if col not in df.columns:
                df[col] = nested[col]
            else:
                df[col] = df[col].fillna(nested[col])

    # ── If sky_condition / cloud columns already exist as flat columns ───
    for src, dst in [
        ("skyCondition", "sky_condition"),
        ("cloudType", "cloud_types"),
        ("cloudOpacity", "cloud_opacity"),
        ("surfaceCondition", "surface_condition"),
    ]:
        if src in df.columns and dst not in df.columns:
            df[dst] = df[src]

    # ── Ensure all schema columns exist ──────────────────────────────────
    for col in SCHEMA:
        if col not in df.columns:
            df[col] = None

    # ── Parse datetime ───────────────────────────────────────────────────
    if "measured_at" in df.columns:
        df["measured_at"] = pd.to_datetime(df["measured_at"], errors="coerce")

    # ── Cloud cover % from sky condition ─────────────────────────────────
    if "cloud_cover_pct" in df.columns:
        mask = df["cloud_cover_pct"].isna()
        df.loc[mask, "cloud_cover_pct"] = df.loc[mask, "sky_condition"].apply(
            _sky_condition_to_pct
        )

    # ── Quality filters ──────────────────────────────────────────────────
    df = df.dropna(subset=["latitude", "longitude"])
    n_after_geo = len(df)

    df = df[df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)]
    n_after_bounds = len(df)

    # Drop rows with no date
    if "measured_at" in df.columns:
        df = df.dropna(subset=["measured_at"])
    n_after_date = len(df)

    # ── Select and order final columns ───────────────────────────────────
    final_cols = [c for c in SCHEMA if c in df.columns]
    df = df[final_cols].reset_index(drop=True)

    # ── Assign observation_id if missing ─────────────────────────────────
    if df["observation_id"].isna().all():
        df["observation_id"] = [f"OBS-{i:06d}" for i in range(len(df))]

    # ── Save ─────────────────────────────────────────────────────────────
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False, engine="pyarrow")
    n_final = len(df)

    provenance = {
        "source_file": str(raw_path),
        "output_file": str(output_path),
        "retrieval_timestamp": datetime.now(timezone.utc).isoformat(),
        "records_raw": n_raw,
        "records_after_geo_filter": n_after_geo,
        "records_after_bounds_filter": n_after_bounds,
        "records_after_date_filter": n_after_date,
        "records_final": n_final,
        "dropped_total": n_raw - n_final,
        "quality_notes": (
            "Dropped rows missing lat/lon, out-of-range coordinates, "
            "and rows without a measured_at timestamp."
        ),
    }
    logger.info(
        "Cleaned %d → %d records (dropped %d). Saved to %s",
        n_raw,
        n_final,
        n_raw - n_final,
        output_path,
    )
    return df, provenance
