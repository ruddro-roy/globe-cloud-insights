# Tutorial: Getting Started with GLOBE Cloud Insights

Welcome! This tutorial walks you through everything you need to start exploring NASA citizen-science cloud data — whether you're a student, educator, researcher, or curious visitor.

## What You'll Be Exploring

During the 2022 NASA GLOBE Cloud Challenge, thousands of volunteers across 89 countries looked up at the sky and recorded what they saw — cloud types, sky conditions, and coverage levels. This project makes that data visual and interactive through a dashboard you can run in your browser.

## Prerequisites

- **For the dashboard:** Python 3.10 or later (or use a zero-install option below)
- **For notebooks:** Jupyter (included if you install with `[notebooks]`)
- **For everything:** Git
- **Optional:** Docker for containerized usage

## Quick Setup

### Option 1: Zero Install (Recommended for Beginners)

The fastest way to explore is through your browser — no software installation needed:

- **Binder:** Click the "Launch Binder" badge in the README. A cloud-hosted Jupyter environment opens with everything pre-installed. From there, open a terminal and run `streamlit run app/streamlit_app.py`.
- **GitHub Codespaces:** Click "Code > Codespaces > New codespace" on the GitHub repository page. The devcontainer sets up everything automatically.

### Option 2: Local Installation

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

### Option 3: Docker

```bash
docker build -t globe-cloud-insights .
docker run -p 8501:8501 globe-cloud-insights
```

Then open http://localhost:8501 in your browser.

## Using the Dashboard

### Launching

```bash
streamlit run app/streamlit_app.py
```

The dashboard opens in your browser automatically. If not, go to http://localhost:8501.

### What You'll See

The dashboard has four main views, accessible through tabs at the top:

1. **World Map** — Every observation plotted as a dot on a world map. Dots cluster together where many observations were made nearby. Zoom in to see individual points, and click a dot to see its sky condition and cloud cover.

2. **Timeline** — A bar chart showing how many observations were submitted each day. Peaks often align with school days or organized events. Dips usually correspond to weekends.

3. **Patterns & Distributions** — Three charts that summarize the data:
   - A donut chart showing how often each sky condition was reported
   - A histogram of cloud cover percentages
   - A bar chart of the top contributing countries

4. **Browse & Download** — A scrollable table of individual observations. Use the download button to save the filtered data as a CSV file for your own analysis.

### Filtering the Data

The sidebar on the left has three filter controls:

- **Date Range** — Narrow to a specific set of days within the challenge period
- **Sky Condition** — Show only observations matching specific sky conditions (e.g., just "Overcast" and "Broken")
- **Cloud Type** — Focus on specific cloud genera like Cumulus or Cirrus

All charts and the map update instantly when you change a filter. Leave filters at their defaults to see the full dataset.

### Tips for Educators

- **Classroom activity:** Have students filter to their country and describe what they see
- **Discussion prompt:** Compare weekday vs. weekend observation counts — why the difference?
- **Data download:** Students can download filtered CSV files and create their own charts in Google Sheets or Excel
- **Cloud identification:** Use the [glossary](glossary.md) alongside the dashboard to teach cloud genera

## Exploring the Notebooks

For a deeper dive into the data and code:

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

Open `notebooks/02_exploratory_analysis.ipynb` for interactive exploration, including:

- Summary statistics
- Temporal trends (daily observation counts)
- Spatial distribution maps (Folium)
- Sky condition and cloud cover distributions
- Top contributing countries

### Step 3: Run the Tests

```bash
pytest -v
```

## Key Concepts

The GLOBE Clouds protocol asks observers to report:

1. **Cloud types** — which of the 10 cloud genera are visible (e.g. Cumulus, Cirrus, Stratus)
2. **Sky condition** — overall cloud coverage category (Clear, Few, Scattered, Broken, Overcast, or Obscured)
3. **Cloud opacity** — how transparent or opaque the clouds are
4. **Surface conditions** — ground-level conditions at the time of observation

Observations made within 15 minutes of a satellite overpass are matched with satellite data for ground-truth validation — connecting what people see from the ground with what satellites measure from space.

## Next Steps

- Read the **[Glossary](glossary.md)** for cloud-observation terminology and definitions
- Check **[CONTRIBUTING.md](../CONTRIBUTING.md)** if you want to contribute
- Explore the **`src/globe_cloud_insights/`** package for the full Python API
- Visit **[GLOBE Observer](https://observer.globe.gov)** to start making your own observations
