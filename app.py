from src.parser import read_family_csv
from src.validate import validate_family
from src.tree import build_tree
from src.filter import filter_subtree
from src.visualize import visualize_family
from src.migration import build_migration_timeline

persons = read_family_csv("data/family.csv")
validate_family(persons)
build_tree(persons)

# 从任意节点展开
root_id = 1       # 改成你想看的那个人
max_depth = 3     # 展开层数
subtree = filter_subtree(persons, root_id=root_id, max_depth=max_depth)
visualize_family(subtree, "family.html")

print("Visualization saved to family.html")

# 打印迁徙时间轴
timeline = build_migration_timeline(persons)
print("\n迁徙时间轴:")
for year, entries in timeline.items():
    for entry in entries:
        print(f"{year}  {entry['name']}  {entry['location']}")
