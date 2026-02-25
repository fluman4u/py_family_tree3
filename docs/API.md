# API 文档

## 1. 概述

本文档描述族谱可视化系统提供的所有编程接口，包括 Python 模块 API 和 Web API。

## 2. Python 模块 API

### 2.1 数据模型 API (src/model.py)

#### Person 类

**类定义**：

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

**属性**：

| 属性         | 类型            | 访问权限 | 说明     |
| ---------- | ------------- | ---- | ------ |
| id         | int           | 读写   | 唯一标识符  |
| parent_id  | Optional[int] | 读写   | 父节点 ID |
| wbs        | str           | 读写   | WBS 编码 |
| name       | str           | 读写   | 姓名     |
| gender     | Optional[str] | 读写   | 性别     |
| birth_year | Optional[int] | 读写   | 出生年份   |
| death_year | Optional[int] | 读写   | 逝世年份   |
| generation | Optional[int] | 读写   | 世代数    |
| clan_name  | Optional[str] | 读写   | 氏族名称   |
| location   | Optional[str] | 读写   | 居住地    |
| note       | Optional[str] | 读写   | 备注信息   |
| children   | List[Person]  | 读写   | 子节点列表  |
| depth      | int           | 只读   | WBS 深度 |

**方法**：

| 方法                | 返回类型 | 说明            |
| ----------------- | ---- | ------------- |
| `__post_init__()` | None | 初始化后处理        |
| `depth`           | int  | 获取 WBS 深度（属性） |

---

### 2.2 数据解析 API (src/parser.py)

#### read_family_csv

读取 CSV 文件并返回人员字典。

**函数签名**：

```python
def read_family_csv(path: str) -> Dict[int, Person]
```

**参数**：

| 参数   | 类型  | 必填  | 说明       |
| ---- | --- | --- | -------- |
| path | str | 是   | CSV 文件路径 |

**返回值**：

| 类型                | 说明           |
| ----------------- | ------------ |
| Dict[int, Person] | 以 ID 为键的人员字典 |

**异常**：

| 异常类型              | 触发条件        |
| ----------------- | ----------- |
| ValueError        | 缺少必填字段      |
| ValueError        | ID 格式错误     |
| ValueError        | ID 重复       |
| ValueError        | WBS 重复      |
| ValueError        | 父节点 WBS 不存在 |
| FileNotFoundError | 文件不存在       |

**示例**：

```python
from src.parser import read_family_csv

persons = read_family_csv("data/family.csv")
print(f"共读取 {len(persons)} 人")
```

---

### 2.3 数据校验 API (src/validate.py)

#### validate_family

验证族谱数据的完整性和一致性。

**函数签名**：

```python
def validate_family(persons: Dict[int, Person]) -> None
```

**参数**：

| 参数      | 类型                | 必填  | 说明   |
| ------- | ----------------- | --- | ---- |
| persons | Dict[int, Person] | 是   | 人员字典 |

**返回值**：None

**异常**：

| 异常类型       | 触发条件          |
| ---------- | ------------- |
| ValueError | WBS 重复        |
| ValueError | 世代与 WBS 深度不匹配 |
| ValueError | 父节点不存在        |
| ValueError | WBS 与父节点关系不匹配 |

**示例**：

```python
from src.parser import read_family_csv
from src.validate import validate_family

persons = read_family_csv("data/family.csv")
try:
    validate_family(persons)
    print("校验通过")
except ValueError as e:
    print(f"校验失败: {e}")
```

---

### 2.4 树构建 API (src/tree.py)

#### build_tree

构建家族树结构。

**函数签名**：

```python
def build_tree(persons: Dict[int, Person]) -> List[Person]
```

**参数**：

| 参数      | 类型                | 必填  | 说明   |
| ------- | ----------------- | --- | ---- |
| persons | Dict[int, Person] | 是   | 人员字典 |

**返回值**：

| 类型           | 说明    |
| ------------ | ----- |
| List[Person] | 根节点列表 |

**行为说明**：该函数是幂等的；对同一 `persons` 重复调用不会重复追加子节点。

**示例**：

```python
from src.tree import build_tree

roots = build_tree(persons)
for root in roots:
    print(f"根节点: {root.name}, 子女数: {len(root.children)}")
```

---

### 2.5 过滤筛选 API (src/filter.py)

#### filter_subtree

