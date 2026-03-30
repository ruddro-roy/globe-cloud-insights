"""Tests for globe_cloud_insights.config."""

from pathlib import Path

from globe_cloud_insights.config import (
    CLEAN_PARQUET_PATH,
    CLOUD_GENERA,
    DATA_CITATION,
    DATA_DIR,
    GLOBE_API_BASE,
    GLOBE_END_DATE,
    GLOBE_PROTOCOL,
    GLOBE_START_DATE,
    PROCESSED_DIR,
    PROJECT_ROOT,
    RAW_DIR,
    SKY_CONDITIONS,
)


def test_project_root_exists():
    assert PROJECT_ROOT.exists()


def test_data_dirs_are_under_project():
    assert str(DATA_DIR).startswith(str(PROJECT_ROOT))
    assert str(RAW_DIR).startswith(str(DATA_DIR))
    assert str(PROCESSED_DIR).startswith(str(DATA_DIR))


def test_api_base_url():
    assert GLOBE_API_BASE.startswith("https://")
    assert "globe.gov" in GLOBE_API_BASE


def test_protocol_is_sky_conditions():
    assert GLOBE_PROTOCOL == "sky_conditions"


def test_date_range():
    assert GLOBE_START_DATE == "2022-01-15"
    assert GLOBE_END_DATE == "2022-02-15"


def test_cloud_genera_count():
    assert len(CLOUD_GENERA) == 10
    assert "Cumulus" in CLOUD_GENERA
    assert "Cumulonimbus" in CLOUD_GENERA


def test_sky_conditions_count():
    assert len(SKY_CONDITIONS) == 7
    assert "Clear" in SKY_CONDITIONS
    assert "Overcast" in SKY_CONDITIONS


def test_data_citation_template():
    citation = DATA_CITATION.format(access_date="2024-01-01")
    assert "GLOBE" in citation
    assert "2024-01-01" in citation
    assert "globe.gov" in citation


def test_paths_are_path_objects():
    assert isinstance(RAW_DIR, Path)
    assert isinstance(PROCESSED_DIR, Path)
    assert isinstance(CLEAN_PARQUET_PATH, Path)
    assert str(CLEAN_PARQUET_PATH).endswith(".parquet")
