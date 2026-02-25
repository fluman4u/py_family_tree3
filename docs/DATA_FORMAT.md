# 数据格式文档

## 1. 概述

本文档详细说明族谱可视化系统使用的数据格式，包括族谱数据（CSV）和行辈配置（YAML）两种格式。

## 2. 族谱数据格式 (CSV)

### 2.1 文件位置

```
data/family.csv
```

### 2.2 编码要求

- 推荐编码：UTF-8 with BOM (`utf-8-sig`)
- 此编码可确保 Excel 正确打开中文内容

### 2.3 字段定义

| 字段名        | 类型  | 必填  | 说明                   | 示例    |
| ---------- | --- | --- | -------------------- | ----- |
| id         | int | 是   | 唯一标识符，必须唯一           | 1     |
| wbs        | str | 是   | WBS 编码，表示层级关系        | 1.1.1 |
| name       | str | 是   | 姓名                   | 张三    |
| parent_id  | int | 否   | 兼容字段；推荐不填写，系统以 WBS 推导为准 | -     |
| gender     | str | 否   | 性别，M=男，F=女           | M     |
| birth_year | int | 否   | 出生年份                 | 1850  |
| death_year | int | 否   | 逝世年份                 | 1920  |
| generation | int | 否   | 世代数，应与 WBS 深度一致      | 3     |
| clan_name  | str | 否   | 氏族名称                 | 张氏    |
| location   | str | 否   | 居住地                  | 陕西西安  |
| note       | str | 否   | 备注信息                 | 始祖    |

### 2.4 字段详细说明

#### 2.4.1 id 字段

- **类型**：整数
- **必填**：是
- **唯一性**：必须唯一
- **用途**：作为人员的唯一标识符
- **规则**：
  - 必须为正整数
  - 建议按顺序分配
  - 一旦分配不建议更改

**示例**：

```csv
id,wbs,name,...
1,1,张始祖,...
2,1.1,张一,...
3,1.2,张二,...
```

#### 2.4.2 wbs 字段

WBS（Work Breakdown Structure）编码是本系统的核心概念，用于表示家族成员的层级关系。

- **类型**：字符串
- **必填**：是
- **唯一性**：必须唯一
- **格式**：`层级1.层级2.层级3...`

**编码规则**：

```
1           # 第一代始祖（根节点）
1.1         # 始祖的第一个孩子
1.2         # 始祖的第二个孩子
1.1.1       # 1.1 的第一个孩子
1.1.2       # 1.1 的第二个孩子
1.2.1       # 1.2 的第一个孩子
1.1.1.1     # 第四代
```

**WBS 与世代的关系**：

| WBS     | 深度  | 世代  |
| ------- | --- | --- |
| 1       | 1   | 第1代 |
| 1.1     | 2   | 第2代 |
| 1.1.1   | 3   | 第3代 |
| 1.1.1.1 | 4   | 第4代 |

**推导规则**：

- 父节点 WBS = 子节点 WBS 去掉最后一节
- 例如：`1.2.3` 的父节点 WBS 为 `1.2`

#### 2.4.3 name 字段

- **类型**：字符串
- **必填**：是
- **用途**：人员姓名
- **建议**：使用全名，便于识别

#### 2.4.4 gender 字段

- **类型**：字符串
- **必填**：否
- **可选值**：
  - `M`：男性
  - `F`：女性
- **默认值**：空

#### 2.4.5 birth_year / death_year 字段

- **类型**：整数
- **必填**：否
- **用途**：记录生卒年份
- **应用场景**：
  - 迁徙时间轴分析
  - 世代时间估算

#### 2.4.6 generation 字段

- **类型**：整数
- **必填**：否
- **用途**：显式标注世代
- **校验规则**：必须与 WBS 深度一致
- **说明**：如果不填写，系统会根据 WBS 自动计算

#### 2.4.7 clan_name 字段

- **类型**：字符串
- **必填**：否
- **用途**：记录所属氏族
- **示例**：张氏、李氏、王氏

#### 2.4.8 location 字段

- **类型**：字符串
- **必填**：否
- **用途**：记录居住地
- **应用场景**：迁徙时间轴分析
- **格式建议**：省份+城市，如"陕西西安"

#### 2.4.9 note 字段

- **类型**：字符串
- **必填**：否
- **用途**：备注信息
- **示例**：始祖、过继、入赘等

### 2.5 完整示例

```csv
id,wbs,name,gender,birth_year,death_year,generation,clan_name,location,note
1,1,张始祖,M,1800,1870,1,张氏,陕西西安,始祖
2,1.1,张一,M,1825,1890,2,张氏,陕西西安,
3,1.2,张二,M,1830,1900,2,张氏,陕西西安,
4,1.1.1,张三,M,1850,1920,3,张氏,陕西西安,
5,1.1.2,张四,F,1855,1925,3,张氏,陕西西安,
6,1.2.1,张五,M,1860,1930,3,张氏,山西太原,
7,1.1.1.1,张六,M,1880,1950,4,张氏,陕西西安,
8,1.1.1.2,张七,F,1885,1955,4,张氏,陕西西安,
9,1.2.1.1,张八,M,1890,1960,4,张氏,山西太原,
10,1.1.1.1.1,张九,M,1910,1980,5,张氏,北京,
11,1.2.1.1.1,张十,M,1920,1990,5,张氏,北京,
```

### 2.6 数据校验规则

系统在读取 CSV 文件时会进行以下校验：

#### 2.6.1 必填字段校验

```
错误：Line X: missing required field 'id'
错误：Line X: missing required field 'wbs'
错误：Line X: missing required field 'name'
```

