"""GLOBE Cloud Insights — Interactive Dashboard.

A Streamlit-based interactive dashboard for exploring NASA GLOBE Observer
Clouds 2022 challenge data. Designed for educators, students, and researchers.

Run with:
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from globe_cloud_insights.analysis import (  # noqa: E402
    daily_observation_counts,
    plot_cloud_cover_histogram,
    plot_daily_counts,
    plot_sky_conditions,
    plot_top_countries,
    sky_condition_distribution,
    summary_statistics,
    top_countries,
)
from globe_cloud_insights.config import (  # noqa: E402
    CLEAN_PARQUET_PATH,
    DATA_CITATION,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GLOBE Cloud Insights",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the cleaned Parquet dataset."""
    if CLEAN_PARQUET_PATH.exists():
        return pd.read_parquet(CLEAN_PARQUET_PATH)
    # Fallback: try to find any parquet in processed dir
    processed = CLEAN_PARQUET_PATH.parent
    parquets = list(processed.glob("*.parquet"))
    if parquets:
        return pd.read_parquet(parquets[0])
    # Generate sample data for demo purposes
    return _generate_demo_data()


def _generate_demo_data() -> pd.DataFrame:
    """Generate synthetic demo data when real data is unavailable."""
    import numpy as np

    np.random.seed(42)
    n = 2000
    dates = pd.date_range("2022-01-15", "2022-02-15", periods=n)
    conditions = ["Clear", "Few", "Scattered", "Broken", "Overcast", "Obscured"]
    cloud_types = [
        "Cumulus",
        "Stratus",
        "Cirrus",
        "Stratocumulus",
        "Altocumulus",
        "Cumulonimbus",
        "Nimbostratus",
    ]
    cover_map = {
        "Clear": 0,
        "Few": 15,
        "Scattered": 40,
        "Broken": 70,
        "Overcast": 95,
        "Obscured": 100,
    }
    sky = np.random.choice(conditions, n)
    countries = np.random.choice(
        [
            "United States",
            "India",
            "Brazil",
            "Germany",
            "Japan",
            "Nigeria",
            "Australia",
            "Mexico",
            "Kenya",
            "France",
        ],
        n,
    )
    return pd.DataFrame(
        {
            "observation_id": [f"OBS-{i:06d}" for i in range(n)],
            "measured_at": dates,
            "latitude": np.random.uniform(-60, 70, n),
            "longitude": np.random.uniform(-170, 170, n),
            "country_name": countries,
            "sky_condition": sky,
            "cloud_cover_pct": [cover_map[s] + np.random.normal(0, 5) for s in sky],
            "cloud_types": np.random.choice(cloud_types, n),
            "cloud_opacity": np.random.choice(["Transparent", "Thin", "Opaque"], n),
            "surface_condition": np.random.choice(["Dry", "Wet", "Snow", "Ice"], n),
        }
    )


