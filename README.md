# banksys_sy_xuxq · 银行营销预测系统

基于葡萄牙银行营销数据集(Bank Marketing)的交互式数据分析与在线认购预测 Web 应用。

## 技术栈

- Python 3.11 + Streamlit
- scikit-learn (分类模型)
- Plotly (交互式可视化)
- pytest + ruff (测试与代码检查)
- Docker (容器化部署)

## 快速启动

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app/app.py --server.port 8888
```

### Docker 运行

```bash
docker build -t banksys_sy_xuxq .
docker run -d --name banksys_sy_xuxq -p 8888:8888 banksys_sy_xuxq
```

## 项目结构

```
banksys_sy_xuxq/
├── app/            # 应用源码
│   ├── app.py          # 主入口
│   ├── pages/          # 页面
│   ├── data/           # 数据加载
│   ├── analysis/       # 分析模块
│   └── model/          # 模型训练与预测
├── data/           # 原始数据(不进 Git)
├── models/         # 模型产物(不进 Git)
├── tests/          # 测试
├── standards/      # 项目规范与记忆
└── .github/workflows/ # CI/CD
```

## 功能

1. **数据分析页面** — 多维度交互式 EDA,含分布图、交叉分析、相关性热力图
2. **在线预测系统** — 点选表单输入客户特征,实时预测认购概率

## 许可证

开源项目