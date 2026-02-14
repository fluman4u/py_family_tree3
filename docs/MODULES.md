# 模块详细文档

## 1. 概述

本文档详细介绍族谱可视化系统的各个模块，包括模块职责、核心函数、使用示例和注意事项。

## 2. 数据模型模块 (model.py)

### 2.1 模块概述

定义系统核心数据结构 `Person` 类，是整个系统的数据基础。

### 2.2 类定义

```python
@dataclass
class Person:
    id: int
    parent_id: Optional[int]
    wbs: str
    name: str
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    generation: Optional[int] = None
    clan_name: Optional[str] = None
    location: Optional[str] = None
    note: Optional[str] = None
    children: List["Person"] = None
```

### 2.3 属性说明

| 属性         | 类型            | 默认值  | 说明       |
| ---------- | ------------- | ---- | -------- |
| id         | int           | 必填   | 唯一标识符    |
| parent_id  | Optional[int] | None | 父节点 ID   |
| wbs        | str           | 必填   | WBS 编码   |
| name       | str           | 必填   | 姓名       |
| gender     | Optional[str] | None | 性别 (M/F) |
| birth_year | Optional[int] | None | 出生年份     |
| death_year | Optional[int] | None | 逝世年份     |
| generation | Optional[int] | None | 世代数      |
| clan_name  | Optional[str] | None | 氏族名称     |
| location   | Optional[str] | None | 居住地      |
| note       | Optional[str] | None | 备注信息     |
| children   | List[Person]  | []   | 子节点列表    |

### 2.4 方法

#### `__post_init__()`

初始化后处理，确保 `children` 不为 None。

```python
def __post_init__(self):
    if self.children is None:
        self.children = []
```

#### `depth` 属性

计算 WBS 深度，即世代数。

```python
@property
def depth(self) -> int:
    return len(self.wbs.split("."))
```

**返回值**：WBS 深度（整数）

**示例**：

- WBS="1" → depth=1
- WBS="1.1" → depth=2
- WBS="1.1.1" → depth=3

### 2.5 使用示例

```python
from src.model import Person

person = Person(
    id=1,
    parent_id=None,
    wbs="1",
    name="张始祖",
    gender="M",
    birth_year=1800,
    death_year=1870,
    generation=1,
    clan_name="张氏",
    location="陕西西安",
    note="始祖"
)

print(person.depth)
print(person)
```

---

## 3. 数据解析模块 (parser.py)

### 3.1 模块概述

负责读取 CSV 文件并转换为 Person 对象字典，是数据输入的入口。

### 3.2 常量定义

```python
REQUIRED_FIELDS = {"id", "wbs", "name"}
OPTIONAL_FIELDS = {
    "gender", "birth_year", "death_year",
    "generation", "clan_name", "location", "note"
}
```

### 3.3 核心函数

#### `read_family_csv(path: str) -> Dict[int, Person]`

读取 CSV 文件并返回人员字典。

**参数**：

- `path`: CSV 文件路径

**返回值**：

- `Dict[int, Person]`: 以 ID 为键的人员字典

**异常**：

- `ValueError`: 数据格式错误或校验失败

**处理流程**：

```
1. 打开 CSV 文件（utf-8-sig 编码）
2. 遍历每一行数据
   a. 清洗数据（处理空值）
   b. 验证必填字段
   c. 创建 Person 对象
   d. 记录 WBS 到 ID 的映射
3. 根据 WBS 推导 parent_id
4. 返回人员字典
```

**示例**：

```python
from src.parser import read_family_csv

persons = read_family_csv("data/family.csv")
for pid, person in persons.items():
    print(f"{pid}: {person.name}")
```

### 3.4 辅助函数

#### `_clean(value) -> Optional[str]`

清洗数据值，处理各种空值表示。

```python
def _clean(value):
    if value is None:
        return None
    v = value.strip()
    if v in ("", "NA", "N/A", "None", "null", "NULL"):
        return None
    return v
```

#### `_get_parent_wbs(wbs: str) -> Optional[str]`

从 WBS 推导父节点 WBS。

