# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 老师 / 产品 / 客户 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI/CD · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构、测试、CI 与 CD,
以便 后续每次开发都能自动检查并自动部署。

验收标准:
- AC1: 从 `main` 开 feature 分支完成初始化,不直接 push main。
- AC2: PR 触发 CI,至少包含格式检查、静态检查、单元测试、构建检查。
- AC3: CI 全绿后合并 main。
- AC4: 合并 main 自动触发 CD,部署后健康检查通过。
- AC5: 完成后更新 `standards/PROGRESS.md`。

---

### US-2 数据加载与预处理模块 · 状态: Backlog

作为 **银行营销分析人员**,
我想要 系统能正确加载 CSV 训练数据,并做数据清洗与类型转换,
以便 后续分析和建模使用干净、结构化的数据。

验收标准:
- AC1: Given `train.csv` 存在于 `data/` 目录,When 调用加载函数,Then 返回 Pandas DataFrame,行数=22500,列数=22。
- AC2: Given `test.csv` 存在于 `data/` 目录,When 加载测试数据,Then 返回 DataFrame,行数=7500。
- AC3: Given 含有缺失值的数据,When 执行预处理,Then 缺失值被合理处理(如填充模式值/删除),且不抛出异常。
- AC4: Given 加载后的数据,When 检查列类型,Then 数值列(dtype=float/int)和分类列(dtype=object/str)正确区分。
- AC5: 目标变量 `subscribe` 被编码为二值(0/1)。

技术备注:
- 数据文件不进 Git,通过 `.gitignore` 排除。
- 使用 `pandas` 进行数据加载与处理。

---

### US-3 数据分析交互页面 · 状态: Backlog

作为 **银行营销分析人员**,
我想要 在 Web 页面上通过交互式图表和统计摘要探索训练数据,
以便 直观理解客户特征分布、各特征与认购目标的关系,辅助营销决策。

验收标准:
- AC1: Given 用户访问数据分析页面,When 页面加载,Then 显示数据集概览(总行数、列数、有无缺失值、正负样本统计)。
- AC2: Given 数据分析页面,When 用户选择某个数值特征(如 age、duration、campaign),Then 显示该特征的分布直方图(含 KDE 曲线),按 subscribe 分组着色。
- AC3: Given 数据分析页面,When 用户选择某个分类特征(如 job、marital、education),Then 显示按 subscribe 分组的堆叠柱状图。
- AC4: Given 数据分析页面,When 用户查看相关性分析,Then 显示数值特征间的热力图(使用 Plotly)。
- AC5: Given 数据分析页面,When 页面包含筛选控件,Then 用户可筛选数据的子集,所有图表随之联动更新。
- AC6: 页面使用 Streamlit 实现,布局清晰,包含侧边栏导航。

技术备注:
- 使用 Plotly 实现交互式图表,支持缩放、悬停详情。
- 分析逻辑写在 `app/analysis/eda.py` 中,便于测试。

---

### US-4 离线模型训练与保存 · 状态: Backlog

作为 **银行营销分析人员**,
我想要 系统能基于历史数据离线训练一个二分类模型并保存,
以便 后续用于在线预测。

验收标准:
- AC1: Given 训练数据,When 执行训练脚本,Then 模型训练完成并保存为 `.pkl` 文件到 `models/` 目录。
- AC2: 训练过程包含数据预处理(特征编码、数值型标准化/归一化)和特征选择。
- AC3: 模型在测试集上的 AUC >= 0.75。
- AC4: 训练脚本输出分类报告(Precision、Recall、F1)和混淆矩阵。
- AC5: 训练过程可重复(固定随机种子)。

技术备注:
- 使用 `scikit-learn` 的 Pipeline 封装预处理 + 模型,确保模型可序列化。
- 模型文件 `models/` 目录不进 Git,通过 `.gitignore` 排除。
- 训练脚本支持 `app/model/train.py` 独立运行。

---

### US-5 在线预测系统 · 状态: Backlog

作为 **银行营销人员**,
我想要 在 Web 页面上通过点选表单(下拉菜单、单选按钮、滑块)输入客户信息,
以便 实时获得该客户是否会认购定期存款的预测结果。

验收标准:
- AC1: Given 用户进入"在线预测"页面,When 页面加载,Then 展示所有模型输入特征的点选式输入控件。
- AC2: Given 用户填写完所有必填字段,When 点击"预测"按钮,Then 系统加载已训练模型,返回预测结果(认购/不认购)和概率值。
- AC3: AC2 的预测结果显示:预测标签(认购/不认购) + 认购概率百分比,并以颜色区分(绿色=高概率,红色=低概率)。
- AC4: Given 模型文件不存在时,When 用户尝试预测,Then 页面显示引导提示"请先运行模型训练",并给出训练按钮。
- AC5: 预测耗时 < 2 秒。
- AC6: 输入控件按特征类型组织:数值型用滑块(slider),类别型用下拉框(selectbox)。

技术备注:
- 使用 `joblib` 加载模型,模型加载有缓存,避免每次预测重新加载。
- 在线预测使用与训练相同的预处理 Pipeline,保证一致性。

---

### US-6 页面一:在线训练触发 · 状态: Backlog

作为 **银行营销分析人员**,
我想要 在"在线预测"页面中内置一个"重新训练模型"按钮,
以便 无需命令行即可触发模型重新训练。

验收标准:
- AC1: Given 用户进入在线预测页面,When 点击"重新训练模型"按钮,Then 系统执行训练流程,并显示训练进度/日志。
- AC2: 训练完成后,页面显示训练结果摘要(AUC、分类报告)。
- AC3: 训练完成后自动更新模型文件,后续预测使用新模型。
- AC4: 如果训练出错,页面显示错误信息,不崩溃。

---

### US-7 健康检查与 Docker 容器化 · 状态: Backlog

作为 **运维人员**,
我想要 应用提供健康检查端点,并打包为 Docker 镜像,
以便 CD 流水线能自动验证部署状态。

验收标准:
- AC1: Given 应用运行中,When 访问 `GET /health`,Then 返回 HTTP 200,内容为 `{"status": "ok"}`。
- AC2: `Dockerfile` 构建成功,镜像名 `banksys_sy_xuxq`。
- AC3: 容器内 Streamlit 运行在端口 8888。
- AC4: `.dockerignore` 排除 `data/`、`models/`、`__pycache__`、`.git`。

---

### US-8 CI/CD 流水线 · 状态: Backlog

作为 **项目开发者**,
我想要 在 GitHub Actions 中配置 CI 和 CD 流水线,
以便 每次 PR 自动检查代码质量,合并 main 自动部署到服务器。

验收标准:
- AC1: CI 流水线(触发:PR): `ruff format --check .` + `ruff check .` + `pytest` + `docker build`。
- AC2: CD 流水线(触发:push main): SSH 到服务器 → docker build → docker run → 健康检查。
- AC3: 所有 Secrets(SSH_PRIVATE_KEY/SSH_HOST/SSH_USER) 通过 GitHub Secrets 注入,不硬编码。
- AC4: 部署失败时 Actions 红灯,不假成功。
- AC5: 部署脚本支持端口回退(8888→8889),避免端口冲突。

---

## 5. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git。
- **可维护**:一需求一小 PR,避免大爆炸式提交。
- **可测试**:核心逻辑(数据加载、EDA、模型训练、预测)必须有单元测试。
- **可部署**:部署后必须有健康检查或等价验证。
- **性能**:在线预测响应时间 < 2 秒。
- **模型质量**:模型 AUC >= 0.75。