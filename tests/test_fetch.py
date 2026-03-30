"""Tests for globe_cloud_insights.fetch."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import responses

from globe_cloud_insights.fetch import (
    _checksum,
    _date_range_chunks,
    _features_to_records,
    build_api_url,
    fetch_globe_data,
)


class TestBuildApiUrl:
    def test_default_parameters(self):
        url = build_api_url()
        assert "sky_conditions" in url
        assert "2022-01-15" in url
        assert "2022-02-15" in url
        assert "geojson=TRUE" in url
        assert "sample=FALSE" in url

    def test_custom_parameters(self):
        url = build_api_url(
            protocol="aerosols",
            start_date="2023-01-01",
            end_date="2023-06-01",
            geojson=False,
            sample=True,
        )
        assert "aerosols" in url
        assert "2023-01-01" in url
        assert "geojson=FALSE" in url
        assert "sample=TRUE" in url

    def test_url_starts_with_base(self):
        url = build_api_url()
        assert url.startswith("https://api.globe.gov/")


class TestDateRangeChunks:
    def test_single_week(self):
        chunks = _date_range_chunks("2022-01-15", "2022-01-22", chunk_days=7)
        assert len(chunks) == 1
        assert chunks[0] == ("2022-01-15", "2022-01-22")

    def test_multiple_chunks(self):
        chunks = _date_range_chunks("2022-01-15", "2022-02-15", chunk_days=7)
        assert len(chunks) >= 4
        assert chunks[0][0] == "2022-01-15"
        assert chunks[-1][1] == "2022-02-15"

    def test_small_chunk(self):
        chunks = _date_range_chunks("2022-01-15", "2022-01-17", chunk_days=1)
        assert len(chunks) == 2

    def test_exact_boundary(self):
        chunks = _date_range_chunks("2022-01-01", "2022-01-08", chunk_days=7)
        assert len(chunks) == 1

    def test_empty_range(self):
        chunks = _date_range_chunks("2022-01-15", "2022-01-15", chunk_days=7)
        assert len(chunks) == 0


class TestFeaturesToRecords:
    def test_basic_extraction(self):
        features = [
            {
                "geometry": {"type": "Point", "coordinates": [-77.0, 38.9]},
                "properties": {"pid": "P1", "measuredDate": "2022-01-15"},
            }
        ]
        records = _features_to_records(features)
        assert len(records) == 1
        assert records[0]["longitude"] == -77.0
        assert records[0]["latitude"] == 38.9
        assert records[0]["pid"] == "P1"

    def test_missing_geometry(self):
        features = [{"properties": {"pid": "P2"}}]
        records = _features_to_records(features)
        assert records[0]["longitude"] is None
        assert records[0]["latitude"] is None

    def test_empty_features(self):
        records = _features_to_records([])
        assert records == []

    def test_null_coordinates(self):
        features = [
            {
                "geometry": {"type": "Point", "coordinates": [None, None]},
                "properties": {"pid": "P3"},
            }
        ]
        records = _features_to_records(features)
        assert records[0]["longitude"] is None
        assert records[0]["latitude"] is None


class TestChecksum:
    def test_consistent_hash(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello world")
        h1 = _checksum(f)
        h2 = _checksum(f)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_different_content(self, tmp_path: Path):
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("hello")
        f2.write_text("world")
        assert _checksum(f1) != _checksum(f2)


class TestFetchGlobeData:
    @responses.activate
    def test_fetch_with_api(self, tmp_path: Path, sample_geojson_response: dict):
        """Test fetch with mocked API responses."""
        responses.add(
            responses.GET,
            "https://api.globe.gov/search/v1/measurement/protocol/measureddate",
            json=sample_geojson_response,
            status=200,
        )
        # May need multiple chunks
        for _ in range(10):
            responses.add(
                responses.GET,
                "https://api.globe.gov/search/v1/measurement/protocol/measureddate",
                json=sample_geojson_response,
                status=200,
            )

        df = fetch_globe_data(
            start_date="2022-01-15",
            end_date="2022-01-22",
            output_dir=tmp_path,
            chunk_days=7,
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "longitude" in df.columns
        assert "latitude" in df.columns

    def test_fetch_uses_cache(self, tmp_path: Path):
        """Test that existing file is reused without API calls."""
        csv = tmp_path / "globe_clouds_2022.csv"
        pd.DataFrame({"latitude": [1.0], "longitude": [2.0]}).to_csv(csv, index=False)

        df = fetch_globe_data(output_dir=tmp_path)
        assert len(df) == 1
        assert df["latitude"].iloc[0] == 1.0

    @responses.activate
    def test_fetch_handles_empty_response(self, tmp_path: Path):
        """Test graceful handling of empty API response."""
        responses.add(
            responses.GET,
            "https://api.globe.gov/search/v1/measurement/protocol/measureddate",
            json={"type": "FeatureCollection", "features": []},
            status=200,
        )
        for _ in range(10):
            responses.add(
                responses.GET,
                "https://api.globe.gov/search/v1/measurement/protocol/measureddate",
                json={"type": "FeatureCollection", "features": []},
                status=200,
            )

        df = fetch_globe_data(
            start_date="2022-01-15",
            end_date="2022-01-22",
            output_dir=tmp_path,
            chunk_days=7,
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
