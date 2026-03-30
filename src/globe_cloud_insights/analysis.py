"""Exploratory analysis helpers.

Functions for descriptive statistics, temporal aggregation, spatial
summaries, and visualization of GLOBE Clouds data.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Descriptive statistics ───────────────────────────────────────────────────


def summary_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """Return a dict of high-level descriptive statistics."""
    stats: dict[str, Any] = {
        "total_observations": len(df),
        "date_range": None,
        "unique_countries": 0,
        "sky_condition_counts": {},
        "cloud_cover_mean": None,
        "cloud_cover_median": None,
    }
    if "measured_at" in df.columns and not df["measured_at"].isna().all():
        stats["date_range"] = (
            str(df["measured_at"].min()),
            str(df["measured_at"].max()),
        )
    if "country_name" in df.columns:
        stats["unique_countries"] = df["country_name"].nunique()
    if "sky_condition" in df.columns:
        stats["sky_condition_counts"] = df["sky_condition"].value_counts().to_dict()
    if "cloud_cover_pct" in df.columns:
        stats["cloud_cover_mean"] = float(df["cloud_cover_pct"].mean())
        stats["cloud_cover_median"] = float(df["cloud_cover_pct"].median())
    return stats


# ── Temporal ─────────────────────────────────────────────────────────────────


def daily_observation_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame of daily observation counts."""
    if "measured_at" not in df.columns:
        return pd.DataFrame(columns=["date", "count"])
    tmp = df.copy()
    tmp["date"] = pd.to_datetime(tmp["measured_at"]).dt.date
    counts = tmp.groupby("date").size().reset_index(name="count")
    counts["date"] = pd.to_datetime(counts["date"])
    return counts


def plot_daily_counts(counts_df: pd.DataFrame) -> go.Figure:
    """Plotly bar chart of daily observation counts."""
    fig = px.bar(
        counts_df,
        x="date",
        y="count",
        title="Daily GLOBE Cloud Observations (2022 Challenge)",
        labels={"date": "Date", "count": "Observations"},
        color_discrete_sequence=["#1f77b4"],
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Observations",
        template="plotly_white",
        annotations=[
            dict(
                text="Data: GLOBE Program, globe.gov",
                xref="paper",
                yref="paper",
                x=1,
                y=-0.15,
                showarrow=False,
                font=dict(size=10, color="gray"),
            )
        ],
    )
    return fig


# ── Sky condition distribution ───────────────────────────────────────────────


def sky_condition_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Count observations by sky condition."""
    if "sky_condition" not in df.columns:
        return pd.DataFrame(columns=["sky_condition", "count", "pct"])
    vc = df["sky_condition"].value_counts().reset_index()
    vc.columns = ["sky_condition", "count"]
    vc["pct"] = (vc["count"] / vc["count"].sum() * 100).round(1)
    return vc


def plot_sky_conditions(dist_df: pd.DataFrame) -> go.Figure:
    """Plotly pie chart of sky-condition distribution."""
    fig = px.pie(
        dist_df,
        names="sky_condition",
        values="count",
        title="Sky Condition Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_layout(
        annotations=[
            dict(
                text="Data: GLOBE Program, globe.gov",
                xref="paper",
                yref="paper",
                x=1,
                y=-0.1,
                showarrow=False,
                font=dict(size=10, color="gray"),
            )
        ]
    )
    return fig


# ── Country-level ────────────────────────────────────────────────────────────


def top_countries(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Return the top *n* countries by observation count."""
    if "country_name" not in df.columns:
        return pd.DataFrame(columns=["country_name", "count"])
    vc = df["country_name"].value_counts().head(n).reset_index()
    vc.columns = ["country_name", "count"]
    return vc


def plot_top_countries(countries_df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of top-contributing countries."""
    fig = px.bar(
        countries_df.sort_values("count"),
        x="count",
        y="country_name",
        orientation="h",
        title="Top Contributing Countries",
        labels={"count": "Observations", "country_name": "Country"},
        color_discrete_sequence=["#2ca02c"],
    )
    fig.update_layout(
        template="plotly_white",
        yaxis_title="",
        annotations=[
            dict(
                text="Data: GLOBE Program, globe.gov",
                xref="paper",
                yref="paper",
                x=1,
                y=-0.15,
                showarrow=False,
                font=dict(size=10, color="gray"),
            )
        ],
    )
    return fig


# ── Spatial helpers ──────────────────────────────────────────────────────────


def create_observation_map(
    df: pd.DataFrame,
    sample_n: int = 5000,
) -> Any:
    """Create a Folium map with observation markers (sampled for performance)."""
    import folium
    from folium.plugins import MarkerCluster

    center_lat = df["latitude"].mean() if "latitude" in df.columns else 20.0
    center_lon = df["longitude"].mean() if "longitude" in df.columns else 0.0

    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=2, tiles="cartodbpositron"
    )

    plot_df = (
        df.sample(n=min(sample_n, len(df)), random_state=42)
        if len(df) > sample_n
        else df
    )

    cluster = MarkerCluster()
    for _, row in plot_df.iterrows():
        lat = row.get("latitude")
        lon = row.get("longitude")
        if pd.notna(lat) and pd.notna(lon):
            popup_text = (
                f"Sky: {row.get('sky_condition', 'N/A')}<br>"
                f"Cloud cover: {row.get('cloud_cover_pct', 'N/A')}%<br>"
                f"Date: {row.get('measured_at', 'N/A')}"
            )
            folium.CircleMarker(
                location=[float(lat), float(lon)],
                radius=3,
                color="#1f77b4",
                fill=True,
                fill_opacity=0.6,
                popup=popup_text,
            ).add_to(cluster)
    cluster.add_to(m)
    return m


def plot_cloud_cover_histogram(df: pd.DataFrame) -> go.Figure:
    """Histogram of cloud-cover percentage."""
    fig = px.histogram(
        df.dropna(subset=["cloud_cover_pct"]),
        x="cloud_cover_pct",
        nbins=20,
        title="Cloud Cover Distribution",
        labels={"cloud_cover_pct": "Cloud Cover (%)"},
        color_discrete_sequence=["#ff7f0e"],
    )
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Cloud Cover (%)",
        yaxis_title="Frequency",
        annotations=[
            dict(
                text="Data: GLOBE Program, globe.gov",
                xref="paper",
                yref="paper",
                x=1,
                y=-0.15,
                showarrow=False,
                font=dict(size=10, color="gray"),
            )
        ],
    )
    return fig