```python
def _get_parent_wbs(wbs: str) -> Optional[str]:
    parts = wbs.split(".")
    if len(parts) == 1:
        return None
    return ".".join(parts[:-1])
```

**示例**：

- `_get_parent_wbs("1")` → `None`
- `_get_parent_wbs("1.1")` → `"1"`
- `_get_parent_wbs("1.1.1")` → `"1.1"`

---

## 4. 数据校验模块 (validate.py)

### 4.1 模块概述

验证族谱数据的完整性和一致性，确保数据质量。

### 4.2 核心函数

#### `validate_family(persons: Dict[int, Person])`

验证族谱数据。

**参数**：

- `persons`: 人员字典

**异常**：

- `ValueError`: 数据校验失败

**校验项**：

| 校验项        | 说明                        | 错误信息示例                       |
| ---------- | ------------------------- | ---------------------------- |
| WBS 唯一性    | 每个 WBS 只能出现一次             | `Duplicated WBS: 1.1`        |
| 世代一致性      | generation 必须等于 WBS 深度    | `Generation mismatch for 张三` |
| 父节点存在性     | parent_id 必须存在于 persons 中 | `parent_id 5 not found`      |
| WBS-父节点一致性 | WBS 必须是父节点 WBS 的子级        | `WBS-parent mismatch`        |

**示例**：

```python
from src.parser import read_family_csv
from src.validate import validate_family

persons = read_family_csv("data/family.csv")
try:
    validate_family(persons)
    print("数据校验通过")
except ValueError as e:
    print(f"数据校验失败: {e}")
```

### 4.3 校验逻辑详解

```python
def validate_family(persons: Dict[int, Person]):
    wbs_map = {}
    for p in persons.values():
        if p.wbs in wbs_map:
            raise ValueError(f"Duplicated WBS: {p.wbs}")
        wbs_map[p.wbs] = p.id

        if p.generation is not None:
            if p.generation != p.depth:
                raise ValueError(
                    f"Generation mismatch for {p.name}: "
                    f"generation={p.generation}, wbs={p.wbs}"
                )

        if p.parent_id:
            if p.parent_id not in persons:
                raise ValueError(f"{p.name}: parent_id {p.parent_id} not found")
            parent = persons[p.parent_id]
            if not p.wbs.startswith(parent.wbs + "."):
                raise ValueError(
                    f"WBS-parent mismatch: {p.wbs} not under {parent.wbs}"
                )
```

---

## 5. 树构建模块 (tree.py)

### 5.1 模块概述

根据父子关系构建家族树结构，建立 children 列表。

### 5.2 核心函数

#### `build_tree(persons: Dict[int, Person]) -> List[Person]`

构建家族树结构。

**参数**：

- `persons`: 人员字典

**返回值**：

- `List[Person]`: 根节点列表（parent_id 为 None 的节点）

**处理逻辑**：

```python
def build_tree(persons: Dict[int, Person]) -> List[Person]:
    for p in persons.values():
        if p.parent_id:
            parent = persons[p.parent_id]
            parent.children.append(p)
    roots = [p for p in persons.values() if p.parent_id is None]
    return roots
```

**示例**：

```python
from src.parser import read_family_csv
from src.validate import validate_family
from src.tree import build_tree

persons = read_family_csv("data/family.csv")
validate_family(persons)
roots = build_tree(persons)

print(f"共有 {len(roots)} 个根节点")
for root in roots:
    print(f"根节点: {root.name}")
```

---

## 6. 过滤筛选模块 (filter.py)

### 6.1 模块概述

提供子树筛选功能，支持按根节点、深度、世代范围过滤。

### 6.2 核心函数

#### `filter_subtree(persons, root_id, root_wbs, max_depth, gen_min, gen_max) -> List[Person]`

筛选子树。

**参数**：

| 参数        | 类型                | 必填  | 说明      |
| --------- | ----------------- | --- | ------- |
| persons   | Dict[int, Person] | 是   | 人员字典    |
| root_id   | Optional[int]     | 否   | 根节点 ID  |
| root_wbs  | Optional[str]     | 否   | 根节点 WBS |
| max_depth | Optional[int]     | 否   | 最大展开深度  |
| gen_min   | Optional[int]     | 否   | 最小世代    |
| gen_max   | Optional[int]     | 否   | 最大世代    |

