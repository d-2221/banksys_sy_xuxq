# PROGRESS · banksys_sy_xuxq 银行营销预测系统 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by AI)

- **阶段**:`CI 全绿 — 等待人工审核合并与 CD 部署`
- **上一步完成**:全部模块开发完成 + 本地 CI 自检全绿 + GitHub CI 全绿(ruff format/lint 通过, 41 tests 通过, 核心模块覆盖率 99%, Docker build 成功)
- **下一步 (TODO 第一条)**:人工审核 PR → 合并 → CD 自动部署
- **阻塞项**:CD 需要目标服务器可达(SSH_HOST + SSH_USER + SSH_PRIVATE_KEY 已在 Secrets 中配置)

---

## 待办清单 (TODO,按优先级)

### 六步流程第①步:建仓 + 配 Secrets ✅

- [x] 用 `gh` 创建 GitHub 仓库 `banksys_sy_xuxq`(开源仓库,含 README、.gitignore)
- [x] ✋ 确认门 1:提示人类配置 GitHub Secrets ✅

### 六步流程第②步:开 feature 分支 ✅

- [x] 从 main 切出 feature 分支 `feature/1-init-project-structure`

### 六步流程第③步:本地模块化开发(逐模块实现) ✅

- [x] **模块 1:项目骨架** — app/ 目录结构、requirements.txt、requirements-dev.txt、.gitignore、Dockerfile、.dockerignore、README.md、CI/CD workflows
- [x] **模块 2:数据加载模块** — app/data/loader.py + 单元测试 (12 tests)
- [x] **模块 3:数据分析页面** — app/analysis/eda.py + app/pages/01_数据分析.py + 单元测试 (15 tests)
- [x] **模块 4:模型训练模块** — app/model/train.py + 单元测试 (9 tests)
- [x] **模块 5:在线预测页面** — app/model/predict.py + app/pages/02_在线预测.py + 单元测试 (5 tests)
- [x] **模块 6:健康检查与主入口** — app/app.py(Streamlit 内置 /_stcore/health)
- [x] 每模块完成后更新 PROGRESS.md 并汇报进度 ✅

### 六步流程第④步:本地 CI 自检 ✅

- [x] ruff format --check . ✅
- [x] ruff check . ✅
- [x] pytest --cov=app.data --cov=app.analysis --cov=app.model --cov-fail-under=80 ✅ (41 tests, 99% coverage)
- [x] 全绿后进入下一步,红则修复重跑 ✅

### 六步流程第④步:本地 CI 自检

- [ ] ruff format --check .
- [ ] ruff check .
- [ ] pytest --cov --cov-fail-under=80
- [ ] 全绿后进入下一步,红则修复重跑

### 六步流程第⑤步:触发 PR ✅

- [x] git push feature 分支 ✅
- [x] gh pr create → CI 在 PR 上复检(含 docker build) ✅
- [x] ✋ 确认门 5:汇报 PR 链接与 CI 状态 ✅

### 六步流程第⑥步:人工审核 → 合并 → CD

- [ ] ✋ 人工 Review + 合并(由人执行,AI 不替人 Merge)
- [ ] CD 自动部署 → 健康检查 → 汇报端口与访问地址
- [ ] 会话结束前更新 PROGRESS.md

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-08-02 | .gitignore 中 `data/` 改为 `/data/` | 避免排除 `app/data/` 目录，导致 `ModuleNotFoundError: No module named 'app.data'` |
| 2026-08-02 | CI 中 PYTHONPATH 使用 `${{ github.workspace }}` | 确保 pytest 能找到本地 app 包 |
| 2026-08-02 | ruff.toml 添加 `known-first-party = ["app"]` | 解决 CI 上 import 排序规则与本地不一致问题 |
| 2026-08-02 | CI 中生成合成测试数据供 docker build 使用 | 真实数据不进 Git,CI runner 上没有原始数据,docker build 需要 data/ 目录存在(即使为空) |
| 2026-08-02 | 采用 Streamlit 多页面架构(app/pages/) | 天然支持数据分析与预测两个独立页面,路由零配置,开发效率高 |
| 2026-08-02 | scikit-learn Pipeline 封装预处理+模型 | 保证训练与预测的预处理一致性,模型可序列化为单一 pkl 文件 |
| 2026-08-02 | 数据与模型产物不进 Git | 遵守 00-project-context.md 不变约束,避免大文件拖慢 clone 和 CI |
| 2026-08-02 | 在线预测页面内置"重新训练"按钮 | 降低运维门槛,非技术用户无需命令行即可触发模型更新 |

---

## 已知坑 (GOTCHAS)

- `.gitignore` 中 `data/` 匹配任意层级的 `data/` 目录，包括 `app/data/` → 必须使用 `/data/` 仅匹配根目录。
- CI 上 `ModuleNotFoundError: No module named 'app'` → 需要设置 `PYTHONPATH` 环境变量或 `pip install -e .`。
- ruff 版本差异可能导致本地与 CI 检查结果不一致 → 精确锁定 ruff 版本如 `ruff>=0.16,<0.17`。
- `Streamlit` 页面文件使用中文名（如 `01_数据分析.py`）→ ruff N999 告警，需在 `ruff.toml` 中忽略。

---

## 里程碑 (DONE)

- [x] 项目需求分析完成
- [x] standards/00-project-context.md 初始化
- [x] standards/01-requirements.md 初始化(含 8 个用户故事)
- [x] standards/PROGRESS.md 初始化(第一批 TODO)
- [x] 仓库创建 + Secrets 配置
- [x] feature 分支创建
- [x] 模块 1-6 全部开发完成
- [x] 本地 CI 自检全绿(ruff + pytest + coverage)
- [x] GitHub CI 全绿(格式检查、lint、测试、Docker build 全部通过)

> 反臃肿:里程碑超过 15 条时,把更早内容合并成一行摘要,保持本文件可快速阅读。