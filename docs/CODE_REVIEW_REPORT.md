# 代码审查与改进建议（2026-02）

> 范围：`src/`、`web/`、`desktop/`、入口脚本与关键模板。本文聚焦可维护性、正确性、健壮性、可测试性与工程化成熟度。

## 总体结论

项目结构清晰、模块职责边界较明确，核心流程（解析 → 校验 → 建树 → 过滤 → 可视化）可运行，文档也较完整。

但当前版本仍有若干**高优先级正确性问题**与**可扩展性隐患**，建议优先修复以下 3 项：

1. `src/generator.py` 中 ID 生成策略会产生重复 ID（已可复现）。
2. `src/tree.py` 的 `build_tree` 不是幂等函数，重复调用会导致 children 重复累积。
3. `web/app.py` 在请求路径上直接写共享静态文件 `web/static/family.html`，并且缺少表单输入健壮性校验。

---

## 重点问题与建议

### P0：随机数据生成存在重复 ID 风险（正确性）

**位置**：`src/generator.py`

- 当前通过 `build_tree(current_id + len(persons), ...)` 递归分配 ID，依赖全局可变长度 `len(persons)`，会导致不同分支在某些顺序下出现碰撞。
- 该问题会直接破坏解析环节对 `id` 唯一性的假设。

**建议**：

- 用单调递增计数器（如闭包变量、`itertools.count`）统一分配 ID。
- 增加生成后断言：`len(ids) == len(set(ids))`。
- 为 `generator` 添加最小单测：多次随机生成并校验唯一性。

### P0：建树函数非幂等（重复调用会污染内存状态）

**位置**：`src/tree.py`

- `build_tree` 直接 `append` 子节点，但未先清空 `children`。
- 在同一进程内重复调用会把子节点重复挂载。

**建议**：

- 进入主循环前先对所有节点执行 `p.children = []`。
- 或改为返回新的不可变邻接结构，避免修改输入对象。
- 增加幂等性测试：连续调用两次后，边数不应变化。

### P1：Web 层并发与输入处理健壮性不足

**位置**：`web/app.py`

- 所有请求共享输出文件 `web/static/family.html`，多用户并发时会互相覆盖。
- `depth = int(request.form.get("depth", 2))` 对非法输入会抛 `ValueError`，导致 500。
- 应用导入时即加载与构图，启动阶段失败时会阻断服务。

**建议**：

- 将图谱按会话/请求参数生成独立文件名（或前端改为 JSON + 客户端渲染）。
- 对 `depth` 做区间和类型校验，失败返回 4xx 与提示。
- 把数据加载放入应用工厂或惰性初始化，并提供启动健康检查。

### P1：过滤逻辑对“0/None”采用 truthy 判断，语义易错

**位置**：`src/filter.py`

- `elif root_id:`、`if gen_min`、`if gen_max` 采用真值判断，语义依赖“0 不合法”的隐含前提。

**建议**：

- 改为显式 `is not None` 判断。
- 把 API 约束写进 docstring 与参数校验。

### P2：解析器校验粒度可提升

**位置**：`src/parser.py`、`src/validate.py`

- 尚未校验 `wbs` 的格式合法性（如连续点、非数字片段、前导零策略）。
- `OPTIONAL_FIELDS` 常量未被使用，容易造成“声明与行为不一致”。

**建议**：

- 增加 WBS 正则校验（例如 `^\d+(\.\d+)*$`）。
- 将 CSV 字段白名单策略落实到解析逻辑（未知字段告警或拒绝）。
- 补充“错误上下文”信息（行号 + 字段值 + 建议修复方式）。

### P2：可视化层可配置性不足

**位置**：`src/visualize.py`

- 画布尺寸、布局参数、颜色盘等写死在代码中。

**建议**：

- 提供 `VisualizationConfig` 数据类或配置文件。
- 把“代际颜色策略”“节点 tooltip 模板”抽成策略函数，降低耦合。

---

## 工程化完善建议

### 1) 测试体系

- 引入 `pytest`，至少覆盖：
  - 解析正确路径 + 异常路径；
  - 建树幂等性；
  - 过滤边界（`max_depth=0`、`gen_min/gen_max` 组合）；
  - 迁徙时间轴排序。
- 对已发现 bug 添加回归测试，防止再次引入。

### 2) 代码质量与类型

- 开启 `ruff`（lint + import sort）与 `mypy`（逐步严格）。
- 为关键公开函数补全 docstring 与类型细化（如 `Mapping[int, Person]`）。

### 3) 运行与部署

- Web 运行建议从 Flask 内置开发服务器迁移到 `gunicorn/uwsgi`（生产）。
- 增加日志分级（info/warn/error）与错误监控埋点。
- 为 `data/` 提供样例与 schema 说明，降低录入风险。

### 4) 架构演进方向（中期）

- 将“读写数据”和“图谱计算”解耦，形成 service 层。
- 逐步引入仓储层（CSV 只是一种实现），后续可平滑迁移到 SQLite/PostgreSQL。
- 为 Web 端增加 API（JSON）并前端异步渲染，避免频繁写 HTML 文件。

---

## 建议执行顺序（两周）

- **第 1 周（稳定性优先）**：修复 generator ID、build_tree 幂等、web 输入校验；补 6~10 个回归测试。
- **第 2 周（可维护性）**：引入 ruff/pytest/mypy 基线；提炼配置对象；补充数据 schema 与错误提示。



## 工程化建议落地状态

- ✅ 测试体系：补齐了解析正常路径、过滤 `gen_min/gen_max` 组合、迁徙时间轴排序、service/API 回归测试。
- ✅ 代码质量与类型：已引入 `ruff` 与 `mypy` 基线配置（`pyproject.toml`），并通过本地检查。
- ✅ 运行与部署：Web 增加结构化日志与异常日志埋点；文档补充 Gunicorn 生产运行建议。
- ✅ 数据与 schema：补充 `data/family.schema.json`，并在数据格式文档中说明。
- ✅ 架构演进（中期项先落地最小版本）：新增 repository/service 分层，Web 增加 `/api/tree` JSON 接口，支持前端异步渲染演进。