**返回值**：

- `List[Person]`: 筛选后的人员列表

**注意**：`root_id` 和 `root_wbs` 必须提供其中一个

**示例**：

```python
from src.filter import filter_subtree

subset = filter_subtree(
    persons,
    root_id=1,
    max_depth=3
)

subset = filter_subtree(
    persons,
    root_wbs="1.1",
    max_depth=2,
    gen_min=2,
    gen_max=4
)
```

### 6.3 辅助函数

#### `find_by_wbs(persons: Dict[int, Person], wbs: str) -> Person`

根据 WBS 查找人员。

```python
def find_by_wbs(persons: Dict[int, Person], wbs: str) -> Person:
    for p in persons.values():
        if p.wbs == wbs:
            return p
    raise ValueError(f"WBS not found: {wbs}")
```

---

## 7. 子树展开模块 (expand.py)

### 7.1 模块概述

提供子树展开功能，与 filter.py 功能类似但更简洁。

### 7.2 核心函数

#### `expand_subtree(persons: Dict[int, Person], root_id: int, max_depth: int) -> List[Person]`

展开子树。

**参数**：

- `persons`: 人员字典
- `root_id`: 根节点 ID
- `max_depth`: 最大展开深度

**返回值**：

- `List[Person]`: 展开后的人员列表

**示例**：

```python
from src.expand import expand_subtree

subset = expand_subtree(persons, root_id=1, max_depth=3)
```

---

## 8. 可视化模块 (visualize.py)

### 8.1 模块概述

生成交互式 HTML 族谱图，使用 pyvis 库。

### 8.2 常量定义

```python
GEN_COLORS = [
    "#e6194b", "#3cb44b", "#ffe119", "#4363d8",
    "#f58231", "#911eb4", "#46f0f0", "#f032e6",
    "#bcf60c", "#fabebe"
]
```

不同世代使用不同颜色，循环使用这 10 种颜色。

### 8.3 核心函数

#### `visualize_family(persons, output_html, lineage_path)`

生成可视化 HTML 文件。

**参数**：

| 参数           | 类型           | 默认值                 | 说明     |
| ------------ | ------------ | ------------------- | ------ |
| persons      | List[Person] | 必填                  | 人员列表   |
| output_html  | str          | "family.html"       | 输出文件路径 |
| lineage_path | str          | "data/lineage.yaml" | 行辈配置路径 |

**示例**：

```python
from src.visualize import visualize_family

visualize_family(subset, "output/family.html")
visualize_family(subset, "family.html", "data/custom_lineage.yaml")
```

### 8.4 可视化配置

使用 hierarchical 布局实现自上而下的树状结构：

```json
{
  "layout": {
    "hierarchical": {
      "enabled": true,
      "direction": "UD",
      "sortMethod": "directed",
      "levelSeparation": 150,
      "nodeSpacing": 200
    }
  },
  "physics": {
    "enabled": false
  }
}
```

### 8.5 节点信息

每个节点显示：

- **标签**：姓名 + 行辈标注 + WBS
- **颜色**：根据世代分配
- **提示框**：详细信息（姓名、WBS、世代、行辈、生卒年份、备注）

---

## 9. 行辈系统模块 (lineage.py)

### 9.1 模块概述

管理行辈字系统，支持从 YAML 配置加载和姓名标注。

### 9.2 类定义

```python
class LineageSystem:
    def __init__(self, poem: list):
        self.poem = poem
```

### 9.3 方法

#### `from_yaml(path: str) -> LineageSystem`

从 YAML 文件创建 LineageSystem 实例。

```python
@classmethod
def from_yaml(cls, path: str):
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return cls(data["lineage_poem"])
```

#### `generation_char(generation: int) -> Optional[str]`

获取指定世代的行辈字。

```python
def generation_char(self, generation: int) -> Optional[str]:
    if generation <= 0:
        return None
    return self.poem[(generation - 1) % len(self.poem)]
```

#### `annotate_name(name: str, generation: int) -> str`

为姓名添加行辈标注。