筛选子树。

**函数签名**：

```python
def filter_subtree(
    persons: Dict[int, Person],
    root_id: Optional[int] = None,
    root_wbs: Optional[str] = None,
    max_depth: Optional[int] = None,
    gen_min: Optional[int] = None,
    gen_max: Optional[int] = None,
) -> List[Person]
```

**参数**：

| 参数        | 类型                | 必填  | 默认值  | 说明      |
| --------- | ----------------- | --- | ---- | ------- |
| persons   | Dict[int, Person] | 是   | -    | 人员字典    |
| root_id   | Optional[int]     | 否*  | None | 根节点 ID  |
| root_wbs  | Optional[str]     | 否*  | None | 根节点 WBS |
| max_depth | Optional[int]     | 否   | None | 最大展开深度  |
| gen_min   | Optional[int]     | 否   | None | 最小世代    |
| gen_max   | Optional[int]     | 否   | None | 最大世代    |

*注：`root_id` 和 `root_wbs` 必须提供其中一个

**返回值**：

| 类型           | 说明       |
| ------------ | -------- |
| List[Person] | 筛选后的人员列表 |

**异常**：

| 异常类型       | 触发条件                   |
| ---------- | ---------------------- |
| ValueError | 未提供 root_id 或 root_wbs |
| ValueError | 指定的 WBS 不存在            |
| ValueError | 指定的 ID 不存在             |

**示例**：

```python
from src.filter import filter_subtree

subset = filter_subtree(persons, root_id=1, max_depth=3)
print(f"筛选结果: {len(subset)} 人")

subset = filter_subtree(persons, root_wbs="1.1", max_depth=2)
```

#### find_by_wbs

根据 WBS 查找人员。

**函数签名**：

```python
def find_by_wbs(persons: Dict[int, Person], wbs: str) -> Person
```

**参数**：

| 参数      | 类型                | 必填  | 说明     |
| ------- | ----------------- | --- | ------ |
| persons | Dict[int, Person] | 是   | 人员字典   |
| wbs     | str               | 是   | WBS 编码 |

**返回值**：

| 类型     | 说明      |
| ------ | ------- |
| Person | 找到的人员对象 |

**异常**：

| 异常类型       | 触发条件    |
| ---------- | ------- |
| ValueError | WBS 不存在 |

---

### 2.6 子树展开 API (src/expand.py)

#### expand_subtree

展开子树。

**函数签名**：

```python
def expand_subtree(
    persons: Dict[int, Person],
    root_id: int,
    max_depth: int
) -> List[Person]
```

**参数**：

| 参数        | 类型                | 必填  | 说明     |
| --------- | ----------------- | --- | ------ |
| persons   | Dict[int, Person] | 是   | 人员字典   |
| root_id   | int               | 是   | 根节点 ID |
| max_depth | int               | 是   | 最大展开深度 |

**返回值**：

| 类型           | 说明       |
| ------------ | -------- |
| List[Person] | 展开后的人员列表 |

---

### 2.7 可视化 API (src/visualize.py)

#### visualize_family

生成可视化 HTML 文件。

**函数签名**：

```python
def visualize_family(
    persons: List[Person],
    output_html: str = "family.html",
    lineage_path: str = "data/lineage.yaml"
) -> None
```

**参数**：

| 参数           | 类型           | 必填  | 默认值                 | 说明     |
| ------------ | ------------ | --- | ------------------- | ------ |
| persons      | List[Person] | 是   | -                   | 人员列表   |
| output_html  | str          | 否   | "family.html"       | 输出文件路径 |
| lineage_path | str          | 否   | "data/lineage.yaml" | 行辈配置路径 |

**返回值**：None

**示例**：

```python
from src.visualize import visualize_family

visualize_family(subset, "output/my_family.html")
visualize_family(subset, "family.html", "data/custom_lineage.yaml")
```

---

### 2.8 行辈系统 API (src/lineage.py)

#### LineageSystem 类

**类定义**：

```python
class LineageSystem:
    def __init__(self, poem: list):
        self.poem = poem
```

**类方法**：

##### from_yaml

从 YAML 文件创建实例。

```python
@classmethod
def from_yaml(cls, path: str) -> LineageSystem
```

**参数**：

| 参数   | 类型  | 必填  | 说明        |
| ---- | --- | --- | --------- |
| path | str | 是   | YAML 文件路径 |

