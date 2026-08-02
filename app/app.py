"""banksys_sy_xuxq — Streamlit 主入口。

提供两个页面:
1. 数据分析:交互式 EDA
2. 在线预测:基于训练的模型预测认购概率

健康检查由 Streamlit 内置的 /_stcore/health 端点提供。
"""

import streamlit as st

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="银行营销预测系统",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar navigation ──
st.sidebar.title("🏦 银行营销系统")
st.sidebar.markdown("---")
st.sidebar.page_link("app.py", label="首页", icon="🏠")
st.sidebar.page_link("pages/01_数据分析.py", label="数据分析", icon="📊")
st.sidebar.page_link("pages/02_在线预测.py", label="在线预测", icon="🔮")
st.sidebar.markdown("---")
st.sidebar.markdown("**数据来源**: Bank Marketing (UCI)")
st.sidebar.markdown("**目标**: 预测客户是否认购定期存款")
st.sidebar.markdown("---")
st.sidebar.caption("banksys_sy_xuxq v1.0")

# ── Main page content ──
st.title("🏦 银行营销预测系统")
st.markdown("""
欢迎使用银行营销预测系统！本系统基于葡萄牙银行营销数据集，提供以下功能：

### 📊 数据分析
对训练数据进行多维度探索性分析，包括：
- 数据集概览与统计摘要
- 数值特征分布（按认购结果分组）
- 分类特征认购率分析
- 特征相关性热力图
- 数据筛选与联动更新

### 🔮 在线预测
基于历史数据训练的机器学习模型，通过输入客户特征实时预测认购概率：
- 点选式表单输入（下拉框、滑块）
- 实时预测结果展示
- 支持一键重新训练模型

---
**开始使用**: 点击左侧导航栏进入「数据分析」或「在线预测」页面。
""")

# Show data summary if available
try:
    from app.analysis.eda import dataset_overview
    from app.data.loader import load_train_data

    df = load_train_data()
    overview = dataset_overview(df)
    st.markdown("---")
    st.subheader("📋 数据概览")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总样本数", overview["total_rows"])
    col2.metric("特征数", overview["total_cols"])
    col3.metric("认购样本", overview["positive_count"])
    col4.metric("认购率", f"{overview['positive_rate']}%")
except FileNotFoundError:
    # Data not available on fresh install — silently show placeholder
    pass
