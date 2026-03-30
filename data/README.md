# Data Directory

This directory contains raw and processed datasets for the GLOBE Cloud Insights project.

## Data Source

**Primary source:** NASA GLOBE Observer Clouds protocol data, accessed via the [GLOBE API](https://www.globe.gov/globe-data/globe-api).

**Citation:** Global Learning and Observations to Benefit the Environment (GLOBE) Program, 2024, globe.gov

**GLOBE data policy:** GLOBE makes its data available to everyone and promotes full and open sharing of its data for educational and scientific purposes.

## Sample Dataset

A 500-row sample is committed to this repository so that first-time visitors
can explore the dashboard, run the notebooks, and execute the tests without
needing API access or any data download step. The sample is representative of
the full GLOBE Cloud Challenge 2022 dataset and covers all sky conditions,
multiple countries, and the full challenge date range.

## Directory Structure

```
data/
├── raw/                        # Raw data as retrieved from the GLOBE API
│   ├── globe_clouds_2022.csv   # 500-row sample (committed)
│   └── .gitkeep
├── processed/                  # Cleaned, analysis-ready outputs
│   ├── globe_clouds_2022_clean.parquet  # Cleaned sample (committed)
│   └── .gitkeep
└── README.md                   # This file
```

## Provenance

| Field | Value |
| --- | --- |
| **API endpoint** | `https://api.globe.gov/search/v1/measurement/protocol/measureddate` |
| **Protocol** | `sky_conditions` |
| **Date range** | 2022-01-15 to 2022-02-15 |
| **Format** | GeoJSON (converted to CSV, then cleaned to Parquet) |
| **Retrieval method** | Weekly chunked API calls (see `src/globe_cloud_insights/fetch.py`) |

## Schema (Cleaned Dataset)

| Column | Type | Description |
| --- | --- | --- |
| `observation_id` | str | Unique identifier for each observation |
| `measured_at` | datetime64[ns] | UTC timestamp of the observation |
| `latitude` | float64 | Latitude in decimal degrees (WGS 84) |
| `longitude` | float64 | Longitude in decimal degrees (WGS 84) |
| `country_name` | str | Country where the observation was made |
| `sky_condition` | category | Reported sky condition (e.g. Clear, Scattered, Overcast) |
| `cloud_cover_pct` | float64 | Estimated cloud cover percentage (0-100) |
| `cloud_types` | str | Comma-separated list of cloud genera observed |
| `cloud_opacity` | str | Reported cloud opacity (Transparent, Thin, Opaque) |
| `surface_condition` | str | Reported surface condition at observation site |

## Quality Filters Applied

1. **Coordinate completeness:** Rows missing latitude or longitude are dropped.
2. **Coordinate validity:** Latitude must be in [-90, 90]; longitude in [-180, 180].
3. **Timestamp presence:** Rows without a `measured_at` timestamp are dropped.
4. **Cloud cover derivation:** Where `cloud_cover_pct` is missing, it is inferred from the sky condition label using the GLOBE protocol mapping (Clear → 0%, Few → 15%, Scattered → 40%, Broken → 70%, Overcast → 95%, Obscured → 100%).

## Privacy Note

Observation coordinates are publicly available through the GLOBE Program's open data policy. However, users of this dataset should exercise care to avoid sensitive inference about individual observers — especially when observations are at high spatial resolution. Do not attempt to identify or contact individual participants from coordinate data.

## Reproducing the Dataset

```bash
# From the project root:
python -c "from globe_cloud_insights.fetch import fetch_globe_data; fetch_globe_data()"
python -c "from globe_cloud_insights.clean import clean_data; clean_data()"
```

Or run `notebooks/01_fetch_and_clean.ipynb` for the full interactive pipeline.
