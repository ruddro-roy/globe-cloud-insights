# Tutorial: Getting Started with GLOBE Cloud Insights

Welcome! This tutorial walks you through the project from setup to exploration.

## Prerequisites

- Python 3.10 or later
- Git
- (Optional) Docker for containerised usage

## Quick Setup

### Option 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/ruddro-roy/globe-cloud-insights.git
cd globe-cloud-insights

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install the package with development extras
pip install -e ".[dev,notebooks]"
```

### Option 2: Docker

```bash
docker build -t globe-cloud-insights .
docker run -p 8501:8501 globe-cloud-insights
```

Then open http://localhost:8501 in your browser.

### Option 3: Binder (Zero Install)

Click the Binder badge in the README to launch a cloud-hosted Jupyter
environment with everything pre-installed.

### Option 4: GitHub Codespaces

Click "Code → Codespaces → New codespace" on the GitHub repository page.
The devcontainer configuration will set up everything automatically.

## Workflow

### Step 1: Fetch and Clean the Data

Open `notebooks/01_fetch_and_clean.ipynb` or run:

```python
from globe_cloud_insights.fetch import fetch_globe_data
from globe_cloud_insights.clean import clean_data

# Download from GLOBE API (cached after first run)
df_raw = fetch_globe_data()

# Clean and save as Parquet
df_clean, provenance = clean_data()
print(f"Cleaned {provenance['records_final']} records")
```

### Step 2: Explore the Data

Open `notebooks/02_exploratory_analysis.ipynb` for interactive exploration,
including:

- Summary statistics
- Temporal trends (daily observation counts)
- Spatial distribution maps (Folium)
- Sky condition and cloud cover distributions
- Top contributing countries

### Step 3: Launch the Dashboard

```bash
streamlit run app/streamlit_app.py
```

The dashboard provides:

- **Interactive map** with clustered observation markers
- **Date, sky condition, and cloud type filters**
- **Time series** of daily observations
- **Distribution charts** for sky conditions and cloud cover
- **Filterable data table** with CSV download

### Step 4: Run the Tests

```bash
pytest -v
```

## Key Concepts

The GLOBE Clouds protocol asks observers to report:

1. **Cloud types** — which of the 10 cloud genera are visible
2. **Sky condition** — overall cloud coverage category (Clear to Obscured)
3. **Cloud opacity** — how transparent/opaque the clouds are
4. **Surface conditions** — ground-level conditions

Observations made within 15 minutes of a satellite overpass are matched
with satellite data for ground-truth validation.

## Next Steps

- Read `docs/glossary.md` for cloud-observation terminology
- Check `CONTRIBUTING.md` if you want to contribute
- Explore the `src/globe_cloud_insights/` package for the full Python API
