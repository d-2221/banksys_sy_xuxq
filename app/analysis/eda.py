"""Exploratory Data Analysis (EDA) module for bank marketing dataset."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def dataset_overview(df: pd.DataFrame) -> dict:
    """Return summary statistics about the dataset.

    Args:
        df: Preprocessed DataFrame (target encoded as 0/1).

    Returns:
        Dictionary with keys:
        - total_rows, total_cols, missing_cells, missing_pct
        - positive_count, negative_count, positive_rate
        - numeric_cols, categorical_cols
    """
    total_rows, total_cols = df.shape
    missing_cells = int(df.isna().sum().sum())
    missing_pct = round(missing_cells / (total_rows * total_cols) * 100, 2)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Remove target from numeric list for overview
    if "subscribe" in numeric_cols:
        numeric_cols.remove("subscribe")

    positive_count = int(df["subscribe"].sum()) if "subscribe" in df.columns else 0
    negative_count = total_rows - positive_count if "subscribe" in df.columns else 0
    positive_rate = (
        round(positive_count / total_rows * 100, 2) if total_rows > 0 else 0.0
    )

    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "missing_cells": missing_cells,
        "missing_pct": missing_pct,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "positive_rate": positive_rate,
        "numeric_cols": numeric_cols,
        "categorical_cols": categorical_cols,
    }


def plot_numeric_distribution(df: pd.DataFrame, col: str, bins: int = 40) -> go.Figure:
    """Plot histogram with KDE overlay for a numeric column, grouped by subscribe.

    Args:
        df: Preprocessed DataFrame with 'subscribe' column.
        col: Numeric column name.
        bins: Number of histogram bins.

    Returns:
        Plotly Figure.
    """
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame.")

    fig = go.Figure()

    for label, color, group_name in [
        (0, "#ef5350", "未认购 (no)"),
        (1, "#26a69a", "认购 (yes)"),
    ]:
        subset = df[df["subscribe"] == label][col].dropna()
        if len(subset) == 0:
            continue

        fig.add_trace(
            go.Histogram(
                x=subset,
                nbinsx=bins,
                name=group_name,
                marker_color=color,
                opacity=0.65,
                histnorm="probability density",
                legendgroup=group_name,
            )
        )

    fig.update_layout(
        title=f"分布: {col}",
        xaxis_title=col,
        yaxis_title="密度",
        barmode="overlay",
        template="plotly_white",
        height=450,
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
    )
    return fig


def plot_categorical_distribution(
    df: pd.DataFrame, col: str, top_n: int = 15
) -> go.Figure:
    """Plot stacked bar chart for a categorical column, grouped by subscribe.

    Args:
        df: Preprocessed DataFrame with 'subscribe' column.
        col: Categorical column name.
        top_n: Show only top N categories by count.

    Returns:
        Plotly Figure.
    """
    if col not in df.columns:
        raise ValueError(f"Column '{col}' not found in DataFrame.")

    # Get top N categories
    top_cats = df[col].value_counts().nlargest(top_n).index.tolist()
    df_plot = df[df[col].isin(top_cats)].copy()

    crosstab = (
        pd.crosstab(
            df_plot[col],
            df_plot["subscribe"],
            normalize="index",
        )
        * 100
    )
    crosstab.columns = ["未认购 (no)", "认购 (yes)"]
    crosstab = crosstab.sort_values("认购 (yes)", ascending=True)

    counts = pd.crosstab(df_plot[col], df_plot["subscribe"])
    counts = counts.loc[crosstab.index]

    fig = go.Figure()

    for label, color, name in [
        (0, "#ef5350", "未认购 (no)"),
        (1, "#26a69a", "认购 (yes)"),
    ]:
        if name in crosstab.columns:
            fig.add_trace(
                go.Bar(
                    y=crosstab.index,
                    x=crosstab[name],
                    name=name,
                    orientation="h",
                    marker_color=color,
                    text=[
                        f"{v:.1f}%<br>(n={int(counts.loc[i, label] if label in counts.columns else 0)})"
                        for i, v in zip(crosstab.index, crosstab[name])
                    ],
                    textposition="inside",
                    insidetextanchor="middle",
                    textfont={"size": 10, "color": "white"},
                )
            )

    fig.update_layout(
        title=f"认购率 vs {col}",
        xaxis_title="百分比 (%)",
        yaxis_title=col,
        barmode="stack",
        template="plotly_white",
        height=max(300, len(crosstab) * 35),
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
    )
    return fig


def plot_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Plot correlation heatmap for numeric columns.

    Args:
        df: Preprocessed DataFrame.

    Returns:
        Plotly Figure.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()

    # Create mask for upper triangle (optional, plotly can handle it)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    corr_masked = corr.copy()
    corr_masked.values[mask] = None

    fig = px.imshow(
        corr_masked,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        title="数值特征相关性热力图",
        template="plotly_white",
        height=700,
        width=900,
    )
    fig.update_layout(margin={"l": 40, "r": 40, "t": 50, "b": 40})
    return fig


def plot_target_pie(df: pd.DataFrame) -> go.Figure:
    """Plot pie chart of target distribution.

    Args:
        df: Preprocessed DataFrame with 'subscribe' column.

    Returns:
        Plotly Figure.
    """
    counts = df["subscribe"].value_counts()
    labels = ["未认购 (no)", "认购 (yes)"]
    values = [counts.get(0, 0), counts.get(1, 0)]
    colors = ["#ef5350", "#26a69a"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors,
                textinfo="label+percent",
                hole=0.4,
            )
        ]
    )
    fig.update_layout(
        title="目标变量分布 (subscribe)",
        template="plotly_white",
        height=400,
    )
    return fig


def get_numeric_summary(df: pd.DataFrame, col: str) -> dict:
    """Compute summary statistics for a numeric column.

    Args:
        df: Preprocessed DataFrame.
        col: Numeric column name.

    Returns:
        Dictionary with mean, median, std, min, max, q1, q3.
    """
    return {
        "mean": round(df[col].mean(), 2),
        "median": round(df[col].median(), 2),
        "std": round(df[col].std(), 2),
        "min": round(df[col].min(), 2),
        "max": round(df[col].max(), 2),
        "q1": round(df[col].quantile(0.25), 2),
        "q3": round(df[col].quantile(0.75), 2),
    }
