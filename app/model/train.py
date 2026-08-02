"""Model training module for bank marketing prediction."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.data.loader import (
    CAT_COLS,
    FEATURE_COLS,
    NUM_COLS,
    TARGET_COL,
    load_test_data,
    load_train_data,
)

# Model output path
MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models"
MODEL_PATH = MODEL_DIR / "model.pkl"
RANDOM_STATE = 42


def _build_preprocessor() -> ColumnTransformer:
    """Build the preprocessing pipeline for categorical and numeric features.

    Returns:
        ColumnTransformer with separate pipelines for cat and num columns.
    """
    cat_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    num_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    preprocessor = ColumnTransformer(
        [
            ("cat", cat_pipeline, CAT_COLS),
            ("num", num_pipeline, NUM_COLS),
        ]
    )
    return preprocessor


def build_model() -> Pipeline:
    """Build a full pipeline with preprocessing + RandomForest classifier.

    Returns:
        Scikit-learn Pipeline object.
    """
    preprocessor = _build_preprocessor()

    classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )
    return pipeline


def train_model(
    data_dir: str | None = None,
    test_size: float = 0.2,
    save: bool = True,
) -> dict:
    """Train the model and return evaluation metrics.

    Args:
        data_dir: Optional explicit data directory path.
        test_size: Fraction of data to use for test set.
        save: Whether to save the trained model to disk.

    Returns:
        Dictionary with keys: accuracy, auc, classification_report,
        confusion_matrix, roc_curve_data.
    """
    # Load data
    df = load_train_data(data_dir)

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Build and train
    model = build_model()
    model.fit(X_train, y_train)

    # Predict
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()

    # ROC curve data (for plotting)
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    roc_data = {
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "thresholds": thresholds.tolist(),
    }

    result = {
        "accuracy": round(accuracy, 4),
        "auc": round(auc, 4),
        "classification_report": report,
        "confusion_matrix": cm,
        "roc_curve_data": roc_data,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }

    # Save model
    if save:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        result["model_path"] = str(MODEL_PATH)

    return result


def load_model(model_path: Path | None = None):
    """Load a trained model from disk.

    Args:
        model_path: Path to the model file. Defaults to MODEL_PATH.

    Returns:
        Scikit-learn Pipeline object, or None if not found.
    """
    path = model_path or MODEL_PATH
    if not path.exists():
        return None
    return joblib.load(path)


def predict(
    features: pd.DataFrame,
    model_path: Path | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Make predictions using the trained model.

    Args:
        features: DataFrame with the same feature columns as training data.
        model_path: Optional path to the model file.

    Returns:
        Tuple of (predictions, probabilities) where predictions are 0/1
        and probabilities are the probability of class 1 (subscribe).
    """
    model = load_model(model_path)
    if model is None:
        raise FileNotFoundError(
            "Trained model not found. Please train the model first."
        )

    y_pred = model.predict(features)
    y_proba = model.predict_proba(features)[:, 1]
    return y_pred, y_proba


def train_model_on_full_data(
    data_dir: str | None = None,
) -> dict:
    """Train the model on the full training dataset (no holdout split).

    This is used for the final model that goes into production.
    Evaluation is done on the test set.

    Returns:
        Dictionary with evaluation metrics on test set.
    """
    # Load and train on full training data
    train_df = load_train_data(data_dir)
    test_df = load_test_data(data_dir)

    X_train = train_df[FEATURE_COLS]
    y_train = train_df[TARGET_COL]
    X_test = test_df[FEATURE_COLS]
    y_test = test_df[TARGET_COL]

    model = build_model()
    model.fit(X_train, y_train)

    # Evaluate on test set
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()

    result = {
        "accuracy": round(accuracy, 4),
        "auc": round(auc, 4),
        "classification_report": report,
        "confusion_matrix": cm,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }

    # Save model
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    result["model_path"] = str(MODEL_PATH)

    return result
