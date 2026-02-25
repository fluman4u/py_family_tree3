# 开发指南

## 1. 概述

本文档面向开发者，介绍如何参与族谱可视化系统的开发，包括开发环境搭建、代码规范、测试方法和扩展开发指南。

## 2. 开发环境搭建

### 2.1 系统要求

- Python 3.8+
- Git
- 推荐使用 VS Code 或 PyCharm

### 2.2 克隆项目

```bash
git clone https://github.com/your-username/py_family_tree3.git
cd py_family_tree3
```

### 2.3 创建虚拟环境

**Windows**：

```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/macOS**：

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2.4 安装开发依赖

```bash
pip install -r requirements.txt
pip install pytest black flake8 mypy
```

### 2.5 配置 IDE

#### VS Code 配置

创建 `.vscode/settings.json`：

```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.analysis.typeCheckingMode": "basic"
}
```

#### PyCharm 配置

1. 设置 Python 解释器为虚拟环境
2. 启用 Flake8 代码检查
3. 配置 Black 为代码格式化工具


### 2.6 运行测试

```bash
pytest -q
```

当前回归测试覆盖：
- 生成器 ID 唯一性
- build_tree 幂等性
- filter_subtree 边界条件（`max_depth=0`）
- 解析器对非法 WBS / 未知列的拒绝
- Web depth 参数校验
- 测试数据约束（10 代；`1.1` 主支每代 2~3 兄弟节点；`1.3` 支系含随机兄弟节点）

## 3. 项目结构

```
py_family_tree3/
├── data/                    # 数据文件
│   ├── family.csv          # 族谱数据
│   └── lineage.yaml        # 行辈配置
├── src/                    # 核心源码
│   ├── __init__.py
│   ├── model.py            # 数据模型
│   ├── parser.py           # CSV 解析
│   ├── validate.py         # 数据校验
│   ├── tree.py             # 树构建
│   ├── filter.py           # 过滤功能
│   ├── expand.py           # 子树展开
│   ├── visualize.py        # 可视化
│   ├── lineage.py          # 行辈系统
│   ├── migration.py        # 迁徙分析
│   └── generator.py        # 数据生成
├── web/                    # Web 应用
│   ├── app.py              # Flask 应用
│   ├── static/             # 静态文件
│   └── templates/          # 模板文件
├── desktop/                # 桌面应用
│   └── main.py             # 入口文件
├── docs/                   # 文档
│   ├── ARCHITECTURE.md
│   ├── DATA_FORMAT.md
│   ├── MODULES.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DEVELOPMENT.md
├── app.py                  # 命令行入口
├── requirements.txt        # 依赖列表
└── README.md               # 项目说明
```

## 4. 代码规范

### 4.1 编码风格

本项目遵循 PEP 8 编码规范，使用 Black 进行代码格式化。

**关键规则**：

- 使用 4 个空格缩进
- 行长度不超过 88 字符（Black 默认）
- 使用 UTF-8 编码
- 不添加注释（除非用户要求）

### 4.2 命名规范

| 类型   | 规范    | 示例                          |
| ---- | ----- | --------------------------- |
| 模块名  | 小写下划线 | `parser.py`                 |
| 类名   | 大驼峰   | `Person`, `LineageSystem`   |
| 函数名  | 小写下划线 | `read_family_csv`           |
| 变量名  | 小写下划线 | `persons`, `root_id`        |
| 常量名  | 大写下划线 | `REQUIRED_FIELDS`           |
| 私有函数 | 前置下划线 | `_clean`, `_get_parent_wbs` |

### 4.3 类型注解

所有公开函数应添加类型注解：

```python
from typing import Dict, List, Optional

def filter_subtree(
    persons: Dict[int, Person],
    root_id: Optional[int] = None,
    max_depth: Optional[int] = None,
) -> List[Person]:
    ...
```

### 4.4 文档字符串

公开函数应添加文档字符串：

```python
def read_family_csv(path: str) -> Dict[int, Person]:
    """
    读取 CSV 文件并返回人员字典。

    Args:
        path: CSV 文件路径

    Returns:
        以 ID 为键的人员字典

    Raises:
        ValueError: 数据格式错误
        FileNotFoundError: 文件不存在
    """
    ...