```python
def annotate_name(self, name: str, generation: int) -> str:
    char = self.generation_char(generation)
    if not char:
        return name
    return name[0] + char + name[1:]
```

### 9.4 使用示例

```python
from src.lineage import LineageSystem

lineage = LineageSystem.from_yaml("data/lineage.yaml")

print(lineage.generation_char(1))
print(lineage.generation_char(3))
print(lineage.annotate_name("张三", 3))
```

---

## 10. 迁徙分析模块 (migration.py)

### 10.1 模块概述

分析家族迁徙历史，生成时间轴数据。

### 10.2 核心函数

#### `build_migration_timeline(persons: Dict[int, Person]) -> Dict[int, List[dict]]`

构建迁徙时间轴。

**参数**：

- `persons`: 人员字典

**返回值**：

- `Dict[int, List[dict]]`: 按年份排序的迁徙记录

**返回结构**：

```python
{
    1800: [{"name": "张始祖", "location": "陕西西安", "wbs": "1"}],
    1825: [{"name": "张一", "location": "陕西西安", "wbs": "1.1"}],
    1860: [{"name": "张五", "location": "山西太原", "wbs": "1.2.1"}],
    ...
}
```

### 10.3 使用示例

```python
from src.migration import build_migration_timeline

timeline = build_migration_timeline(persons)
for year, entries in timeline.items():
    for entry in entries:
        print(f"{year}: {entry['name']} - {entry['location']}")
```

---

## 11. 数据生成模块 (generator.py)

### 11.1 模块概述

生成随机测试数据，用于开发和测试。

### 11.2 核心函数

#### `generate_family_data(num_roots, max_depth, max_children, output_path)`

生成随机族谱数据。

**参数**：

| 参数           | 类型  | 默认值                      | 说明      |
| ------------ | --- | ------------------------ | ------- |
| num_roots    | int | 1                        | 根节点数量   |
| max_depth    | int | 5                        | 最大世代深度  |
| max_children | int | 3                        | 每人最多子女数 |
| output_path  | str | "data/random_family.csv" | 输出文件路径  |

**返回值**：

- `List[dict]`: 生成的人员数据列表

### 11.3 使用示例

```python
from src.generator import generate_family_data

generate_family_data(
    num_roots=2,
    max_depth=4,
    max_children=3,
    output_path="data/test_family.csv"
)
```

### 11.4 命令行使用

```bash
python src/generator.py
```

---

## 12. Web 应用模块 (web/app.py)

### 12.1 模块概述

Flask Web 应用，提供 Web 界面交互。

### 12.2 路由定义

| 路由  | 方法   | 功能         |
| --- | ---- | ---------- |
| `/` | GET  | 显示主页       |
| `/` | POST | 生成指定参数的族谱图 |

### 12.3 初始化流程

```python
persons = read_family_csv("data/family.csv")
validate_family(persons)
build_tree(persons)

static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "family.html")
root_person = next(p for p in persons.values() if p.parent_id is None)
subset = filter_subtree(persons, root_id=root_person.id, max_depth=2)
visualize_family(subset, static_path)
```

### 12.4 POST 处理

```python
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        root_wbs = request.form.get("root_wbs")
        depth = int(request.form.get("depth", 2))
        subset = filter_subtree(
            persons,
            root_wbs=root_wbs,
            max_depth=depth
        )
        visualize_family(subset, static_path)
    ...
```

---

## 13. 桌面应用模块 (desktop/main.py)

### 13.1 模块概述

桌面应用入口，自动打开浏览器访问 Web 界面。

### 13.2 实现方式

```python
import webbrowser
from web.app import app

if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run()
```

### 13.3 打包方式

```bash
pyinstaller --onefile desktop/main.py
```

---

## 14. 模块依赖关系图

```
model.py (无依赖)
    ↓
parser.py → model.py
    ↓
validate.py → model.py
    ↓
tree.py → model.py
    ↓
filter.py → model.py
    ↓
lineage.py (无依赖)
    ↓
visualize.py → model.py, lineage.py
    ↓
migration.py → model.py
    ↓
generator.py (无依赖)
    ↓
web/app.py → parser, validate, tree, filter, visualize, migration
    ↓
desktop/main.py → web/app
```
