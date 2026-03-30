"""Tests for globe_cloud_insights.analysis."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from globe_cloud_insights.analysis import (
    create_observation_map,
    daily_observation_counts,
    plot_cloud_cover_histogram,
    plot_daily_counts,
    plot_sky_conditions,
    plot_top_countries,
    sky_condition_distribution,
    summary_statistics,
    top_countries,
)


class TestSummaryStatistics:
    def test_basic_stats(self, sample_clean_df: pd.DataFrame):
        stats = summary_statistics(sample_clean_df)
        assert stats["total_observations"] == 50
        assert stats["unique_countries"] > 0
        assert stats["cloud_cover_mean"] is not None
        assert stats["cloud_cover_median"] is not None

    def test_date_range(self, sample_clean_df: pd.DataFrame):
        stats = summary_statistics(sample_clean_df)
        assert stats["date_range"] is not None
        assert len(stats["date_range"]) == 2

    def test_sky_condition_counts(self, sample_clean_df: pd.DataFrame):
        stats = summary_statistics(sample_clean_df)
        assert isinstance(stats["sky_condition_counts"], dict)
        assert sum(stats["sky_condition_counts"].values()) == 50

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["measured_at", "country_name", "sky_condition"])
        stats = summary_statistics(df)
        assert stats["total_observations"] == 0

    def test_missing_columns(self):
        df = pd.DataFrame({"latitude": [1.0, 2.0]})
        stats = summary_statistics(df)
        assert stats["total_observations"] == 2
        assert stats["unique_countries"] == 0


class TestDailyObservationCounts:
    def test_returns_dataframe(self, sample_clean_df: pd.DataFrame):
        counts = daily_observation_counts(sample_clean_df)
        assert isinstance(counts, pd.DataFrame)
        assert "date" in counts.columns
        assert "count" in counts.columns
        assert counts["count"].sum() == len(sample_clean_df)

    def test_no_measured_at(self):
        df = pd.DataFrame({"latitude": [1.0]})
        counts = daily_observation_counts(df)
        assert counts.empty


class TestSkyConditionDistribution:
    def test_returns_counts(self, sample_clean_df: pd.DataFrame):
        dist = sky_condition_distribution(sample_clean_df)
        assert "sky_condition" in dist.columns
        assert "count" in dist.columns
        assert "pct" in dist.columns
        assert dist["count"].sum() == 50

    def test_percentages_sum_to_100(self, sample_clean_df: pd.DataFrame):
        dist = sky_condition_distribution(sample_clean_df)
        assert abs(dist["pct"].sum() - 100.0) < 1.0

    def test_no_sky_condition_column(self):
        df = pd.DataFrame({"latitude": [1.0]})
        dist = sky_condition_distribution(df)
        assert dist.empty


class TestTopCountries:
    def test_returns_top_n(self, sample_clean_df: pd.DataFrame):
        tc = top_countries(sample_clean_df, n=3)
        assert len(tc) <= 3
        assert "country_name" in tc.columns
        assert "count" in tc.columns

    def test_default_n_15(self, sample_clean_df: pd.DataFrame):
        tc = top_countries(sample_clean_df)
        assert len(tc) <= 15

    def test_no_country_column(self):
        df = pd.DataFrame({"latitude": [1.0]})
        tc = top_countries(df)
        assert tc.empty


class TestPlotFunctions:
    def test_plot_daily_counts(self, sample_clean_df: pd.DataFrame):
        counts = daily_observation_counts(sample_clean_df)
        fig = plot_daily_counts(counts)
        assert isinstance(fig, go.Figure)

    def test_plot_sky_conditions(self, sample_clean_df: pd.DataFrame):
        dist = sky_condition_distribution(sample_clean_df)
        fig = plot_sky_conditions(dist)
        assert isinstance(fig, go.Figure)

    def test_plot_top_countries(self, sample_clean_df: pd.DataFrame):
        tc = top_countries(sample_clean_df)
        fig = plot_top_countries(tc)
        assert isinstance(fig, go.Figure)

    def test_plot_cloud_cover_histogram(self, sample_clean_df: pd.DataFrame):
        fig = plot_cloud_cover_histogram(sample_clean_df)
        assert isinstance(fig, go.Figure)


class TestCreateObservationMap:
    def test_returns_folium_map(self, sample_clean_df: pd.DataFrame):
        m = create_observation_map(sample_clean_df, sample_n=10)
        import folium

        assert isinstance(m, folium.Map)

    def test_sampling(self, sample_clean_df: pd.DataFrame):
        m = create_observation_map(sample_clean_df, sample_n=5)
        import folium

        assert isinstance(m, folium.Map)
