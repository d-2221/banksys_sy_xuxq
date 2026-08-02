"""Tests for the data loader module."""

from pathlib import Path

import pandas as pd
import pytest

from app.data.loader import (
    CAT_COLS,
    FEATURE_COLS,
    ID_COL,
    NUM_COLS,
    TARGET_COL,
    get_feature_target,
    load_csv,
    load_test_data,
    load_train_data,
    preprocess,
)


@pytest.fixture
def sample_csv_path(tmp_path: Path) -> Path:
    """Create a minimal sample CSV for testing."""
    filepath = tmp_path / "train.csv"
    data = {
        ID_COL: [1, 2, 3],
        "age": [30, 40, 50],
        "job": ["admin.", "blue-collar", "services"],
        "marital": ["married", "single", "divorced"],
        "education": ["high.school", "basic.9y", "professional.course"],
        "default": ["no", "unknown", "no"],
        "housing": ["yes", "no", "yes"],
        "loan": ["no", "no", "yes"],
        "contact": ["cellular", "telephone", "cellular"],
        "month": ["may", "jun", "jul"],
        "day_of_week": ["mon", "tue", "wed"],
        "duration": [200, 300, 400],
        "campaign": [1, 2, 3],
        "pdays": [999, 100, 200],
        "previous": [0, 1, 2],
        "poutcome": ["nonexistent", "failure", "success"],
        "emp_var_rate": [1.1, -1.8, 0.4],
        "cons_price_index": [93.9, 96.3, 95.0],
        "cons_conf_index": [-36.4, -40.5, -38.0],
        "lending_rate3m": [2.5, 4.0, 3.0],
        "nr_employed": [5100.0, 4975.0, 5050.0],
        TARGET_COL: ["no", "yes", "no"],
    }
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)
    return filepath


class TestLoadCSV:
    def test_load_existing_file(self, sample_csv_path: Path):
        df = load_csv("train.csv", str(sample_csv_path.parent))
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert TARGET_COL in df.columns
        assert ID_COL in df.columns
        assert df[ID_COL].tolist() == [1, 2, 3]

    def test_load_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_csv("nonexistent.csv", str(Path(__file__).parent))


class TestPreprocess:
    def test_drop_id_column(self):
        df = pd.DataFrame({ID_COL: [1, 2], "age": [30, 40], TARGET_COL: ["no", "yes"]})
        result = preprocess(df)
        assert ID_COL not in result.columns

    def test_encode_target(self):
        df = pd.DataFrame({"age": [30, 40], TARGET_COL: ["no", "yes"]})
        result = preprocess(df)
        assert result[TARGET_COL].dtype == int
        assert result[TARGET_COL].tolist() == [0, 1]

    def test_strip_whitespace(self):
        df = pd.DataFrame({"job": [" admin. ", "blue-collar "], "age": [30, 40]})
        result = preprocess(df)
        assert result["job"].iloc[0] == "admin."
        assert result["job"].iloc[1] == "blue-collar"

    def test_no_target_column(self):
        df = pd.DataFrame({"age": [30, 40]})
        result = preprocess(df)
        assert TARGET_COL not in result.columns

    def test_returns_copy(self):
        df = pd.DataFrame({ID_COL: [1], "age": [30], TARGET_COL: ["no"]})
        result = preprocess(df)
        # Original should still have id column
        assert ID_COL in df.columns
        assert ID_COL not in result.columns


class TestLoadTrainData:
    def test_load_and_preprocess(self, sample_csv_path: Path):
        df = load_train_data(str(sample_csv_path.parent))
        assert isinstance(df, pd.DataFrame)
        assert ID_COL not in df.columns
        assert df[TARGET_COL].dtype == int
        assert df[TARGET_COL].tolist() == [0, 1, 0]


class TestLoadTestData:
    def test_load_and_preprocess(self, tmp_path: Path):
        # Create minimal test.csv
        filepath = tmp_path / "test.csv"
        pd.DataFrame({"age": [35], TARGET_COL: ["yes"]}).to_csv(filepath, index=False)
        df = load_test_data(str(tmp_path))
        assert isinstance(df, pd.DataFrame)
        assert df[TARGET_COL].dtype == int


class TestGetFeatureTarget:
    def test_split_with_target(self):
        df = pd.DataFrame(
            {"age": [30, 40], "job": ["admin.", "blue-collar"], TARGET_COL: [0, 1]}
        )
        X, y = get_feature_target(df)
        assert list(X.columns) == ["age", "job"]
        assert y.tolist() == [0, 1]

    def test_split_without_target(self):
        df = pd.DataFrame({"age": [30, 40], "job": ["admin.", "blue-collar"]})
        X, y = get_feature_target(df)
        assert list(X.columns) == ["age", "job"]
        assert y is None

    def test_column_constants(self):
        """Verify that column constants match expectations."""
        assert TARGET_COL == "subscribe"
        assert ID_COL == "id"
        assert len(CAT_COLS) > 0
        assert len(NUM_COLS) > 0
        assert len(FEATURE_COLS) == len(CAT_COLS) + len(NUM_COLS)
