"""Data loading and preprocessing module for bank marketing dataset."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Optional

# Column definitions
TARGET_COL = "subscribe"
ID_COL = "id"

# Categorical columns (excluding target)
CAT_COLS = [
    "job", "marital", "education", "default", "housing", "loan",
    "contact", "month", "day_of_week", "poutcome",
]

# Numerical columns (excluding id and target)
NUM_COLS = [
    "age", "duration", "campaign", "pdays", "previous",
    "emp_var_rate", "cons_price_index", "cons_conf_index",
    "lending_rate3m", "nr_employed",
]

# All feature columns (excluding id and target)
FEATURE_COLS = CAT_COLS + NUM_COLS


def _resolve_data_path(path: Optional[str] = None) -> Path:
    """Resolve the data directory path.

    Args:
        path: Optional explicit path. If None, resolves relative to this file.

    Returns:
        Absolute path to the data directory.
    """
    if path:
        return Path(path)

    # Navigate from app/data/ -> project root -> data/
    return Path(__file__).resolve().parent.parent.parent / "data"


def load_csv(filename: str, data_dir: Optional[str] = None) -> pd.DataFrame:
    """Load a CSV file from the data directory.

    Args:
        filename: CSV filename (e.g. 'train.csv').
        data_dir: Optional explicit data directory path.

    Returns:
        DataFrame with the CSV contents.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    data_path = _resolve_data_path(data_dir)
    filepath = data_path / filename

    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    df = pd.read_csv(filepath)
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and preprocess the raw DataFrame.

    Steps:
    - Drop id column if present.
    - Strip whitespace from string columns.
    - Encode target variable (subscribe) to 0/1.
    - Handle unknown/missing values in categorical columns.

    Args:
        df: Raw DataFrame loaded from CSV.

    Returns:
        Cleaned DataFrame with encoded target.
    """
    df = df.copy()

    # Drop id column
    if ID_COL in df.columns:
        df = df.drop(columns=[ID_COL])

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Encode target: 'yes' -> 1, 'no' -> 0
    if TARGET_COL in df.columns:
        df[TARGET_COL] = df[TARGET_COL].map({"yes": 1, "no": 0}).astype(int)

    return df


def load_train_data(data_dir: Optional[str] = None) -> pd.DataFrame:
    """Load and preprocess training data.

    Args:
        data_dir: Optional explicit data directory path.

    Returns:
        Cleaned training DataFrame.
    """
    df = load_csv("train.csv", data_dir)
    return preprocess(df)


def load_test_data(data_dir: Optional[str] = None) -> pd.DataFrame:
    """Load and preprocess test data.

    Args:
        data_dir: Optional explicit data directory path.

    Returns:
        Cleaned test DataFrame.
    """
    df = load_csv("test.csv", data_dir)
    return preprocess(df)


def get_feature_target(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
    """Split DataFrame into features and target.

    Args:
        df: Preprocessed DataFrame.

    Returns:
        Tuple of (X, y) where X is feature DataFrame and y is target Series.
        y is None if target column is not present.
    """
    if TARGET_COL in df.columns:
        X = df.drop(columns=[TARGET_COL])
        y = df[TARGET_COL]
    else:
        X = df
        y = None

    return X, y