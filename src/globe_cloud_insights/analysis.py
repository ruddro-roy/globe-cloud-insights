"""Exploratory analysis helpers.

Functions for descriptive statistics, temporal aggregation, spatial
summaries, and visualization of GLOBE Clouds data.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Shared colour palette ────────────────────────────────────────────────────

_BLUE = "#3b82f6"
_BLUE_LIGHT = "#93c5fd"
_GREEN = "#10b981"
_ORANGE = "#f59e0b"
_SKY_PALETTE = [
    "#60a5fa",  # light blue
    "#38bdf8",  # sky
    "#818cf8",  # indigo
    "#a78bfa",  # violet
    "#f472b6",  # pink
    "#fb923c",  # orange
    "#34d399",  # emerald
]

_LAYOUT_DEFAULTS: dict[str, Any] = dict(
    template="plotly_white",
    font=dict(family="Inter, -apple-system, sans-serif", size=13),
    title_font=dict(size=16, color="#1e293b"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=50, b=40),
)


def _apply_layout(fig: go.Figure, **overrides: Any) -> go.Figure:
    """Apply shared layout defaults to a Plotly figure."""
    fig.update_layout(**{**_LAYOUT_DEFAULTS, **overrides})
    return fig


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
        labels={"date": "Date", "count": "Observations"},
        color_discrete_sequence=[_BLUE],
    )
    fig.update_traces(
        marker_line_width=0,
        marker_cornerradius=3,
        opacity=0.9,
    )
    _apply_layout(
        fig,
        title="Daily Cloud Observations",
        xaxis_title="Date",
        yaxis_title="Number of Observations",
        xaxis=dict(gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9"),
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
    """Plotly donut chart of sky-condition distribution."""
    fig = go.Figure(
        go.Pie(
            labels=dist_df["sky_condition"],
            values=dist_df["count"],
            hole=0.45,
            marker=dict(colors=_SKY_PALETTE, line=dict(color="#fff", width=2)),
            textinfo="label+percent",
            textfont=dict(size=12),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "%{value:,} observations (%{percent})<extra></extra>"
            ),
        )
    )
    _apply_layout(
        fig,
        title="Sky Conditions",
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
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
    sorted_df = countries_df.sort_values("count")
    fig = go.Figure(
        go.Bar(
            x=sorted_df["count"],
            y=sorted_df["country_name"],
            orientation="h",
            marker=dict(
                color=sorted_df["count"],
                colorscale=[[0, _BLUE_LIGHT], [1, _BLUE]],
                line=dict(width=0),
                cornerradius=3,
            ),
            hovertemplate=("<b>%{y}</b><br>%{x:,} observations<extra></extra>"),
        )
    )
    _apply_layout(
        fig,
        title="Top Contributing Countries",
        xaxis_title="Observations",
        yaxis_title="",
        yaxis=dict(gridcolor="#f1f5f9"),
        xaxis=dict(gridcolor="#f1f5f9"),
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
                radius=4,
                color="#3b82f6",
                fill=True,
                fill_color="#60a5fa",
                fill_opacity=0.7,
                weight=1,
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
        labels={"cloud_cover_pct": "Cloud Cover (%)"},
        color_discrete_sequence=[_ORANGE],
    )
    fig.update_traces(
        marker_line_width=0,
        marker_cornerradius=3,
        opacity=0.9,
    )
    _apply_layout(
        fig,
        title="Cloud Cover Distribution",
        xaxis_title="Cloud Cover (%)",
        yaxis_title="Frequency",
        xaxis=dict(gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9"),
    )
    return fig


# ── Inferential statistics ───────────────────────────────────────────────────


def analyze_cloud_cover_by_latitude(df: pd.DataFrame) -> dict[str, Any]:
    """Correlate cloud cover with absolute latitude."""
    if "latitude" not in df.columns or "cloud_cover_pct" not in df.columns:
        return {"error": "Missing required columns"}

    tmp = df.dropna(subset=["latitude", "cloud_cover_pct"]).copy()
    if len(tmp) < 2:
        return {"error": "Insufficient data"}

    tmp["abs_latitude"] = tmp["latitude"].abs()
    correlation = tmp["abs_latitude"].corr(tmp["cloud_cover_pct"])

    return {
        "pearson_correlation": float(correlation),
        "n_samples": len(tmp),
    }


def plot_cloud_cover_vs_latitude(df: pd.DataFrame) -> go.Figure:
    """Scatter plot of cloud cover vs absolute latitude, sampled for performance."""
    if "latitude" not in df.columns or "cloud_cover_pct" not in df.columns:
        return go.Figure()

    tmp = df.dropna(subset=["latitude", "cloud_cover_pct"]).copy()
    tmp["abs_latitude"] = tmp["latitude"].abs()

    if len(tmp) > 5000:
        tmp = tmp.sample(5000, random_state=42)

    fig = px.scatter(
        tmp,
        x="abs_latitude",
        y="cloud_cover_pct",
        opacity=0.3,
        color_discrete_sequence=[_BLUE],
    )

    _apply_layout(
        fig,
        title="Cloud Cover vs. Distance from Equator",
        xaxis_title="Absolute Latitude (degrees)",
        yaxis_title="Cloud Cover (%)",
        xaxis=dict(gridcolor="#f1f5f9"),
        yaxis=dict(gridcolor="#f1f5f9"),
    )
    return fig