**返回值**：

| 类型            | 说明               |
| ------------- | ---------------- |
| LineageSystem | LineageSystem 实例 |

**实例方法**：

##### generation_char

获取指定世代的行辈字。

```python
def generation_char(self, generation: int) -> Optional[str]
```

**参数**：

| 参数         | 类型  | 必填  | 说明  |
| ---------- | --- | --- | --- |
| generation | int | 是   | 世代数 |

**返回值**：

| 类型            | 说明                   |
| ------------- | -------------------- |
| Optional[str] | 行辈字，世代 <= 0 时返回 None |

##### annotate_name

为姓名添加行辈标注。

```python
def annotate_name(self, name: str, generation: int) -> str
```

**参数**：

| 参数         | 类型  | 必填  | 说明   |
| ---------- | --- | --- | ---- |
| name       | str | 是   | 原始姓名 |
| generation | int | 是   | 世代数  |

**返回值**：

| 类型  | 说明     |
| --- | ------ |
| str | 标注后的姓名 |

**示例**：

```python
from src.lineage import LineageSystem

lineage = LineageSystem.from_yaml("data/lineage.yaml")
print(lineage.generation_char(1))
print(lineage.annotate_name("张三", 3))
```

---

### 2.9 迁徙分析 API (src/migration.py)

#### build_migration_timeline

构建迁徙时间轴。

**函数签名**：

```python
def build_migration_timeline(persons: Dict[int, Person]) -> Dict[int, List[dict]]
```

**参数**：

| 参数      | 类型                | 必填  | 说明   |
| ------- | ----------------- | --- | ---- |
| persons | Dict[int, Person] | 是   | 人员字典 |

**返回值**：

| 类型                    | 说明         |
| --------------------- | ---------- |
| Dict[int, List[dict]] | 按年份排序的迁徙记录 |

**返回结构**：

```python
{
    1800: [
        {"name": "张始祖", "location": "陕西西安", "wbs": "1"}
    ],
    1825: [
        {"name": "张一", "location": "陕西西安", "wbs": "1.1"}
    ]
}
```

**示例**：

```python
from src.migration import build_migration_timeline

timeline = build_migration_timeline(persons)
for year, entries in sorted(timeline.items()):
    for entry in entries:
        print(f"{year}: {entry['name']} -> {entry['location']}")
```

---

### 2.10 数据生成 API (src/generator.py)

#### generate_family_data

生成随机族谱数据。

**函数签名**：

```python
def generate_family_data(
    num_roots: int = 1,
    max_depth: int = 5,
    max_children: int = 3,
    output_path: str = "data/random_family.csv"
) -> List[dict]
```

**参数**：

| 参数           | 类型  | 必填  | 默认值                      | 说明      |
| ------------ | --- | --- | ------------------------ | ------- |
| num_roots    | int | 否   | 1                        | 根节点数量   |
| max_depth    | int | 否   | 5                        | 最大世代深度  |
| max_children | int | 否   | 3                        | 每人最多子女数 |
| output_path  | str | 否   | "data/random_family.csv" | 输出文件路径  |

**返回值**：

| 类型         | 说明        |
| ---------- | --------- |
| List[dict] | 生成的人员数据列表 |

**示例**：

```python
from src.generator import generate_family_data

data = generate_family_data(
    num_roots=2,
    max_depth=4,
    output_path="data/test.csv"
)
print(f"生成了 {len(data)} 人")
```

---

## 3. Web API

### 3.1 概述

Web 版本基于 Flask 框架，提供简单的表单提交接口。

**基础 URL**: `http://127.0.0.1:5000`

### 3.2 端点列表

| 端点                    | 方法   | 说明       |
| --------------------- | ---- | -------- |
| `/`                   | GET  | 显示主页     |
| `/`                   | POST | 生成族谱图    |
| `/static/family.html` | GET  | 获取生成的族谱图 |

### 3.3 端点详情

#### GET /

显示主页，包含族谱选择表单和迁徙时间轴。

**请求**：无参数

**响应**：HTML 页面

**页面内容**：

- 根节点选择下拉框
- 展开层数输入框
- 生成按钮
- 族谱图 iframe
- 迁徙时间轴

---

#### POST /

生成指定参数的族谱图。

**请求参数**：

