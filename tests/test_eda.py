"""Tests for the EDA module."""

import numpy as np
import pandas as pd
import pytest

from app.analysis.eda import (
    dataset_overview,
    get_numeric_summary,
    plot_categorical_distribution,
    plot_correlation_heatmap,
    plot_numeric_distribution,
    plot_target_pie,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Create a small sample DataFrame for testing."""
    np.random.seed(42)
    n = 50
    return pd.DataFrame(
        {
            "age": np.random.randint(20, 70, n),
            "duration": np.random.randint(50, 5000, n),
            "campaign": np.random.randint(1, 50, n),
            "job": np.random.choice(
                ["admin.", "blue-collar", "services", "technician"], n
            ),
            "marital": np.random.choice(["married", "single", "divorced"], n),
            "education": np.random.choice(
                ["high.school", "basic.9y", "university.degree"], n
            ),
            "subscribe": np.random.choice([0, 1], n, p=[0.85, 0.15]),
        }
    )


class TestDatasetOverview:
    def test_basic_stats(self, sample_df: pd.DataFrame):
        info = dataset_overview(sample_df)
        assert info["total_rows"] == 50
        assert info["total_cols"] == 7
        assert info["positive_count"] + info["negative_count"] == 50
        assert info["positive_rate"] >= 0.0
        assert "age" in info["numeric_cols"]
        assert "job" in info["categorical_cols"]
        assert "subscribe" not in info["numeric_cols"]  # excluded from overview

    def test_missing_values(self):
        df = pd.DataFrame(
            {
                "age": [30, np.nan, 40],
                "job": ["admin.", None, "blue-collar"],
                "subscribe": [0, 1, 0],
            }
        )
        info = dataset_overview(df)
        assert info["missing_cells"] == 2
        assert info["missing_pct"] > 0

    def test_all_zero_target(self):
        df = pd.DataFrame({"age": [30, 40], "subscribe": [0, 0]})
        info = dataset_overview(df)
        assert info["positive_count"] == 0
        assert info["positive_rate"] == 0.0


class TestPlotNumericDistribution:
    def test_valid_column(self, sample_df: pd.DataFrame):
        fig = plot_numeric_distribution(sample_df, "age")
        assert fig is not None
        assert len(fig.data) > 0  # has traces

    def test_missing_column_raises(self, sample_df: pd.DataFrame):
        with pytest.raises(ValueError, match="not_found"):
            plot_numeric_distribution(sample_df, "not_found")

    def test_returns_figure_with_correct_layout(self, sample_df: pd.DataFrame):
        fig = plot_numeric_distribution(sample_df, "duration", bins=20)
        assert fig.layout.title.text == "分布: duration"
        assert fig.layout.xaxis.title.text == "duration"


class TestPlotCategoricalDistribution:
    def test_valid_column(self, sample_df: pd.DataFrame):
        fig = plot_categorical_distribution(sample_df, "job")
        assert fig is not None
        assert len(fig.data) > 0

    def test_missing_column_raises(self, sample_df: pd.DataFrame):
        with pytest.raises(ValueError, match="not_there"):
            plot_categorical_distribution(sample_df, "not_there")

    def test_top_n_filter(self, sample_df: pd.DataFrame):
        fig = plot_categorical_distribution(sample_df, "education", top_n=2)
        assert fig is not None


class TestPlotCorrelationHeatmap:
    def test_returns_figure(self, sample_df: pd.DataFrame):
        fig = plot_correlation_heatmap(sample_df)
        assert fig is not None
        assert fig.layout.title.text == "数值特征相关性热力图"

    def test_works_with_only_numeric(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "subscribe": [0, 1, 0]})
        fig = plot_correlation_heatmap(df)
        assert fig is not None


class TestPlotTargetPie:
    def test_returns_figure(self, sample_df: pd.DataFrame):
        fig = plot_target_pie(sample_df)
        assert fig is not None
        assert len(fig.data) == 1

    def test_labels_and_values(self, sample_df: pd.DataFrame):
        fig = plot_target_pie(sample_df)
        pie = fig.data[0]
        assert "未认购" in pie.labels[0]
        assert "认购" in pie.labels[1]
        assert pie.values[0] > pie.values[1]  # more no than yes


class TestGetNumericSummary:
    def test_basic_stats(self, sample_df: pd.DataFrame):
        stats = get_numeric_summary(sample_df, "age")
        assert "mean" in stats
        assert "median" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats
        assert stats["min"] <= stats["mean"] <= stats["max"]

    def test_known_values(self):
        df = pd.DataFrame({"age": [10, 20, 30, 40, 50], "subscribe": [0, 0, 1, 1, 0]})
        stats = get_numeric_summary(df, "age")
        assert stats["mean"] == 30.0
        assert stats["min"] == 10.0
        assert stats["max"] == 50.0
        assert stats["median"] == 30.0
