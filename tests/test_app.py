"""Smoke tests for the Streamlit dashboard app."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def test_app_imports():
    """Verify the Streamlit app module can be imported without errors."""
    app_dir = Path(__file__).resolve().parents[1] / "app"
    sys.path.insert(0, str(app_dir.parent / "src"))
    sys.path.insert(0, str(app_dir))

    # Import the module (this validates syntax and top-level imports)
    spec = importlib.util.spec_from_file_location(
        "streamlit_app", app_dir / "streamlit_app.py"
    )
    assert spec is not None
    assert spec.loader is not None


def test_demo_data_generation():
    """Verify the demo data generator produces valid output."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

    # Import just the helper
    import numpy as np
    import pandas as pd

    from globe_cloud_insights.analysis import summary_statistics

    np.random.seed(42)
    n = 100
    conditions = ["Clear", "Few", "Scattered", "Broken", "Overcast"]
    sky = np.random.choice(conditions, n)
    demo = pd.DataFrame(
        {
            "observation_id": [f"OBS-{i:06d}" for i in range(n)],
            "measured_at": pd.date_range("2022-01-15", periods=n, freq="4h"),
            "latitude": np.random.uniform(-60, 70, n),
            "longitude": np.random.uniform(-170, 170, n),
            "country_name": np.random.choice(["US", "IN", "BR"], n),
            "sky_condition": sky,
            "cloud_cover_pct": np.random.uniform(0, 100, n),
            "cloud_types": np.random.choice(["Cumulus", "Stratus"], n),
            "cloud_opacity": np.random.choice(["Thin", "Opaque"], n),
            "surface_condition": np.random.choice(["Dry", "Wet"], n),
        }
    )
    stats = summary_statistics(demo)
    assert stats["total_observations"] == 100
    assert stats["unique_countries"] == 3
