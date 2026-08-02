"""Tests for the model training module."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.model.train import (
    FEATURE_COLS,
    build_model,
    load_model,
    predict,
    train_model,
    train_model_on_full_data,
)


@pytest.fixture
def sample_train_data(tmp_path: Path) -> Path:
    """Create a minimal training CSV for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    n = 30
    np.random.seed(42)
    data = {
        "id": range(1, n + 1),
        "age": np.random.randint(20, 70, n),
        "job": np.random.choice(["admin.", "blue-collar", "services"], n),
        "marital": np.random.choice(["married", "single", "divorced"], n),
        "education": np.random.choice(
            ["high.school", "basic.9y", "university.degree"], n
        ),
        "default": np.random.choice(["no", "unknown"], n),
        "housing": np.random.choice(["yes", "no"], n),
        "loan": np.random.choice(["no", "yes"], n, p=[0.8, 0.2]),
        "contact": np.random.choice(["cellular", "telephone"], n),
        "month": np.random.choice(["may", "jun", "jul"], n),
        "day_of_week": np.random.choice(["mon", "tue", "wed", "thu", "fri"], n),
        "duration": np.random.randint(50, 5000, n),
        "campaign": np.random.randint(1, 50, n),
        "pdays": np.random.choice([-1, 100, 200, 300], n),
        "previous": np.random.randint(0, 10, n),
        "poutcome": np.random.choice(["nonexistent", "failure", "success"], n),
        "emp_var_rate": np.random.uniform(-3, 3, n),
        "cons_price_index": np.random.uniform(92, 98, n),
        "cons_conf_index": np.random.uniform(-50, -30, n),
        "lending_rate3m": np.random.uniform(0, 6, n),
        "nr_employed": np.random.uniform(4900, 5300, n),
        "subscribe": np.random.choice(["no", "yes"], n, p=[0.85, 0.15]),
    }
    df = pd.DataFrame(data)
    df.to_csv(data_dir / "train.csv", index=False)
    # Also create test.csv
    df.to_csv(data_dir / "test.csv", index=False)
    return data_dir


class TestBuildModel:
    def test_returns_pipeline(self):
        model = build_model()
        assert model is not None
        # Pipeline should have preprocessor and classifier
        assert "preprocessor" in model.named_steps
        assert "classifier" in model.named_steps

    def test_pipeline_fits_and_predicts(self, sample_train_data: Path):
        # Load data manually
        df = pd.read_csv(sample_train_data / "train.csv")
        from app.data.loader import preprocess

        df = preprocess(df)

        X = df[FEATURE_COLS]
        y = df["subscribe"]

        model = build_model()
        model.fit(X, y)
        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)[:, 1]

        assert len(y_pred) == len(y)
        assert all(p in [0, 1] for p in y_pred)
        assert all(0 <= p <= 1 for p in y_proba)


class TestTrainModel:
    def test_training_returns_metrics(self, sample_train_data: Path):
        result = train_model(data_dir=str(sample_train_data), test_size=0.3, save=False)
        assert "accuracy" in result
        assert "auc" in result
        assert "classification_report" in result
        assert "confusion_matrix" in result
        assert result["train_samples"] > 0
        assert result["test_samples"] > 0

    def test_training_saves_model(self, sample_train_data: Path, tmp_path: Path):
        # Override MODEL_PATH to a temp location
        import app.model.train as train_module

        original_path = train_module.MODEL_PATH
        temp_model_path = tmp_path / "models" / "model.pkl"
        temp_model_path.parent.mkdir(parents=True)
        train_module.MODEL_PATH = temp_model_path

        try:
            result = train_model(data_dir=str(sample_train_data), save=True)
            assert "model_path" in result
            assert temp_model_path.exists()
        finally:
            train_module.MODEL_PATH = original_path


class TestLoadModel:
    def test_load_nonexistent_returns_none(self):
        model = load_model(Path("/nonexistent/model.pkl"))
        assert model is None

    def test_load_trained_model(self, sample_train_data: Path, tmp_path: Path):
        import app.model.train as train_module

        original_path = train_module.MODEL_PATH
        temp_model_path = tmp_path / "models" / "model.pkl"
        temp_model_path.parent.mkdir(parents=True)
        train_module.MODEL_PATH = temp_model_path

        try:
            train_model(data_dir=str(sample_train_data), save=True)
            model = load_model(temp_model_path)
            assert model is not None
        finally:
            train_module.MODEL_PATH = original_path


class TestPredict:
    def test_predict_raises_without_model(self):
        with pytest.raises(FileNotFoundError):
            predict(pd.DataFrame(), Path("/nonexistent/model.pkl"))

    def test_predict_returns_correct_shape(
        self, sample_train_data: Path, tmp_path: Path
    ):
        import app.model.train as train_module

        original_path = train_module.MODEL_PATH
        temp_model_path = tmp_path / "models" / "model.pkl"
        temp_model_path.parent.mkdir(parents=True)
        train_module.MODEL_PATH = temp_model_path

        try:
            train_model(data_dir=str(sample_train_data), save=True)
            df = pd.read_csv(sample_train_data / "train.csv")
            from app.data.loader import preprocess

            df = preprocess(df)
            X = df[FEATURE_COLS].head(5)

            y_pred, y_proba = predict(X, temp_model_path)
            assert len(y_pred) == 5
            assert len(y_proba) == 5
            assert all(p in [0, 1] for p in y_pred)
            assert all(0 <= p <= 1 for p in y_proba)
        finally:
            train_module.MODEL_PATH = original_path


class TestTrainModelOnFullData:
    def test_uses_test_csv_for_eval(self, sample_train_data: Path, tmp_path: Path):
        import app.model.train as train_module

        original_path = train_module.MODEL_PATH
        temp_model_path = tmp_path / "models" / "model.pkl"
        temp_model_path.parent.mkdir(parents=True)
        train_module.MODEL_PATH = temp_model_path

        try:
            result = train_model_on_full_data(data_dir=str(sample_train_data))
            assert "accuracy" in result
            assert "auc" in result
            assert "classification_report" in result
            assert "model_path" in result
            assert temp_model_path.exists()
        finally:
            train_module.MODEL_PATH = original_path