# ── Main app ─────────────────────────────────────────────────────────────────
def main():
    """Run the Streamlit dashboard."""
    df = load_data()

    # Ensure datetime
    if "measured_at" in df.columns:
        df["measured_at"] = pd.to_datetime(df["measured_at"], errors="coerce")

    # ── Sidebar filters ──────────────────────────────────────────────────
    st.sidebar.markdown("## Filters")
    st.sidebar.markdown(
        "Use these controls to explore subsets of the GLOBE Cloud "
        "Challenge 2022 observations."
    )

    # Date range
    if "measured_at" in df.columns and not df["measured_at"].isna().all():
        min_date = df["measured_at"].min().date()
        max_date = df["measured_at"].max().date()
        date_range = st.sidebar.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Filter observations by date range",
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            mask = df["measured_at"].dt.date.between(date_range[0], date_range[1])
            df = df[mask]

    # Sky condition
    if "sky_condition" in df.columns:
        available_conditions = sorted(df["sky_condition"].dropna().unique().tolist())
        selected_conditions = st.sidebar.multiselect(
            "Sky condition",
            options=available_conditions,
            default=available_conditions,
            help="Select one or more sky conditions to include",
        )
        if selected_conditions:
            df = df[df["sky_condition"].isin(selected_conditions)]

    # Cloud type
    if "cloud_types" in df.columns:
        all_types = set()
        for val in df["cloud_types"].dropna():
            for t in str(val).split(","):
                stripped = t.strip()
                if stripped:
                    all_types.add(stripped)
        if all_types:
            selected_types = st.sidebar.multiselect(
                "Cloud type",
                options=sorted(all_types),
                default=[],
                help="Filter by cloud type (leave empty for all)",
            )
            if selected_types:
                pattern = "|".join(selected_types)
                df = df[df["cloud_types"].str.contains(pattern, na=False)]

    # ── Header ───────────────────────────────────────────────────────────
    st.markdown(
        '<p class="main-header">☁️ GLOBE Cloud Insights</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sub-header">'
        "Interactive explorer for NASA GLOBE Observer Clouds 2022 Challenge data. "
        "Use the sidebar filters to drill into specific time periods, sky conditions, "
        "and cloud types."
        "</p>",
        unsafe_allow_html=True,
    )

    # ── KPI metrics ──────────────────────────────────────────────────────
    stats = summary_statistics(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Observations", f"{stats['total_observations']:,}")
    col2.metric("Countries", stats["unique_countries"])
    col3.metric(
        "Avg Cloud Cover",
        f"{stats['cloud_cover_mean']:.0f}%" if stats["cloud_cover_mean"] else "N/A",
    )
    if stats["date_range"]:
        col4.metric(
            "Date Range",
            f"{stats['date_range'][0][:10]} – {stats['date_range'][1][:10]}",
        )
    else:
        col4.metric("Date Range", "N/A")

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────
    tab_map, tab_temporal, tab_dist, tab_table = st.tabs(
        ["🗺️ Map", "📈 Temporal", "📊 Distributions", "📋 Data Table"]
    )

    with tab_map:
        st.markdown("### Global Observation Map")
        st.markdown(
            "Each point represents a citizen-science cloud observation. "
            "Clusters break apart as you zoom in."
        )
        sample_n = min(3000, len(df))
        map_df = df.sample(n=sample_n, random_state=42) if len(df) > sample_n else df

        m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodbpositron")
        from folium.plugins import MarkerCluster

        cluster = MarkerCluster()
        for _, row in map_df.iterrows():
            lat, lon = row.get("latitude"), row.get("longitude")
            if pd.notna(lat) and pd.notna(lon):
                folium.CircleMarker(
                    location=[float(lat), float(lon)],
                    radius=3,
                    color="#1f77b4",
                    fill=True,
                    fill_opacity=0.6,
                    popup=(
                        f"Sky: {row.get('sky_condition', 'N/A')}<br>"
                        f"Cover: {row.get('cloud_cover_pct', 'N/A')}%"
                    ),
                ).add_to(cluster)
        cluster.add_to(m)
        st_folium(m, width=None, height=480)

    with tab_temporal:
        st.markdown("### Observation Timeline")
        counts = daily_observation_counts(df)
        if not counts.empty:
            fig = plot_daily_counts(counts)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No temporal data available for the current filter selection.")

    with tab_dist:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### Sky Condition Breakdown")
            dist = sky_condition_distribution(df)
            if not dist.empty:
                fig = plot_sky_conditions(dist)
                st.plotly_chart(fig, use_container_width=True)
        with col_b:
            st.markdown("### Cloud Cover Histogram")
            fig2 = plot_cloud_cover_histogram(df)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Top Contributing Countries")
        tc = top_countries(df)
        if not tc.empty:
            fig3 = plot_top_countries(tc)
            st.plotly_chart(fig3, use_container_width=True)

    with tab_table:
        st.markdown("### Filtered Observations")
        st.markdown(f"Showing **{len(df):,}** records matching your filters.")
        st.dataframe(df.head(500), use_container_width=True, height=400)

        st.markdown("### Download Filtered Data")
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="globe_clouds_filtered.csv",
            mime="text/csv",
            help="Download the currently filtered dataset as a CSV file.",
        )

    # ── Footer ───────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        f"**Data citation:** {DATA_CITATION.format(access_date='2024')}  \n"
        "**Privacy note:** Observation coordinates are publicly available from "
        "the GLOBE Program. Please use location data responsibly and avoid "
        "sensitive inference about individual observers.  \n"
        "Built with [Streamlit](https://streamlit.io) | "
        "[Source on GitHub](https://github.com/ruddro-roy/globe-cloud-insights)"
    )


if __name__ == "__main__":
    main()
