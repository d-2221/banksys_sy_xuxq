"""Streamlit page: 数据分析 — Interactive EDA for bank marketing dataset."""

import streamlit as st

from app.analysis.eda import (
    dataset_overview,
    get_numeric_summary,
    plot_categorical_distribution,
    plot_correlation_heatmap,
    plot_numeric_distribution,
    plot_target_pie,
)
from app.data.loader import load_train_data

st.set_page_config(page_title="数据分析", page_icon="📊", layout="wide")

st.title("📊 数据分析")
st.markdown("对训练数据进行多维度探索性分析，洞察客户特征与认购行为的关系。")


# ── Load data ──
@st.cache_data
def _load_data():
    return load_train_data()


try:
    df = _load_data()
except FileNotFoundError:
    st.error("未找到训练数据文件，请确保 `data/train.csv` 存在。")
    st.stop()

# ── Overview section ──
st.header("📋 数据集概览")
info = dataset_overview(df)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("总样本数", f"{info['total_rows']:,}")
col2.metric("特征数", info["total_cols"])
col3.metric("认购 (yes)", info["positive_count"])
col4.metric("未认购 (no)", info["negative_count"])
col5.metric("认购率", f"{info['positive_rate']}%")

if info["missing_cells"] > 0:
    st.warning(f"数据存在 {info['missing_cells']} 个缺失值 ({info['missing_pct']}%)")
else:
    st.success("数据无缺失值 ✓")

# Target pie
with st.expander("🎯 目标变量分布", expanded=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_pie = plot_target_pie(df)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        st.markdown("""
        **subscribe (是否认购定期存款)**

        从饼图可以看出数据存在类别不平衡问题：
        - **认购 (yes)** 样本占少数
        - 模型训练时需关注类别不平衡处理
        """)

col_numeric = info["numeric_cols"]
col_categorical = info["categorical_cols"]

# ── Numeric feature analysis ──
st.header("📈 数值特征分析")
selected_num = st.selectbox(
    "选择数值特征",
    col_numeric,
    key="num_select",
    format_func=lambda x: {
        "age": "年龄",
        "duration": "通话时长(秒)",
        "campaign": "联系次数",
        "pdays": "上次联系间隔(天)",
        "previous": "历史联系次数",
        "emp_var_rate": "就业变化率",
        "cons_price_index": "消费价格指数",
        "cons_conf_index": "消费者信心指数",
        "lending_rate3m": "3个月贷款利率",
        "nr_employed": "就业人数",
    }.get(x, x),
)

if selected_num:
    col1, col2 = st.columns([3, 1])
    with col1:
        fig_num = plot_numeric_distribution(df, selected_num)
        st.plotly_chart(fig_num, use_container_width=True)
    with col2:
        stats = get_numeric_summary(df, selected_num)
        st.markdown(f"**{selected_num} 统计摘要**")
        st.metric("均值", stats["mean"])
        st.metric("中位数", stats["median"])
        st.metric("标准差", stats["std"])
        st.metric("最小值", stats["min"])
        st.metric("25%分位", stats["q1"])
        st.metric("75%分位", stats["q3"])
        st.metric("最大值", stats["max"])

# ── Categorical feature analysis ──
st.header("🏷️ 分类特征分析")
selected_cat = st.selectbox(
    "选择分类特征",
    col_categorical,
    key="cat_select",
    format_func=lambda x: {
        "job": "职业",
        "marital": "婚姻状况",
        "education": "教育水平",
        "default": "是否有违约",
        "housing": "是否有房贷",
        "loan": "是否有个人贷款",
        "contact": "联系类型",
        "month": "联系月份",
        "day_of_week": "联系星期",
        "poutcome": "上次营销结果",
    }.get(x, x),
)

if selected_cat:
    fig_cat = plot_categorical_distribution(df, selected_cat)
    st.plotly_chart(fig_cat, use_container_width=True)

# ── Correlation heatmap ──
st.header("🔗 特征相关性")
st.markdown("查看数值特征之间的 Pearson 相关系数。")
fig_corr = plot_correlation_heatmap(df)
st.plotly_chart(fig_corr, use_container_width=True)

# ── Raw data viewer ──
st.header("📄 原始数据预览")
with st.expander("点击展开/收起"):
    st.dataframe(df.head(100), use_container_width=True)
    st.caption(f"显示前 100 行，共 {len(df):,} 行")

# ── Footer ──
st.markdown("---")
st.caption("banksys_sy_xuxq · 数据分析页面")