| 参数       | 类型  | 必填  | 说明        |
| -------- | --- | --- | --------- |
| root_wbs | str | 是   | 根节点 WBS   |
| depth    | int | 否   | 展开层数，默认 2 |

**请求示例**：

```html
<form method="post">
  <select name="root_wbs">
    <option value="1">1 - 张始祖</option>
    <option value="1.1">1.1 - 张一</option>
  </select>
  <input type="number" name="depth" value="3">
  <button type="submit">生成图谱</button>
</form>
```

**响应**：重定向到主页，族谱图已更新

---

#### GET /static/family.html

获取生成的族谱图 HTML 文件。

**请求**：无参数

**响应**：HTML 文件（pyvis 生成的交互式网络图）

---

## 4. 完整使用示例

### 4.1 基本使用流程

```python
from src.parser import read_family_csv
from src.validate import validate_family
from src.tree import build_tree
from src.filter import filter_subtree
from src.visualize import visualize_family
from src.migration import build_migration_timeline

persons = read_family_csv("data/family.csv")
validate_family(persons)
build_tree(persons)

subset = filter_subtree(persons, root_id=1, max_depth=3)
visualize_family(subset, "family.html")

timeline = build_migration_timeline(persons)
for year, entries in timeline.items():
    for entry in entries:
        print(f"{year}: {entry['name']} - {entry['location']}")
```

### 4.2 自定义行辈配置

```python
from src.lineage import LineageSystem
from src.visualize import visualize_family

lineage = LineageSystem.from_yaml("data/custom_lineage.yaml")
print(f"第5代行辈字: {lineage.generation_char(5)}")

visualize_family(subset, "family.html", "data/custom_lineage.yaml")
```

### 4.3 按世代范围筛选

```python
from src.filter import filter_subtree

subset = filter_subtree(
    persons,
    root_wbs="1",
    gen_min=2,
    gen_max=4
)
print(f"第2-4代共 {len(subset)} 人")
```

### 4.4 遍历家族树

```python
def print_tree(node, indent=0):
    print("  " * indent + f"{node.name} ({node.wbs})")
    for child in node.children:
        print_tree(child, indent + 1)

roots = build_tree(persons)
for root in roots:
    print_tree(root)
```

---

## 5. 错误处理

### 5.1 常见错误

| 错误类型              | 错误信息                   | 原因           | 解决方案             |
| ----------------- | ---------------------- | ------------ | ---------------- |
| ValueError        | missing required field | 缺少必填字段       | 检查 CSV 文件        |
| ValueError        | duplicated id          | ID 重复        | 确保 ID 唯一         |
| ValueError        | duplicated wbs         | WBS 重复       | 确保 WBS 唯一        |
| ValueError        | parent wbs not found   | 父节点不存在       | 检查 WBS 编码        |
| ValueError        | Generation mismatch    | 世代不匹配        | 检查 generation 字段 |
| ValueError        | WBS-parent mismatch    | WBS 与父节点关系错误 | 检查 WBS 编码规则      |
| FileNotFoundError | 文件不存在                  | 文件路径错误       | 检查文件路径           |

### 5.2 错误处理示例

```python
from src.parser import read_family_csv
from src.validate import validate_family

try:
    persons = read_family_csv("data/family.csv")
    validate_family(persons)
    print("数据加载成功")
except FileNotFoundError:
    print("文件不存在，请检查路径")
except ValueError as e:
    print(f"数据格式错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```


### 3.4 Web 参数校验（web/app.py）

- `depth` 必须为整数，且范围为 `0~10`。
- 非法输入时返回页面并展示错误信息，不会导致服务崩溃。
- POST 生成图文件使用 `family_<uuid>.html`，避免多请求覆盖同一静态文件。


### 3.5 Web JSON API：`GET /api/tree`

查询参数：
- `root_wbs`：根节点 WBS（可选，默认根节点）
- `depth`：展开深度，范围 0~10
- `gen_min` / `gen_max`：代际过滤（可选）

返回：
- `nodes`：节点数组
- `edges`：边数组（`from` / `to`）

错误：
- 参数非法返回 `400` + `{"error": "..."}`

### 3.6 分层组件

- `CsvFamilyRepository`（`src/repository.py`）：负责从 CSV 载入人员数据。
- `FamilyTreeService`（`src/service.py`）：负责校验、建树、筛选、迁徙时间轴和 API payload 构建。