```

### 4.5 代码检查

运行代码检查：

```bash
flake8 src/ web/ --max-line-length=88
mypy src/ --ignore-missing-imports
```

### 4.6 代码格式化

```bash
black src/ web/ desktop/
```

## 5. 测试

### 5.1 测试框架

使用 pytest 进行测试。

**安装**：

```bash
pip install pytest
```

### 5.2 测试目录结构

```
tests/
├── conftest.py
├── test_generator.py
├── test_parser.py
├── test_tree.py
├── test_filter.py
└── test_web.py
```

### 5.3 测试示例

**test_model.py**：

```python
import pytest
from src.model import Person


def test_person_depth():
    person = Person(id=1, parent_id=None, wbs="1.1.1", name="测试")
    assert person.depth == 3


def test_person_children_init():
    person = Person(id=1, parent_id=None, wbs="1", name="测试")
    assert person.children == []


def test_person_repr():
    person = Person(id=1, parent_id=None, wbs="1", name="张三")
    assert "张三" in repr(person)
```

**test_parser.py**：

```python
import pytest
import tempfile
import os
from src.parser import read_family_csv
from src.model import Person


@pytest.fixture
def sample_csv():
    content = """id,wbs,name,gender,birth_year,death_year,generation,clan_name,location,note
1,1,张始祖,M,1800,1870,1,张氏,陕西西安,始祖
2,1.1,张一,M,1825,1890,2,张氏,陕西西安,
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        f.write(content)
        yield f.name
    os.unlink(f.name)


def test_read_family_csv(sample_csv):
    persons = read_family_csv(sample_csv)
    assert len(persons) == 2
    assert persons[1].name == "张始祖"
    assert persons[2].parent_id == 1


def test_read_family_csv_missing_field():
    content = "id,wbs,name\n1,1,"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        f.write(content)
        path = f.name
    with pytest.raises(ValueError, match="missing required field"):
        read_family_csv(path)
    os.unlink(path)
```

**test_validate.py**：

```python
import pytest
from src.model import Person
from src.validate import validate_family


def test_validate_family_success():
    persons = {
        1: Person(id=1, parent_id=None, wbs="1", name="张始祖", generation=1),
        2: Person(id=2, parent_id=1, wbs="1.1", name="张一", generation=2),
    }
    validate_family(persons)


def test_validate_family_duplicated_wbs():
    persons = {
        1: Person(id=1, parent_id=None, wbs="1", name="张始祖"),
        2: Person(id=2, parent_id=1, wbs="1", name="张一"),
    }
    with pytest.raises(ValueError, match="Duplicated WBS"):
        validate_family(persons)


def test_validate_family_generation_mismatch():
    persons = {
        1: Person(id=1, parent_id=None, wbs="1", name="张始祖", generation=2),
    }
    with pytest.raises(ValueError, match="Generation mismatch"):
        validate_family(persons)
```

### 5.4 运行测试

```bash
pytest tests/ -v
pytest tests/ --cov=src
```

### 5.5 测试覆盖率

安装覆盖率工具：

```bash
pip install pytest-cov
```

生成覆盖率报告：

```bash
pytest tests/ --cov=src --cov-report=html
```

## 6. 扩展开发

### 6.1 添加新字段

**步骤 1**：修改 `src/model.py`

```python
@dataclass
class Person:
    ...
    new_field: Optional[str] = None
```

**步骤 2**：修改 `src/parser.py`

```python
OPTIONAL_FIELDS = {
    ...,
    "new_field"
}

persons[pid] = Person(
    ...,
    new_field=row.get("new_field"),
)
```

**步骤 3**：更新 CSV 格式

```csv
id,wbs,name,...,new_field
1,1,张始祖,...,新字段值
```

### 6.2 添加新的可视化布局

**修改 `src/visualize.py`**：

```python
def visualize_family(
    persons: List[Person],
    output_html: str = "family.html",
    layout: str = "hierarchical"
):
    net = Network(...)

    if layout == "hierarchical":
        net.set_options("...")
    elif layout == "force":
        net.set_options("...")

    ...
```

### 6.3 添加新的数据源

**创建新解析器**：

```python
def read_family_json(path: str) -> Dict[int, Person]:
    import json
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    persons = {}
    for item in data["persons"]:
        persons[item["id"]] = Person(
            id=item["id"],
            wbs=item["wbs"],
            name=item["name"],
            ...
        )

    return persons
```

### 6.4 添加新的 API 端点

**修改 `web/app.py`**：

```python
@app.route("/api/persons")
def api_persons():
    return jsonify([
        {"id": p.id, "name": p.name, "wbs": p.wbs}
        for p in persons.values()
    ])


@app.route("/api/person/<int:person_id>")
def api_person(person_id):
    p = persons.get(person_id)
    if not p:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "id": p.id,
        "name": p.name,
        "wbs": p.wbs,
        ...
    })
```

### 6.5 添加数据库支持

**使用 SQLite**：

```python
import sqlite3

def save_to_db(persons: Dict[int, Person], db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY,
            wbs TEXT UNIQUE,
            name TEXT,
            parent_id INTEGER,
            ...
        )
    """)

    for p in persons.values():
        cursor.execute(
            "INSERT OR REPLACE INTO persons VALUES (?, ?, ?, ?, ...)",
            (p.id, p.wbs, p.name, p.parent_id, ...)
        )

    conn.commit()
    conn.close()


