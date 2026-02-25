from src.parser import read_family_csv
from src.tree import build_tree
from src.filter import filter_subtree


def test_filter_subtree_supports_zero_depth():
    persons = read_family_csv("data/family.csv")
    build_tree(persons)
    root = next(p for p in persons.values() if p.parent_id is None)

    result = filter_subtree(persons, root_id=root.id, max_depth=0)

    assert len(result) == 1
    assert result[0].id == root.id
