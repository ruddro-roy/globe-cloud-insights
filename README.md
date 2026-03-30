# GLOBE Cloud Insights

[![CI](https://github.com/ruddro-roy/globe-cloud-insights/actions/workflows/ci.yml/badge.svg)](https://github.com/ruddro-roy/globe-cloud-insights/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ruddro-roy/globe-cloud-insights/main)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ruddro-roy/globe-cloud-insights)

**An interactive, research-quality data-visualization project exploring NASA citizen-science cloud observations from the GLOBE Observer Clouds 2022 Challenge.**

---

## The Story Behind This Project

Ever looked up at the sky and wondered what stories those clouds tell? Me too. Out of sheer curiosity, I spent May 5 -- Oct 1, 2022 volunteering remotely with NASA's GLOBE Observer (Clouds) program. That experience --- standing outside with a phone pointed at the sky, carefully identifying cloud genera while a satellite passed overhead --- sparked this open-source project.

The NASA GLOBE Cloud Challenge 2022 ran from January 15 to February 15, 2022, inviting citizen scientists around the world to observe and classify clouds. The response was remarkable: NASA reported over 42,700 cloud observations from 89 countries across all 7 continents, with more than 49,450 satellite matches (over double the 20,000 goal), 108,000+ new sky photographs, and 321,100+ CLOUD GAZE classifications.

This project takes that rich dataset and makes it explorable, visual, and educational.

## Mission & Learning Goals

**Mission:** Make NASA citizen-science cloud data accessible, interactive, and pedagogically useful for educators, students, and researchers.

**What you'll learn:**

- How citizen scientists contribute to real climate research
- The basics of cloud classification (10 genera, sky conditions, opacity)
- How ground-based observations compare with satellite measurements
- Practical data science: API access, data cleaning, visualisation, and reproducibility

## Quick Start (90 Seconds)

### Zero-install options

| Method | Link |
| --- | --- |
| **Binder** | [![Launch Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ruddro-roy/globe-cloud-insights/main) |
| **Codespaces** | [![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ruddro-roy/globe-cloud-insights) |

### Local setup

```bash
git clone https://github.com/ruddro-roy/globe-cloud-insights.git
cd globe-cloud-insights
pip install -e ".[dev,notebooks]"
streamlit run app/streamlit_app.py
```

### Docker

```bash
docker build -t globe-cloud-insights .
docker run -p 8501:8501 globe-cloud-insights
# Open http://localhost:8501
```

## Data Provenance

### Primary Source

All observation data comes from the **GLOBE Program**, accessed through the [GLOBE API](https://www.globe.gov/globe-data/globe-api).

| Detail | Value |
| --- | --- |
| **Protocol** | [GLOBE Clouds (sky_conditions)](https://www.globe.gov/web/atmosphere/protocols/clouds) |
| **Date range** | January 15 -- February 15, 2022 |
| **Campaign** | [NASA GLOBE Cloud Challenge 2022](https://observer.globe.gov/do-globe-observer/challenges/cloudchallenge-2022) |
| **API endpoint** | `api.globe.gov/search/v1/measurement/protocol/measureddate` |
| **Format** | GeoJSON (chunked weekly to respect the 1M-record API limit) |

### Citation

> Global Learning and Observations to Benefit the Environment (GLOBE) Program, *date data was accessed*, globe.gov

### Licensing & Reuse

GLOBE makes its data available to everyone and promotes full and open sharing for educational and scientific purposes. See [GLOBE Terms of Use](https://www.globe.gov).

### Ethics Note on Location Privacy

Observation coordinates are publicly available through the GLOBE Program's open data policy. However, we encourage responsible use: avoid sensitive inference about individual observers, especially at high spatial resolution. Do not attempt to identify or contact participants from coordinate data.

## Methods Overview

### Data Pipeline

```
GLOBE API ──→ Raw CSV ──→ Quality Filters ──→ Tidy Parquet
              (cached)     - Valid coords       (analysis-ready)
                           - Valid timestamps
                           - Bounds checks
```

1. **Fetch** (`src/globe_cloud_insights/fetch.py`): Chunked API retrieval with SHA-256 checksum caching
2. **Clean** (`src/globe_cloud_insights/clean.py`): Column normalisation, coordinate validation, cloud-cover derivation from sky condition labels, and Parquet export
3. **Analyse** (`src/globe_cloud_insights/analysis.py`): Descriptive statistics, temporal aggregation, spatial mapping, and Plotly/Folium visualisation
4. **Explore** (`app/streamlit_app.py`): Interactive Streamlit dashboard with filters, maps, charts, and data export

### Quality Filters

- Rows missing latitude or longitude: **dropped**
- Coordinates outside [-90, 90] / [-180, 180]: **dropped**
- Rows without timestamps: **dropped**
- Cloud cover %: inferred from sky condition labels where missing (Clear=0%, Few=15%, Scattered=40%, Broken=70%, Overcast=95%, Obscured=100%)

## Showcase Gallery

### Interactive Dashboard
The Streamlit dashboard offers four exploration tabs:

- **Map** --- Clustered Folium map of global observations
- **Temporal** --- Daily observation bar chart revealing engagement patterns
- **Distributions** --- Sky condition pie chart, cloud cover histogram, top countries
- **Data Table** --- Filterable, downloadable view of raw observations

*Run `streamlit run app/streamlit_app.py` to see it live, or launch via Binder/Codespaces above.*

### Notebook Analysis
- `notebooks/01_fetch_and_clean.ipynb` --- Reproducible data pipeline with provenance
- `notebooks/02_exploratory_analysis.ipynb` --- Statistical summaries, spatial maps, temporal trends

## Project Structure

```
globe-cloud-insights/
├── README.md                    # You are here
├── LICENSE                      # MIT License
├── pyproject.toml               # Package metadata and tool config
├── requirements.txt             # Pip dependencies
├── CONTRIBUTING.md              # Contribution guidelines
├── .pre-commit-config.yaml      # Code quality hooks
├── Dockerfile                   # Container build
├── .github/
│   ├── workflows/ci.yml         # CI pipeline (lint, test, docs, app check)
│   └── ISSUE_TEMPLATE/          # Bug report and feature request templates
├── .devcontainer/
│   └── devcontainer.json        # GitHub Codespaces / VS Code devcontainer
├── binder/
│   ├── environment.yml          # Binder environment specification
│   └── postBuild                # Post-build setup script
├── src/globe_cloud_insights/
│   ├── __init__.py              # Package root
│   ├── config.py                # Paths, API config, taxonomy constants
│   ├── fetch.py                 # Data acquisition with caching
│   ├── clean.py                 # Cleaning pipeline with provenance
│   └── analysis.py              # Analysis and visualisation helpers
├── app/
│   └── streamlit_app.py         # Interactive Streamlit dashboard
├── notebooks/
│   ├── 01_fetch_and_clean.ipynb # Data pipeline walkthrough
│   └── 02_exploratory_analysis.ipynb  # Exploratory analysis
├── data/
│   ├── README.md                # Data provenance and schema docs
│   ├── raw/                     # Raw API downloads (git-ignored)
│   └── processed/               # Cleaned Parquet (git-ignored)
├── docs/
│   ├── glossary.md              # Cloud-observation terminology
│   └── tutorial.md              # Getting started guide
└── tests/
    ├── conftest.py              # Shared fixtures
    ├── test_config.py           # Config module tests
    ├── test_fetch.py            # Data fetch tests
    ├── test_clean.py            # Cleaning pipeline tests
    ├── test_analysis.py         # Analysis function tests
    └── test_app.py              # Dashboard smoke tests
```

## Contributing

We welcome contributions from educators, students, researchers, and developers!
See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

**Quick version:**

1. Fork the repo
2. Create a feature branch
3. Make changes and add tests
4. Run `black`, `isort`, `flake8`, `mypy`, `pytest`
5. Open a pull request

## Citation & Acknowledgments

### Cite This Repository

```bibtex
@software{globe_cloud_insights_2024,
  author       = {Roy, Ruddro},
  title        = {GLOBE Cloud Insights: Interactive Visualization of NASA
                  GLOBE Observer Clouds 2022 Challenge Data},
  year         = {2024},
  publisher    = {GitHub},
  url          = {https://github.com/ruddro-roy/globe-cloud-insights},
  license      = {MIT}
}
```

### Acknowledgments

- **NASA GLOBE Program** for making citizen-science data openly available
- **GLOBE Observer** volunteers who contributed 42,700+ cloud observations
- **Researchers:** Colón Robles et al. (2020), Dodson et al. (2022) for foundational work on GLOBE Observer data quality and intense observation periods

### Key References

1. NASA GLOBE Cloud Challenge 2022 --- https://observer.globe.gov/do-globe-observer/challenges/cloudchallenge-2022
2. GLOBE Clouds Protocol --- https://www.globe.gov/web/atmosphere/protocols/clouds
3. NASA: Clouds in a Changing Climate --- https://science.nasa.gov/science-research/earth-science/clouds-in-a-changing-climate/
4. GLOBE Data Access --- https://observer.globe.gov/get-data
5. GLOBE API --- https://www.globe.gov/globe-data/globe-api
6. Colón Robles et al. (2020). GLOBE Observer Data: 2016--2019. *Earth and Space Science*, 7(8). [doi:10.1029/2020EA001175](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2020EA001175)
7. Dodson et al. (2022). Intense Observation Periods. *Earth and Space Science*, 9(3). [doi:10.1029/2021EA002058](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2021EA002058)
8. NASA Technical Report on GLOBE-SCC --- https://ntrs.nasa.gov/api/citations/20230006162/downloads/GLOBE-SCC_paper-rev-v4.pdf

## License

This project is licensed under the [MIT License](LICENSE).

You are free to use, modify, and distribute this work. If you use the GLOBE
data in your own projects, please credit the GLOBE Program per their
citation guidance above.

## Roadmap

- [ ] Expand dataset to cover the full 2022 calendar year
- [ ] Add satellite overpass matching analysis
- [ ] Integrate CLOUD GAZE classification data
- [ ] Add machine learning notebooks (cloud type prediction from metadata)
- [ ] Deploy the dashboard to Streamlit Community Cloud
- [ ] Create classroom-ready lesson plans and worksheets
- [ ] Add multilingual support for broader global access

---

*Let's make open science cloud-native and sky-high!*
