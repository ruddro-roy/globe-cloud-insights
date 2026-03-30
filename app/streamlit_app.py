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
    @import url(
      'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
    );

    /* Global typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* Hero section */
    .hero-container {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 40%, #2c5364 100%);
        border-radius: 16px;
        padding: 2.5rem 2.5rem 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -40%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.4rem 0;
        letter-spacing: -0.02em;
        line-height: 1.15;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        font-weight: 400;
        color: rgba(255,255,255,0.78);
        margin: 0;
        line-height: 1.55;
        max-width: 680px;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 20px;
        padding: 0.25rem 0.85rem;
        font-size: 0.78rem;
        font-weight: 500;
        color: rgba(255,255,255,0.9);
        margin-bottom: 0.9rem;
        letter-spacing: 0.03em;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1e293b;
    }

    /* Section headings */
    .section-heading {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0.5rem 0 0.3rem 0;
        letter-spacing: -0.01em;
    }
    .section-help {
        font-size: 0.88rem;
        color: #64748b;
        margin: 0 0 1rem 0;
        line-height: 1.5;
    }

    /* Info callout boxes */
    .insight-box {
        background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
        border-left: 3px solid #3b82f6;
        border-radius: 0 8px 8px 0;
        padding: 0.85rem 1.1rem;
        margin: 0.8rem 0 1.2rem 0;
        font-size: 0.88rem;
        color: #1e40af;
        line-height: 1.55;
    }
    .insight-box strong {
        color: #1e3a8a;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
    }
    .sidebar-label {
        font-size: 0.82rem;
        font-weight: 500;
        color: #475569;
        margin-bottom: 0.2rem;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #f8fafc;
        border-radius: 10px;
        padding: 0.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.9rem;
        padding: 0.5rem 1.2rem;
    }
    .stTabs [aria-selected="true"] {
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    /* Download button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.15s ease;
    }
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 4px 12px rgba(37,99,235,0.3);
        transform: translateY(-1px);
    }

    /* Footer */
    .app-footer {
        background: #f8fafc;
        border-top: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-top: 1.5rem;
        font-size: 0.82rem;
        color: #64748b;
        line-height: 1.6;
    }
    .app-footer a {
        color: #2563eb;
        text-decoration: none;
        font-weight: 500;
    }

    /* General spacing */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
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
    df_original = load_data()
    df = df_original.copy()

    # Ensure datetime
    if "measured_at" in df.columns:
        df["measured_at"] = pd.to_datetime(df["measured_at"], errors="coerce")

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
                <div style="font-size:1.8rem;">☁️</div>
                <div style="font-size:1rem; font-weight:600; color:#1e293b;">
                    GLOBE Cloud Insights
                </div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:0.2rem;">
                    NASA Citizen-Science Data
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("## Explore the Data")
        st.caption(
            "Use the controls below to focus on specific time periods, "
            "weather patterns, or cloud types. The dashboard updates "
            "instantly as you change selections."
        )

        # Date range
        if "measured_at" in df.columns and not df["measured_at"].isna().all():
            min_date = df["measured_at"].min().date()
            max_date = df["measured_at"].max().date()
            st.markdown(
                '<p class="sidebar-label">Date Range</p>',
                unsafe_allow_html=True,
            )
            date_range = st.date_input(
                "Date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help=(
                    "Narrow observations to a specific window. "
                    "The challenge ran Jan 15 to Feb 15, 2022."
                ),
                label_visibility="collapsed",
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                mask = df["measured_at"].dt.date.between(date_range[0], date_range[1])
                df = df[mask]

        # Sky condition
        if "sky_condition" in df.columns:
            available_conditions = sorted(
                df["sky_condition"].dropna().unique().tolist()
            )
            st.markdown(
                '<p class="sidebar-label">Sky Condition</p>',
                unsafe_allow_html=True,
            )
            selected_conditions = st.multiselect(
                "Sky condition",
                options=available_conditions,
                default=available_conditions,
                help=(
                    "Sky conditions describe overall cloud coverage: "
                    "Clear (0%), Few (~15%), Scattered (~40%), "
                    "Broken (~70%), Overcast (~95%), Obscured (100%)."
                ),
                label_visibility="collapsed",
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
                st.markdown(
                    '<p class="sidebar-label">Cloud Type</p>',
                    unsafe_allow_html=True,
                )
                selected_types = st.multiselect(
                    "Cloud type",
                    options=sorted(all_types),
                    default=[],
                    help=(
                        "Filter by specific cloud genera (e.g. Cumulus, "
                        "Cirrus). Leave empty to see all types."
                    ),
                    label_visibility="collapsed",
                )
                if selected_types:
                    pattern = "|".join(selected_types)
                    df = df[df["cloud_types"].str.contains(pattern, na=False)]

        st.markdown("---")
        st.caption(
            "Data from NASA GLOBE Program | " "[Learn more](https://observer.globe.gov)"
        )

    # ── Hero header ───────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-badge">
                NASA GLOBE Observer &middot; 2022 Cloud Challenge
            </div>
            <h1 class="hero-title">Cloud Insights Dashboard</h1>
            <p class="hero-subtitle">
                Explore 42,700+ citizen-science cloud observations collected by
                volunteers across 89 countries during the 2022 NASA GLOBE Cloud
                Challenge. Filter, map, and download the data to uncover global
                weather patterns.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI metrics ──────────────────────────────────────────────────────
    stats = summary_statistics(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Observations", f"{stats['total_observations']:,}")
    col2.metric("Countries Represented", stats["unique_countries"])
    col3.metric(
        "Avg. Cloud Cover",
        f"{stats['cloud_cover_mean']:.0f}%" if stats["cloud_cover_mean"] else "N/A",
    )
    if stats["date_range"]:
        col4.metric(
            "Date Span",
            f"{stats['date_range'][0][:10]} to {stats['date_range'][1][:10]}",
        )
    else:
        col4.metric("Date Span", "N/A")

    st.markdown("")  # spacing

    # ── Tabs ─────────────────────────────────────────────────────────────
    tab_map, tab_temporal, tab_dist, tab_table = st.tabs(
        [
            "World Map",
            "Timeline",
            "Patterns & Distributions",
            "Browse & Download",
        ]
    )

    # ── Map tab ──────────────────────────────────────────────────────────
    with tab_map:
        st.markdown(
            '<p class="section-heading">Where Were Clouds Observed?</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="section-help">'
            "Each dot is a real observation submitted by a citizen scientist. "
            "Clusters show areas with many nearby observations "
            "— zoom in to see individual points."
            "</p>",
            unsafe_allow_html=True,
        )

        sample_n = min(3000, len(df))
        map_df = df.sample(n=sample_n, random_state=42) if len(df) > sample_n else df

        m = folium.Map(
            location=[20, 0],
            zoom_start=2,
            tiles="cartodbpositron",
        )
        from folium.plugins import MarkerCluster

        cluster = MarkerCluster()
        for _, row in map_df.iterrows():
            lat, lon = row.get("latitude"), row.get("longitude")
            if pd.notna(lat) and pd.notna(lon):
                popup_html = (
                    f"<div style='font-family:Inter,sans-serif;font-size:13px;'>"
                    f"<b>Sky:</b> {row.get('sky_condition', 'N/A')}<br>"
                    f"<b>Cover:</b> {row.get('cloud_cover_pct', 'N/A'):.0f}%<br>"
                    f"<b>Country:</b> {row.get('country_name', 'N/A')}"
                    f"</div>"
                )
                folium.CircleMarker(
                    location=[float(lat), float(lon)],
                    radius=4,
                    color="#3b82f6",
                    fill=True,
                    fill_color="#60a5fa",
                    fill_opacity=0.7,
                    weight=1,
                    popup=folium.Popup(popup_html, max_width=220),
                ).add_to(cluster)
        cluster.add_to(m)
        st_folium(m, width=None, height=520)

        st.markdown(
            '<div class="insight-box">'
            "<strong>Reading this map:</strong> "
            "Larger clusters indicate regions with more active citizen "
            "scientists. Notice how observations concentrate in North America, "
            "Europe, and parts of Asia — reflecting where the GLOBE program "
            "has the most participants."
            "</div>",
            unsafe_allow_html=True,
        )

    # ── Temporal tab ─────────────────────────────────────────────────────
    with tab_temporal:
        st.markdown(
            '<p class="section-heading">When Were Observations Collected?</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="section-help">'
            "This chart shows how many cloud observations were submitted each "
            "day during the challenge period. Peaks often align with weekdays "
            "when schools are in session."
            "</p>",
            unsafe_allow_html=True,
        )

        counts = daily_observation_counts(df)
        if not counts.empty:
            fig = plot_daily_counts(counts)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                '<div class="insight-box">'
                "<strong>What to look for:</strong> "
                "Spikes may indicate organized classroom events or social "
                "media campaigns. Dips often correspond to weekends. "
                "The overall trend shows sustained participation throughout "
                "the challenge."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("No timeline data available for the current filter selection.")

    # ── Distribution tab ─────────────────────────────────────────────────
    with tab_dist:
        st.markdown(
            '<p class="section-heading">' "What Did the Sky Look Like?" "</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="section-help">'
            "These charts reveal the most commonly observed sky conditions, "
            "cloud coverage levels, and which countries contributed the most "
            "observations."
            "</p>",
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### Sky Conditions")
            dist = sky_condition_distribution(df)
            if not dist.empty:
                fig = plot_sky_conditions(dist)
                st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "Shows the proportion of each sky condition category "
                "in the filtered dataset."
            )

        with col_b:
            st.markdown("#### Cloud Cover Spread")
            fig2 = plot_cloud_cover_histogram(df)
            st.plotly_chart(fig2, use_container_width=True)
            st.caption(
                "Distribution of estimated cloud coverage percentage "
                "across all filtered observations."
            )

        st.markdown("")
        st.markdown("#### Top Contributing Countries")
        tc = top_countries(df)
        if not tc.empty:
            fig3 = plot_top_countries(tc)
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown(
            '<div class="insight-box">'
            "<strong>Why it matters:</strong> "
            "The country chart shows geographic diversity of the challenge. "
            "A broad global spread means the observations capture a wider "
            "variety of climate zones, making the dataset more scientifically "
            "valuable."
            "</div>",
            unsafe_allow_html=True,
        )

    # ── Data table tab ───────────────────────────────────────────────────
    with tab_table:
        st.markdown(
            '<p class="section-heading">Browse the Raw Observations</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="section-help">'
            "Scroll through individual observations, or download the "
            "filtered dataset as a CSV file for your own analysis."
            "</p>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"Showing **{min(500, len(df)):,}** of "
            f"**{len(df):,}** filtered records."
        )
        st.dataframe(df.head(500), use_container_width=True, height=420)

        st.markdown("")
        col_dl1, col_dl2, _ = st.columns([1.2, 1.2, 2.6])
        with col_dl1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Filtered Data (CSV)",
                data=csv,
                file_name="globe_clouds_filtered.csv",
                mime="text/csv",
                help="Downloads all records matching your current filters.",
            )
        with col_dl2:
            st.markdown(
                f"<span style='font-size:0.82rem; color:#64748b; "
                f"line-height:2.8;'>"
                f"{len(df):,} records ready</span>",
                unsafe_allow_html=True,
            )

    # ── Footer ───────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="app-footer">
            <strong>Data citation:</strong>
            {DATA_CITATION.format(access_date='2024')}<br>
            <strong>Privacy note:</strong> Observation coordinates are
            publicly available from the GLOBE Program. Please use location
            data responsibly.<br>
            <a href="https://github.com/ruddro-roy/globe-cloud-insights"
               target="_blank">Source Code</a> &middot;
            <a href="https://observer.globe.gov" target="_blank">
               GLOBE Observer</a> &middot;
            <a href="https://www.globe.gov/globe-data/globe-api"
               target="_blank">GLOBE API</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
