"""Tests for globe_cloud_insights.clean."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from globe_cloud_insights.clean import (
    SCHEMA,
    _sky_condition_to_pct,
    clean_data,
    get_schema_markdown,
)


class TestSkyConditionToPct:
    def test_clear(self):
        assert _sky_condition_to_pct("Clear") == 0.0

    def test_overcast(self):
        assert _sky_condition_to_pct("Overcast") == 95.0

    def test_obscured(self):
        assert _sky_condition_to_pct("Obscured") == 100.0

    def test_scattered(self):
        assert _sky_condition_to_pct("Scattered") == 40.0

    def test_case_insensitive(self):
        assert _sky_condition_to_pct("clear") == 0.0
        assert _sky_condition_to_pct("OVERCAST") == 95.0

    def test_none_input(self):
        assert _sky_condition_to_pct(None) is None

    def test_unknown_value(self):
        assert _sky_condition_to_pct("Unknown") is None

    def test_whitespace(self):
        assert _sky_condition_to_pct("  Few  ") == 15.0

    def test_non_string(self):
        assert _sky_condition_to_pct(42) is None


class TestGetSchemaMarkdown:
    def test_returns_string(self):
        md = get_schema_markdown()
        assert isinstance(md, str)

    def test_contains_header(self):
        md = get_schema_markdown()
        assert "Column" in md
        assert "Type" in md
        assert "Description" in md

    def test_contains_all_columns(self):
        md = get_schema_markdown()
        for col in SCHEMA:
            assert col in md

    def test_is_valid_markdown_table(self):
        md = get_schema_markdown()
        lines = md.strip().split("\n")
        assert len(lines) >= 3  # header + separator + at least 1 row
        assert lines[1].startswith("|")
        assert "---" in lines[1]


class TestSchema:
    def test_schema_has_required_columns(self):
        required = [
            "observation_id",
            "measured_at",
            "latitude",
            "longitude",
            "sky_condition",
            "cloud_cover_pct",
        ]
        for col in required:
            assert col in SCHEMA

    def test_schema_entries_have_dtype_and_description(self):
        for col, meta in SCHEMA.items():
            assert "dtype" in meta, f"{col} missing dtype"
            assert "description" in meta, f"{col} missing description"


class TestExtractNested:
    def test_dict_blob_with_sky_conditions(self, tmp_path: Path):
        """Test cleaning when data column contains JSON dicts."""
        import json

        raw = tmp_path / "raw.csv"
        blob = json.dumps(
            {
                "sky_conditions": {
                    "value": "Broken",
                    "cloudOpacity": "Opaque",
                    "surfaceCondition": "Wet",
                },
                "clouds": [{"type": "Cumulus"}, {"type": "Stratus"}],
            }
        )
        pd.DataFrame(
            {
                "pid": ["A"],
                "measuredDate": ["2022-01-15T12:00:00"],
                "latitude": [10.0],
                "longitude": [20.0],
                "data": [blob],
            }
        ).to_csv(raw, index=False)
        output = tmp_path / "clean.parquet"
        df, _ = clean_data(raw_path=raw, output_path=output)
        assert len(df) == 1
        assert df["sky_condition"].iloc[0] == "Broken"
        assert "Cumulus" in str(df["cloud_types"].iloc[0])
        assert df["cloud_opacity"].iloc[0] == "Opaque"
        assert df["surface_condition"].iloc[0] == "Wet"

    def test_string_blob_treated_as_sky(self, tmp_path: Path):
        """Test when data column contains a plain string."""
        raw = tmp_path / "raw.csv"
        pd.DataFrame(
            {
                "pid": ["A"],
                "measuredDate": ["2022-01-15T12:00:00"],
                "latitude": [10.0],
                "longitude": [20.0],
                "data": ["Clear"],
            }
        ).to_csv(raw, index=False)
        output = tmp_path / "clean.parquet"
        df, _ = clean_data(raw_path=raw, output_path=output)
        assert len(df) == 1

    def test_cloud_types_as_strings(self, tmp_path: Path):
        """Test when clouds list contains plain strings."""
        import json

        raw = tmp_path / "raw.csv"
        blob = json.dumps(
            {
                "sky_conditions": {"value": "Few"},
                "clouds": ["Cirrus", "Altocumulus"],
            }
        )
        pd.DataFrame(
            {
                "pid": ["A"],
                "measuredDate": ["2022-01-16T12:00:00"],
                "latitude": [15.0],
                "longitude": [25.0],
                "data": [blob],
            }
        ).to_csv(raw, index=False)
        output = tmp_path / "clean.parquet"
        df, _ = clean_data(raw_path=raw, output_path=output)
        assert "Cirrus" in str(df["cloud_types"].iloc[0])
        assert "Altocumulus" in str(df["cloud_types"].iloc[0])

    def test_invalid_json_in_data(self, tmp_path: Path):
        """Test graceful handling of malformed JSON."""
        raw = tmp_path / "raw.csv"
        pd.DataFrame(
            {
                "pid": ["A"],
                "measuredDate": ["2022-01-17T12:00:00"],
                "latitude": [20.0],
                "longitude": [30.0],
                "data": ["{invalid json}"],
            }
        ).to_csv(raw, index=False)
        output = tmp_path / "clean.parquet"
        df, _ = clean_data(raw_path=raw, output_path=output)
        assert len(df) == 1

    def test_missing_lat_lon_columns(self, tmp_path: Path):
        """Test when raw data has no lat/lon columns at all."""
        raw = tmp_path / "raw.csv"
        pd.DataFrame(
            {
                "pid": ["A", "B"],
                "measuredDate": ["2022-01-15", "2022-01-16"],
                "skyCondition": ["Clear", "Few"],
            }
        ).to_csv(raw, index=False)
        output = tmp_path / "clean.parquet"
        df, prov = clean_data(raw_path=raw, output_path=output)
        # All rows should be dropped since lat/lon are None
        assert len(df) == 0
        assert prov["dropped_total"] == 2


class TestCleanData:
    def test_basic_cleaning(self, sample_raw_csv: Path, tmp_path: Path):
        output = tmp_path / "processed" / "clean.parquet"
        df, provenance = clean_data(raw_path=sample_raw_csv, output_path=output)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert output.exists()
        assert "records_raw" in provenance
        assert "records_final" in provenance
        assert provenance["records_final"] <= provenance["records_raw"]

    def test_drops_missing_coords(self, tmp_path: Path):
        raw = tmp_path / "raw.csv"
        pd.DataFrame(
            {
                "pid": ["A", "B", "C"],
                "measuredDate": ["2022-01-15", "2022-01-16", "2022-01-17"],
                "latitude": [10.0, None, 20.0],
                "longitude": [20.0, 30.0, None],
                "skyCondition": ["Clear", "Few", "Scattered"],
            }
        ).to_csv(raw, index=False)
        output = tmp_path / "clean.parquet"
        df, prov = clean_data(raw_path=raw, output_path=output)
        assert len(df) == 1  # Only row A has both lat and lon
        assert prov["dropped_total"] == 2

    def test_drops_out_of_range_coords(self, tmp_path: Path):
        raw = tmp_path / "raw.csv"
        pd.DataFrame(
            {
                "pid": ["A", "B"],
                "measuredDate": ["2022-01-15", "2022-01-16"],
                "latitude": [10.0, 999.0],
                "longitude": [20.0, 20.0],
                "skyCondition": ["Clear", "Few"],
            }
        ).to_csv(raw, index=False)
        output = tmp_path / "clean.parquet"
        df, _ = clean_data(raw_path=raw, output_path=output)
        assert len(df) == 1

    def test_parquet_readable(self, sample_raw_csv: Path, tmp_path: Path):
        output = tmp_path / "processed" / "clean.parquet"
        clean_data(raw_path=sample_raw_csv, output_path=output)
        reloaded = pd.read_parquet(output)
        assert len(reloaded) > 0

    def test_assigns_observation_ids(self, sample_raw_csv: Path, tmp_path: Path):
        output = tmp_path / "processed" / "clean.parquet"
        df, _ = clean_data(raw_path=sample_raw_csv, output_path=output)
        assert df["observation_id"].notna().all()

    def test_provenance_metadata(self, sample_raw_csv: Path, tmp_path: Path):
        output = tmp_path / "processed" / "clean.parquet"
        _, prov = clean_data(raw_path=sample_raw_csv, output_path=output)
        assert "retrieval_timestamp" in prov
        assert "quality_notes" in prov
        assert "source_file" in prov
        assert "output_file" in prov

    def test_cloud_cover_pct_computed(self, tmp_path: Path):
        raw = tmp_path / "raw.csv"
        pd.DataFrame(
            {
                "pid": ["A", "B"],
                "measuredDate": ["2022-01-15", "2022-01-16"],
                "latitude": [10.0, 20.0],
                "longitude": [20.0, 30.0],
                "skyCondition": ["Clear", "Overcast"],
            }
        ).to_csv(raw, index=False)
        output = tmp_path / "clean.parquet"
        df, _ = clean_data(raw_path=raw, output_path=output)
        # Should have computed cloud_cover_pct from sky condition
        assert "cloud_cover_pct" in df.columns
