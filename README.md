# GLOBE Cloud Insights

[![CI](https://github.com/ruddro-roy/globe-cloud-insights/actions/workflows/ci.yml/badge.svg)](https://github.com/ruddro-roy/globe-cloud-insights/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ruddro-roy/globe-cloud-insights/main)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ruddro-roy/globe-cloud-insights)

**An interactive dashboard and data pipeline for exploring NASA citizen-science cloud observations from the GLOBE Observer Clouds 2022 Challenge.**

> 42,700+ cloud observations from 89 countries, 7 continents, and 49,450 satellite matches — collected by citizen scientists and made explorable here.

---

## What Is This?

During the [NASA GLOBE Cloud Challenge 2022](https://observer.globe.gov/do-globe-observer/challenges/cloudchallenge-2022) (January 15 – February 15, 2022), thousands of volunteers around the world looked up at the sky, identified cloud types, and submitted observations through the GLOBE Observer app. This project takes that dataset and turns it into an interactive, visual experience that anyone can explore — no coding required.

### What Can You Do Here?

- **Explore a live dashboard** showing cloud observations on a world map
- **Filter by date, sky condition, and cloud type** to focus on what interests you
- **See charts** of daily observation trends, sky condition breakdowns, and top contributing countries
- **Download the data** as a CSV for classroom activities, homework, or your own research
- **Learn** about cloud classification, citizen science, and how ground observations connect to satellite data


## The Story Behind This Project

Ever looked up at the sky and wondered what stories those clouds tell? Me too. Out of sheer curiosity, I spent May 5 – Oct 1, 2022 volunteering remotely with NASA's GLOBE Observer (Clouds) program. That experience — standing outside with a phone pointed at the sky, carefully identifying cloud genera while a satellite passed overhead — sparked this open-source project.

The response to the 2022 Cloud Challenge was remarkable: NASA reported over 42,700 cloud observations from 89 countries across all 7 continents, with more than 49,450 satellite matches (over double the 20,000 goal), 108,000+ new sky photographs, and 321,100+ CLOUD GAZE classifications.

This project makes that dataset explorable, visual, and educational.

---

## Dashboard Preview

The dashboard includes four main views, each designed to help you understand a different aspect of the data:

| View | What it shows |
| --- | --- |
| **World Map** | Every observation plotted on a globe, with clusters showing hotspots of activity |
| **Timeline** | Daily observation counts, revealing peaks on school days and organized events |
| **Patterns & Distributions** | Sky condition breakdown (donut chart), cloud cover spread (histogram), top countries (bar chart) |
| **Browse & Download** | Searchable table of raw observations with one-click CSV download |

The dashboard uses plain-language labels, guided interpretation callouts, and sensible defaults so that first-time visitors can understand the data without any prior training.

*Run `streamlit run app/streamlit_app.py` to see it live, or launch instantly via Binder/Codespaces above.*

---

## Quick Start

### No installation needed

| Method | Link |
| --- | --- |
| **Binder** (launches in browser) | [![Launch Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ruddro-roy/globe-cloud-insights/main) |
| **GitHub Codespaces** | [![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ruddro-roy/globe-cloud-insights) |

### Local setup (3 commands)

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

---

## How the Data Pipeline Works

```
GLOBE API  ──>  Raw CSV  ──>  Quality Filters  ──>  Tidy Parquet  ──>  Dashboard
                (cached)      - Valid coords         (analysis-ready)
                              - Valid timestamps
                              - Bounds checks
```

| Stage | Code | What it does |
| --- | --- | --- |
| **Fetch** | `src/globe_cloud_insights/fetch.py` | Downloads data from the GLOBE API in weekly chunks, with SHA-256 checksum caching |
| **Clean** | `src/globe_cloud_insights/clean.py` | Normalizes columns, validates coordinates, derives cloud cover % from sky condition labels, exports Parquet |
| **Analyze** | `src/globe_cloud_insights/analysis.py` | Descriptive statistics, temporal aggregation, spatial mapping, Plotly/Folium charts |
| **Explore** | `app/streamlit_app.py` | Interactive Streamlit dashboard with filters, maps, charts, and data export |

### Quality Filters Applied

- Rows missing latitude or longitude: **dropped**
- Coordinates outside [-90, 90] / [-180, 180]: **dropped**
- Rows without timestamps: **dropped**
- Cloud cover %: inferred from sky condition labels where missing (Clear = 0%, Few = 15%, Scattered = 40%, Broken = 70%, Overcast = 95%, Obscured = 100%)

---

## Data Provenance

### Primary Source

All observation data comes from the **GLOBE Program**, accessed through the [GLOBE API](https://www.globe.gov/globe-data/globe-api).

| Detail | Value |
| --- | --- |
| **Protocol** | [GLOBE Clouds (sky_conditions)](https://www.globe.gov/web/atmosphere/protocols/clouds) |
| **Date range** | January 15 – February 15, 2022 |
| **Campaign** | [NASA GLOBE Cloud Challenge 2022](https://observer.globe.gov/do-globe-observer/challenges/cloudchallenge-2022) |
| **API endpoint** | `api.globe.gov/search/v1/measurement/protocol/measureddate` |
| **Format** | GeoJSON (chunked weekly to respect the 1M-record API limit) |

### Citation

> Global Learning and Observations to Benefit the Environment (GLOBE) Program, *date data was accessed*, globe.gov

### Ethics Note on Location Privacy

Observation coordinates are publicly available through the GLOBE Program's open data policy. However, we encourage responsible use: avoid sensitive inference about individual observers, especially at high spatial resolution.

---

## Notebook Analysis

For a deeper look at the data, two Jupyter notebooks walk through the full pipeline:

- [**01_fetch_and_clean.ipynb**](https://nbviewer.org/github/ruddro-roy/globe-cloud-insights/blob/main/notebooks/01_fetch_and_clean.ipynb) — Reproducible data pipeline with provenance tracking
- [**02_exploratory_analysis.ipynb**](https://nbviewer.org/github/ruddro-roy/globe-cloud-insights/blob/main/notebooks/02_exploratory_analysis.ipynb) — Statistical summaries, spatial maps, temporal trends

---

## Documentation

- **[Glossary](docs/glossary.md)** — Cloud genera, sky conditions, opacity levels, and other key terms
- **[Tutorial](docs/tutorial.md)** — Step-by-step guide to setup, exploration, and analysis
- **[Data Schema](data/README.md)** — Column definitions, quality filters, and provenance details

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

**Quick version:**

1. Fork the repo
2. Create a feature branch
3. Make changes and add tests
4. Run `black`, `isort`, `flake8`, `mypy`, `pytest`
5. Open a pull request

---

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
- **Researchers:** Colon Robles et al. (2020), Dodson et al. (2022) for foundational work on GLOBE Observer data quality and intense observation periods

### Key References

1. NASA GLOBE Cloud Challenge 2022 — https://observer.globe.gov/do-globe-observer/challenges/cloudchallenge-2022
2. GLOBE Clouds Protocol — https://www.globe.gov/web/atmosphere/protocols/clouds
3. NASA: Clouds in a Changing Climate — https://science.nasa.gov/science-research/earth-science/clouds-in-a-changing-climate/
4. GLOBE Data Access — https://observer.globe.gov/get-data
5. GLOBE API — https://www.globe.gov/globe-data/globe-api
6. Colon Robles et al. (2020). GLOBE Observer Data: 2016-2019. *Earth and Space Science*, 7(8). [doi:10.1029/2020EA001175](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2020EA001175)
7. Dodson et al. (2022). Intense Observation Periods. *Earth and Space Science*, 9(3). [doi:10.1029/2021EA002058](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2021EA002058)
8. NASA Technical Report on GLOBE-SCC — https://ntrs.nasa.gov/api/citations/20230006162/downloads/GLOBE-SCC_paper-rev-v4.pdf

---

## License

This project is licensed under the [MIT License](LICENSE).

You are free to use, modify, and distribute this work. If you use the GLOBE data in your own projects, please credit the GLOBE Program per their citation guidance above.

## Roadmap

- [ ] Expand dataset to cover the full 2022 calendar year
- [ ] Add satellite overpass matching analysis
- [ ] Integrate CLOUD GAZE classification data
- [ ] Add machine learning notebooks (cloud type prediction from metadata)
- [ ] Deploy the dashboard to Streamlit Community Cloud
- [ ] Create classroom-ready lesson plans and worksheets
- [ ] Add multilingual support for broader global access
