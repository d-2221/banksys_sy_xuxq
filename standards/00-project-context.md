# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。
> **填写方式**:把 `<...>` 替换成真实内容;用不到的行删掉。

---

## 1. 项目是什么

- **项目名称**:`banksys_sy_xuxq` — 银行营销预测系统
- **一句话目标**:基于葡萄牙银行营销数据集(Bank Marketing),构建一个交互式数据分析与在线认购预测的 Web 应用,帮助银行营销人员理解客户特征,并实时预测客户是否会认购定期存款。
- **使用者/受益者**:银行营销分析人员 — 通过数据洞察和在线预测工具,更精准地定位潜在客户,提高营销活动 ROI。
- **核心功能**:
  - 数据分析交互页面:对训练数据进行多维度探索性分析(EDA),含统计摘要、分布可视化、交叉分析、特征相关性等。
  - 在线预测系统:基于训练数据离线训练分类模型,用户通过点选表单(下拉选择/滑块/单选框)输入客户特征,实时返回认购概率预测。
- **输入/数据**:数据来自 `data/` 目录下的 `train.csv`(22500 行,22 列)和 `test.csv`(7500 行,22 列)。数据为葡萄牙银行营销活动历史记录,目标变量 `subscribe`(是否认购定期存款)。数据不进 Git,通过 `.gitignore` 排除。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 项目要求,兼容主流 ML 库 |
| Web/数据框架 | Streamlit | 项目要求,快速构建交互式数据应用,天然支持表单与可视化 |
| ML 模型 | scikit-learn (LogisticRegression / RandomForestClassifier) | 成熟、易部署、适合教学场景的二分类任务 |
| 可视化 | Plotly (辅以 Matplotlib/Seaborn) | 交互式图表,适配 Streamlit 生态 |
| 测试 | pytest | 项目要求,Python 生态标准 |
| 格式/静态检查 | ruff | 项目要求,替代 flake8+isort+black,零配置 |
| 打包/运行 | Docker | 项目要求,容器化部署,保证环境一致 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
banksys_sy_xuxq/
├── standards/                   # AI 项目记忆与通用规范
│   ├── README.md
│   ├── 00-project-context.md
│   ├── 01-requirements.md
│   ├── PROGRESS.md
│   ├── 02-coding-standards.md
│   ├── 03-testing-standards.md
│   ├── 04-git-workflow.md
│   ├── 05-cicd-standards.md
│   └── 06-ai-collab-protocol.md
├── data/                        # 原始数据(不进 Git)
│   ├── train.csv
│   └── test.csv
├── app/                         # 应用源码
│   ├── __init__.py
│   ├── app.py                   # Streamlit 主入口,两个页面路由
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── 01_数据分析.py        # 数据分析交互页面
│   │   └── 02_在线预测.py        # 在线预测系统页面
│   ├── data/                    # 数据加载与预处理模块
│   │   ├── __init__.py
│   │   └── loader.py
│   ├── analysis/                # 分析模块(统计、图表)
│   │   ├── __init__.py
│   │   └── eda.py
│   └── model/                   # 模型训练与预测模块
│       ├── __init__.py
│       ├── train.py             # 离线训练脚本
│       └── predict.py           # 加载模型做预测
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── test_loader.py
│   ├── test_eda.py
│   ├── test_model.py
│   └── test_predict.py
├── models/                      # 训练产物(模型 pkl,不进 Git)
│   └── .gitkeep
├── requirements.txt             # 生产运行依赖
├── requirements-dev.txt         # 本地/CI 检查依赖
├── Dockerfile                   # Docker 镜像构建
├── .dockerignore
├── .gitignore
├── .github/workflows/
│   ├── ci.yml                   # CI: PR 触发,格式检查+测试+构建
│   └── cd.yml                   # CD: main 合并触发,自动部署
└── README.md                    # 项目说明、启动方式、环境变量
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest` |
| 覆盖率 | 核心模块(app.data, app.analysis, app.model) >= 80% |
| 构建 | `docker build` 成功 |
| 业务/模型指标 | 模型 AUC >= 0.75(训练集交叉验证);预测接口响应时间 < 2s |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 大文件、数据集、模型产物(`data/`、`models/`)不进 Git,通过 `.gitignore` 排除。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。

## 6. 部署/CI 占位符取值

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys_sy_xuxq` | 应用名/镜像名/容器名 |
| `<DEPLOY_DIR>` | `/opt/banksys_sy_xuxq` | 服务器部署目录 |
| `<PORT>` | `8888` | 服务端口 |
| `<PORT_MAX>` | `8889` | 端口回退上限 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/health` | 健康检查地址(Streamlit 的 health endpoint) |
| `<SSH_USER>` | `root` | 部署用户(需在 Secrets 中配置) |
| `<SSH_HOST>` | 待定 | 服务器公网 IP 或域名(需在 Secrets 中配置) |