def load_from_db(db_path: str) -> Dict[int, Person]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM persons")
    persons = {}
    for row in cursor.fetchall():
        persons[row[0]] = Person(
            id=row[0],
            wbs=row[1],
            name=row[2],
            ...
        )

    conn.close()
    return persons
```

## 7. 版本控制

### 7.1 Git 工作流

```
main (稳定版本)
  │
  ├── develop (开发分支)
  │     │
  │     ├── feature/new-feature (功能分支)
  │     ├── feature/another-feature
  │     │
  │     └── bugfix/fix-bug (修复分支)
  │
  └── release/v1.0.0 (发布分支)
```

### 7.2 提交规范

使用约定式提交：

```
feat: 添加新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

**示例**：

```
feat: 添加多家族支持功能
fix: 修复 WBS 解析错误
docs: 更新 API 文档
refactor: 重构可视化模块
```

### 7.3 分支管理

```bash
git checkout -b feature/new-feature
git add .
git commit -m "feat: 添加新功能"
git push origin feature/new-feature
```

## 8. 发布流程

### 8.1 版本号规范

使用语义化版本：`MAJOR.MINOR.PATCH`

- MAJOR：不兼容的 API 变更
- MINOR：向后兼容的功能新增
- PATCH：向后兼容的问题修复

### 8.2 发布检查清单

- [ ] 所有测试通过
- [ ] 代码检查无警告
- [ ] 文档已更新
- [ ] CHANGELOG 已更新
- [ ] 版本号已更新

### 8.3 打包发布

**创建发布包**：

```bash
python -m build
```

**上传到 PyPI**：

```bash
twine upload dist/*
```

## 9. 调试技巧

### 9.1 日志调试

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def some_function():
    logger.debug("调试信息")
    logger.info("一般信息")
    logger.warning("警告信息")
    logger.error("错误信息")
```

### 9.2 断点调试

**使用 pdb**：

```python
import pdb

def some_function():
    pdb.set_trace()
    ...
```

**使用 VS Code 调试器**：

创建 `.vscode/launch.json`：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}
```

### 9.3 性能分析

```python
import cProfile

cProfile.run('main_function()')
```

## 10. 常见问题

### Q1: 如何添加新的依赖？

1. 编辑 `requirements.txt`
2. 运行 `pip install -r requirements.txt`
3. 测试新功能

### Q2: 如何处理编码问题？

- CSV 文件使用 `utf-8-sig` 编码
- 读取时指定编码：`open(path, encoding="utf-8-sig")`

### Q3: 如何调试 Web 应用？

```bash
FLASK_DEBUG=1 python web/app.py
```

### Q4: 如何贡献代码？

1. Fork 项目
2. 创建功能分支
3. 提交代码
4. 创建 Pull Request

## 11. 参考资源

- [Python 官方文档](https://docs.python.org/3/)
- [Flask 文档](https://flask.palletsprojects.com/)
- [pyvis 文档](https://pyvis.readthedocs.io/)
- [pytest 文档](https://docs.pytest.org/)
- [Black 代码格式化](https://black.readthedocs.io/)
- [PEP 8 编码规范](https://peps.python.org/pep-0008/)


## 附：Web 应用启动建议

`web/app.py` 提供 `create_app()` 工厂方法，便于测试与后续接入 WSGI 服务。开发模式下可继续使用 `python web/app.py`。
