"""Shared test fixtures for globe_cloud_insights tests."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


@pytest.fixture()
def sample_raw_csv(tmp_path: Path) -> Path:
    """Create a minimal raw CSV file mimicking GLOBE API output."""
    data = {
        "pid": [f"P{i}" for i in range(20)],
        "measuredDate": pd.date_range("2022-01-15", periods=20, freq="D").strftime(
            "%Y-%m-%dT%H:%M:%S"
        ),
        "latitude": np.random.uniform(-60, 70, 20).tolist(),
        "longitude": np.random.uniform(-170, 170, 20).tolist(),
        "countryName": ["United States"] * 5
        + ["India"] * 5
        + ["Brazil"] * 5
        + ["Germany"] * 5,
        "skyCondition": ["Clear", "Few", "Scattered", "Broken", "Overcast"] * 4,
        "cloudType": ["Cumulus", "Stratus", "Cirrus", "Stratocumulus", "Altocumulus"]
        * 4,
        "cloudOpacity": ["Transparent", "Thin", "Opaque", "Thin", "Opaque"] * 4,
        "surfaceCondition": ["Dry", "Wet", "Snow", "Dry", "Ice"] * 4,
    }
    df = pd.DataFrame(data)
    csv_path = tmp_path / "raw" / "globe_clouds_2022.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture()
def sample_clean_df() -> pd.DataFrame:
    """Return a small cleaned DataFrame for analysis tests."""
    n = 50
    np.random.seed(42)
    conditions = ["Clear", "Few", "Scattered", "Broken", "Overcast"]
    cover_map = {"Clear": 0, "Few": 15, "Scattered": 40, "Broken": 70, "Overcast": 95}
    sky = np.random.choice(conditions, n)
    return pd.DataFrame(
        {
            "observation_id": [f"OBS-{i:06d}" for i in range(n)],
            "measured_at": pd.date_range("2022-01-15", periods=n, freq="8h"),
            "latitude": np.random.uniform(-60, 70, n),
            "longitude": np.random.uniform(-170, 170, n),
            "country_name": np.random.choice(
                ["United States", "India", "Brazil", "Germany", "Japan"], n
            ),
            "sky_condition": sky,
            "cloud_cover_pct": [cover_map[s] + np.random.normal(0, 3) for s in sky],
            "cloud_types": np.random.choice(
                ["Cumulus", "Stratus", "Cirrus", "Stratocumulus"], n
            ),
            "cloud_opacity": np.random.choice(["Transparent", "Thin", "Opaque"], n),
            "surface_condition": np.random.choice(["Dry", "Wet", "Snow", "Ice"], n),
        }
    )


@pytest.fixture()
def sample_geojson_response() -> dict:
    """Return a mock GLOBE API GeoJSON response."""
    features = []
    for i in range(10):
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-77.0 + i * 0.1, 38.9 + i * 0.01],
                },
                "properties": {
                    "pid": f"P{i}",
                    "measuredDate": f"2022-01-{15 + i}T12:00:00",
                    "countryName": "United States",
                    "data": json.dumps(
                        {
                            "sky_conditions": {
                                "value": "Scattered",
                                "cloudOpacity": "Thin",
                                "surfaceCondition": "Dry",
                            },
                            "clouds": [{"type": "Cumulus"}, {"type": "Stratus"}],
                        }
                    ),
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}
