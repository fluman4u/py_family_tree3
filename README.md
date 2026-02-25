# 族谱可视化系统

一个符合软件工程规范的族谱可视化软件，支持 CSV 数据维护、Web 可视化、行辈自动标注、迁徙时间轴分析，可打包为桌面应用。

## 项目特点

- **人工可维护**：CSV 格式，方便编辑
- **严格校验**：WBS 编码、世代关系自动校验
- **交互可视化**：彩色族谱图，支持拖拽缩放
- **行辈系统**：自动根据世代标注行辈字
- **迁徙分析**：地域迁徙时间轴
- **桌面应用**：可打包为独立 EXE

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备数据

编辑 `data/family.csv` 录入族谱数据，或运行生成随机测试数据：

```bash
python src/generator.py
```

### 3. 运行命令行版本

```bash
python app.py
```

生成 `family.html`，用浏览器打开查看。

### 4. 运行 Web 版本

```bash
python web/app.py
```

浏览器打开 `http://127.0.0.1:5000`，可选择根节点和展开层数。

### 5. 打包桌面应用

```bash
pyinstaller --onefile desktop/main.py
```

生成 `dist/族谱可视化系统.exe`（Windows 场景）。

**Debian/Linux 打包与运行（推荐）**

```bash
pyinstaller --noconfirm desktop/main.spec
chmod +x dist/family-tree
./dist/family-tree
```

> 说明：`desktop/main.spec` 已包含 `web`/`src` 模块与模板/数据，避免 `ModuleNotFoundError: No module named web`。

## 项目结构

```
family_tree/
├── data/
│   ├── family.csv          # 族谱数据
│   └── lineage.yaml        # 行辈配置
├── src/
│   ├── model.py            # 数据模型
│   ├── parser.py           # CSV 解析
│   ├── validate.py         # 数据校验
│   ├── tree.py             # 树构建
│   ├── filter.py           # 过滤功能
│   ├── expand.py           # 子树展开
│   ├── visualize.py        # 可视化
│   ├── lineage.py          # 行辈系统
│   ├── migration.py        # 迁徙时间轴
│   └── generator.py        # 随机数据生成
├── web/
│   ├── app.py              # Flask 应用
│   └── templates/
│       └── index.html      # Web 页面
├── desktop/
│   └── main.py             # 桌面入口
├── docs/
│   ├── DESIGN.md           # 设计文档
│   └── CODE_REVIEW_REPORT.md # 代码审查与修复建议
├── app.py                  # 命令行入口
├── tests/                 # pytest 回归测试
├── requirements.txt
└── README.md
```

## CSV 数据格式

```csv
id,wbs,name,gender,birth_year,death_year,generation,clan_name,location,note
1,1,张始祖,M,1800,1870,1,张氏,陕西西安,始祖
2,1.1,张一,M,1825,1890,2,张氏,陕西西安,
```

说明：`parent_id` 由系统根据 `wbs` 自动推导，CSV 中无需维护。解析器会严格校验必填列、未知列与 WBS 格式。

默认测试数据（`data/family.csv`）已扩展至 **10 代**：主支 `1.1` 在第 2~10 代每代提供 **3 个兄弟节点**，并新增 `1.3` 支系连续拓展至第 10 代；其中 `1.3.3` 已延伸到第 10 代，并按代在最右端节点随机增加兄弟节点，用于验证深层级与不均匀分支场景。

## 行辈配置

编辑 `data/lineage.yaml`：

```yaml
clan_name: 张氏
lineage_poem:
  - 忠
  - 厚
  - 传
  - 家
  - 久
  - 诗
  - 书
  - 继
  - 世
  - 长
```

## 许可证

MIT License


## 测试

执行回归测试：

```bash
pytest -q
```

当前项目已包含 `tests/` 目录，覆盖生成器 ID 唯一性、建树幂等性、过滤边界、解析器校验、迁徙时间轴排序、service 层与 Web 参数/API 校验。

工程化质量检查：

```bash
ruff check .
mypy src web tests
```

生产部署示例（Gunicorn）：

```bash
gunicorn -w 2 -b 0.0.0.0:5000 web.app:app
```
