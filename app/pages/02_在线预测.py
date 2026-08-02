"""Streamlit page: 在线预测 — Predict customer subscription probability."""

import pandas as pd
import streamlit as st

from app.data.loader import (
    FEATURE_COLS,
)
from app.model.train import (
    MODEL_PATH,
    load_model,
    predict,
    train_model_on_full_data,
)

st.set_page_config(page_title="在线预测", page_icon="🔮", layout="wide")

st.title("🔮 在线预测")
st.markdown("通过输入客户特征，预测该客户是否会认购定期存款。")


# ── Check if model exists, load it ──
@st.cache_resource(show_spinner="加载模型中...")
def _load_model():
    return load_model(MODEL_PATH)


model = _load_model()

# ── Model training section ──
st.sidebar.header("⚙️ 模型管理")
if st.sidebar.button("🔄 重新训练模型", type="primary", use_container_width=True):
    with st.spinner("正在训练模型，请稍候..."):
        try:
            result = train_model_on_full_data()
            st.sidebar.success(f"模型训练完成！AUC: {result['auc']:.4f}")
            # Clear cache so new model is loaded
            st.cache_resource.clear()
            st.rerun()
        except (FileNotFoundError, ValueError) as e:
            st.sidebar.error(f"训练失败: {e}")

# ── Model status ──
if model is not None:
    st.sidebar.info("✅ 模型已就绪")

    # ── Prediction form ──
    st.header("📝 输入客户特征")
    st.markdown("请填写以下客户信息，然后点击「预测」按钮。")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("👤 个人信息")
        age = st.slider("年龄", 18, 95, 35, help="客户年龄")
        job = st.selectbox(
            "职业",
            [
                "admin.",
                "blue-collar",
                "entrepreneur",
                "housemaid",
                "management",
                "retired",
                "self-employed",
                "services",
                "student",
                "technician",
                "unemployed",
                "unknown",
            ],
            index=0,
            help="客户职业类型",
        )
        marital = st.selectbox(
            "婚姻状况",
            ["married", "single", "divorced", "unknown"],
            index=0,
        )
        education = st.selectbox(
            "教育水平",
            [
                "basic.4y",
                "basic.6y",
                "basic.9y",
                "high.school",
                "illiterate",
                "professional.course",
                "university.degree",
                "unknown",
            ],
            index=6,
            help="客户最高教育水平",
        )

    with col2:
        st.subheader("💰 财务信息")
        default = st.selectbox(
            "是否有信用违约",
            ["no", "yes", "unknown"],
            index=0,
            help="客户是否有信用违约记录",
        )
        housing = st.selectbox(
            "是否有房贷",
            ["yes", "no", "unknown"],
            index=0,
            help="客户是否有住房贷款",
        )
        loan = st.selectbox(
            "是否有个人贷款",
            ["no", "yes", "unknown"],
            index=0,
            help="客户是否有个人贷款",
        )

        st.subheader("📞 联系信息")
        contact = st.selectbox(
            "联系类型",
            ["cellular", "telephone"],
            index=0,
            help="与客户的联系方式",
        )
        month = st.selectbox(
            "联系月份",
            [
                "jan",
                "feb",
                "mar",
                "apr",
                "may",
                "jun",
                "jul",
                "aug",
                "sep",
                "oct",
                "nov",
                "dec",
            ],
            index=4,
        )
        day_of_week = st.selectbox(
            "联系星期",
            ["mon", "tue", "wed", "thu", "fri"],
            index=0,
        )

    with col3:
        st.subheader("📊 营销信息")
        duration = st.slider(
            "通话时长(秒)",
            0,
            5000,
            200,
            help="上次联系的通话时长（秒）",
        )
        campaign = st.slider(
            "当前活动联系次数",
            1,
            50,
            1,
            help="本次营销活动中联系该客户的次数",
        )
        pdays = st.slider(
            "上次联系间隔(天)",
            -1,
            1000,
            -1,
            help="上次营销活动后到当前的天数(-1=未联系过)",
        )
        previous = st.slider(
            "历史联系次数",
            0,
            50,
            0,
            help="本次营销活动之前联系该客户的次数",
        )
        poutcome = st.selectbox(
            "上次营销结果",
            ["nonexistent", "failure", "success"],
            index=0,
            help="上次营销活动的结果",
        )

    # ── Economic indicators ──
    st.subheader("📈 经济指标")
    eco_col1, eco_col2, eco_col3, eco_col4, eco_col5 = st.columns(5)
    with eco_col1:
        emp_var_rate = st.number_input(
            "就业变化率",
            value=-1.8,
            step=0.1,
            format="%.2f",
        )
    with eco_col2:
        cons_price_index = st.number_input(
            "消费价格指数",
            value=93.9,
            step=0.1,
            format="%.2f",
        )
    with eco_col3:
        cons_conf_index = st.number_input(
            "消费者信心指数",
            value=-40.0,
            step=0.1,
            format="%.2f",
        )
    with eco_col4:
        lending_rate3m = st.number_input(
            "3个月贷款利率",
            value=2.5,
            step=0.1,
            format="%.2f",
        )
    with eco_col5:
        nr_employed = st.number_input(
            "就业人数",
            value=5100.0,
            step=10.0,
            format="%.2f",
        )

    # ── Predict button ──
    st.markdown("---")
    predict_col1, predict_col2 = st.columns([1, 3])
    with predict_col1:
        predict_btn = st.button("🔮 预测", type="primary", use_container_width=True)

    if predict_btn:
        # Build input DataFrame
        input_data = {
            "age": age,
            "job": job,
            "marital": marital,
            "education": education,
            "default": default,
            "housing": housing,
            "loan": loan,
            "contact": contact,
            "month": month,
            "day_of_week": day_of_week,
            "duration": duration,
            "campaign": campaign,
            "pdays": pdays,
            "previous": previous,
            "poutcome": poutcome,
            "emp_var_rate": emp_var_rate,
            "cons_price_index": cons_price_index,
            "cons_conf_index": cons_conf_index,
            "lending_rate3m": lending_rate3m,
            "nr_employed": nr_employed,
        }
        input_df = pd.DataFrame([input_data], columns=FEATURE_COLS)

        with st.spinner("正在预测..."):
            try:
                y_pred, y_proba = predict(input_df, MODEL_PATH)
                pred_label = y_pred[0]
                prob_value = y_proba[0] * 100

                # Display result
                st.markdown("---")
                st.header("📊 预测结果")

                result_col1, result_col2, result_col3 = st.columns(3)

                with result_col1:
                    if pred_label == 1:
                        st.success("### 预测: 认购 ✅")
                        st.markdown("该客户**很可能**会认购定期存款。")
                    else:
                        st.error("### 预测: 不认购 ❌")
                        st.markdown("该客户**很可能**不会认购定期存款。")

                with result_col2:
                    prob_color = (
                        "green"
                        if prob_value > 60
                        else "red"
                        if prob_value < 30
                        else "orange"
                    )
                    st.markdown(
                        f"### 认购概率: "
                        f"<span style='color:{prob_color};font-size:2em;font-weight:bold;'>"
                        f"{prob_value:.1f}%</span>",
                        unsafe_allow_html=True,
                    )

                with result_col3:
                    # Show threshold recommendation
                    st.markdown("#### 建议")
                    if prob_value >= 70:
                        st.markdown("🟢 **高潜力客户** — 优先联系")
                    elif prob_value >= 40:
                        st.markdown("🟡 **中等潜力** — 可纳入营销名单")
                    else:
                        st.markdown("🔴 **低潜力** — 不建议投入资源")

                # Probability bar
                st.markdown("#### 认购概率(0-100%)")
                st.progress(int(prob_value) / 100.0)
                st.caption(
                    f"认购概率: {prob_value:.1f}% | 不认购概率: {100 - prob_value:.1f}%"
                )

            except FileNotFoundError as e:
                st.error(f"模型未找到: {e}")
            except (ValueError, RuntimeError) as e:
                st.error(f"预测出错: {e}")

else:
    # Model not available
    st.warning("⚠️ 模型尚未训练")
    st.markdown("""
    请先训练模型再进行预测。你可以通过以下方式训练:

    1. **点击左侧边栏的「重新训练模型」按钮** — 一键自动训练
    2. 训练过程约需 1-2 分钟，训练完成后页面会自动刷新
    """)

    if st.button("🚀 开始训练模型", type="primary"):
        with st.spinner("正在训练模型，请稍候..."):
            try:
                result = train_model_on_full_data()
                st.success(f"模型训练完成！AUC: {result['auc']:.4f}")
                st.cache_resource.clear()
                st.rerun()
            except (FileNotFoundError, ValueError) as e:
                st.error(f"训练失败: {e}")

# ── Footer ──
st.markdown("---")
st.caption("banksys_sy_xuxq · 在线预测页面")
