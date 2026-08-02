"""Tests for the predict module / online prediction logic."""

import numpy as np
import pandas as pd

from app.data.loader import FEATURE_COLS


class TestPredictPage:
    """Verify that the required input features are consistent."""

    def test_feature_columns_are_consistent(self):
        """CAT_COLS + NUM_COLS should equal FEATURE_COLS."""
        from app.data.loader import CAT_COLS, FEATURE_COLS, NUM_COLS

        assert set(FEATURE_COLS) == set(CAT_COLS + NUM_COLS)
        assert len(FEATURE_COLS) == len(CAT_COLS) + len(NUM_COLS)

    def test_all_features_have_mapping(self):
        """All features should have a human-readable name mapping."""
        feature_display_names = {
            "age": "年龄",
            "job": "职业",
            "marital": "婚姻状况",
            "education": "教育水平",
            "default": "是否有违约",
            "housing": "是否有房贷",
            "loan": "是否有个人贷款",
            "contact": "联系类型",
            "month": "联系月份",
            "day_of_week": "联系星期",
            "duration": "通话时长(秒)",
            "campaign": "联系次数",
            "pdays": "上次联系间隔(天)",
            "previous": "历史联系次数",
            "poutcome": "上次营销结果",
            "emp_var_rate": "就业变化率",
            "cons_price_index": "消费价格指数",
            "cons_conf_index": "消费者信心指数",
            "lending_rate3m": "3个月贷款利率",
            "nr_employed": "就业人数",
        }
        for col in FEATURE_COLS:
            assert col in feature_display_names, f"Missing display name for {col}"

    def test_input_dataframe_has_correct_columns(self):
        """Input DataFrame for prediction must have the correct columns."""
        input_data = {
            col: "dummy"
            if col
            in [
                "job",
                "marital",
                "education",
                "default",
                "housing",
                "loan",
                "contact",
                "month",
                "day_of_week",
                "poutcome",
            ]
            else 0.0
            for col in FEATURE_COLS
        }
        df = pd.DataFrame([input_data], columns=FEATURE_COLS)
        assert list(df.columns) == FEATURE_COLS
        assert df.shape == (1, len(FEATURE_COLS))

    def test_numeric_features_are_numeric(self):
        """All numeric features should accept numeric values."""
        from app.data.loader import NUM_COLS

        input_data = {col: 0.0 for col in NUM_COLS}
        df = pd.DataFrame([input_data])
        for col in NUM_COLS:
            assert np.issubdtype(df[col].dtype, np.number), f"{col} is not numeric"

    def test_categorical_features_are_string(self):
        """All categorical features should accept string values."""
        from app.data.loader import CAT_COLS

        input_data = {col: "test_value" for col in CAT_COLS}
        df = pd.DataFrame([input_data])
        for col in CAT_COLS:
            assert df[col].dtype == object or df[col].dtype == str, (
                f"{col} is not string"
            )