#### 2.6.2 ID 唯一性校验

```
错误：Line X: duplicated id 5
```

#### 2.6.3 WBS 唯一性校验

```
错误：Line X: duplicated wbs 1.1
```

#### 2.6.4 整数字段格式校验

```
错误：Line X: field 'id' must be integer, got 'abc'
错误：Line X: field 'generation' must be integer, got '三'
```

#### 2.6.5 父节点存在性校验

```
错误：Person 张三 (wbs=1.3): parent wbs 1 not found
```

#### 2.6.6 世代一致性校验

```
错误：Generation mismatch for 张三: generation=3, wbs=1.1
```

#### 2.6.7 WBS-父节点一致性校验

```
错误：WBS-parent mismatch: 1.3 not under 1.1
```

#### 2.6.8 WBS 格式校验

```
错误：Line X: invalid wbs format '1..2'; expected digits separated by '\.'
错误：Line X: invalid wbs segment with leading zero in '1.01'
```

#### 2.6.9 未知列校验

```
错误：CSV contains unknown columns: ['foo']
```

### 2.7 空值处理

以下值会被视为空值（null）：

| 输入值    | 处理结果 |
| ------ | ---- |
| 空字符串   | None |
| `NA`   | None |
| `N/A`  | None |
| `None` | None |
| `null` | None |
| `NULL` | None |


### 2.8 默认测试数据约束（当前仓库）

`data/family.csv` 当前采用如下测试数据约束：

- 最大世代：10 代
- 第 2~10 代：每代同父节点下均为 2~3 个兄弟节点（当前为 3）
- `generation` 字段与 WBS 深度一致
- 新增 `1.3` 支系并连续拓展到第 10 代；其中 `1.3.3` 支链延伸至第 10 代，且每代最右端节点随机增加兄弟节点（分支宽度不固定）

该数据用于覆盖深层树构建、代际筛选和可视化同代分支展示（含多分支深链与随机分叉宽度场景）。

## 3. 行辈配置格式 (YAML)

### 3.1 文件位置

```
data/lineage.yaml
```

### 3.2 字段定义

| 字段名          | 类型   | 必填  | 说明         |
| ------------ | ---- | --- | ---------- |
| clan_name    | str  | 是   | 氏族名称       |
| lineage_poem | list | 是   | 行辈诗（行辈字列表） |

### 3.3 完整示例

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

### 3.4 行辈字映射规则

行辈诗按照世代循环使用：

| 世代  | 行辈字 | 说明                   |
| --- | --- | -------------------- |
| 1   | 忠   | lineage_poem[0]      |
| 2   | 厚   | lineage_poem[1]      |
| 3   | 传   | lineage_poem[2]      |
| ... | ... | ...                  |
| 10  | 长   | lineage_poem[9]      |
| 11  | 忠   | 循环回到 lineage_poem[0] |
| 12  | 厚   | 循环回到 lineage_poem[1] |

**计算公式**：

```python
lineage_char = lineage_poem[(generation - 1) % len(lineage_poem)]
```

### 3.5 姓名标注规则

系统会自动为姓名添加行辈字标注：

**原始姓名**：张三（第3代）

**标注后**：张传三

**标注规则**：

```python
annotated_name = name[0] + lineage_char + name[1:]
```

即：姓氏 + 行辈字 + 名字

## 4. 多家族支持

### 4.1 多个 CSV 文件

可以为不同家族创建不同的 CSV 文件：

```
data/
├── zhang_family.csv    # 张氏族谱
├── li_family.csv       # 李氏族谱
└── wang_family.csv     # 王氏族谱
```

### 4.2 多个行辈配置

每个家族可以有独立的行辈配置：

```
data/
├── zhang_lineage.yaml  # 张氏行辈
├── li_lineage.yaml     # 李氏行辈
└── wang_lineage.yaml   # 王氏行辈
```

## 5. 数据迁移

### 5.1 从其他格式导入

#### 从 Excel 导入

1. 在 Excel 中整理数据
2. 另存为 CSV 格式
3. 选择 UTF-8 编码
4. 放入 `data/family.csv`

#### 从数据库导入

可以编写脚本从数据库导出为 CSV 格式：

```python
import csv
import sqlite3

conn = sqlite3.connect('family.db')
cursor = conn.cursor()
cursor.execute('SELECT id, wbs, name, ... FROM persons')

with open('data/family.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'wbs', 'name', ...])
    writer.writerows(cursor.fetchall())
```

### 5.2 数据备份

建议定期备份 CSV 和 YAML 文件：

```bash
cp data/family.csv data/backup/family_20240101.csv
cp data/lineage.yaml data/backup/lineage_20240101.yaml
```

## 6. 常见问题

### Q1: CSV 文件在 Excel 中打开乱码？

**解决方案**：确保文件使用 `utf-8-sig` 编码保存。本系统生成的 CSV 文件默认使用此编码。

### Q2: 如何处理过继/入赘等情况？

**解决方案**：在 `note` 字段中标注，如：

```csv
id,wbs,name,...,note
5,1.1.2,张四,...,过继给1.2
```

### Q3: 如何处理多配偶情况？

**解决方案**：当前版本暂不支持多配偶记录，建议在 `note` 字段中标注配偶信息。

### Q4: WBS 编号可以不连续吗？

**解决方案**：可以不连续，但建议保持连续以便于理解。例如 `1.1, 1.3` 是合法的，但 `1.1, 1.2` 更清晰。

### Q5: 如何处理无后代的成员？

**解决方案**：正常录入即可，该成员不会有子节点。WBS 编码不会为其分配子编号。
