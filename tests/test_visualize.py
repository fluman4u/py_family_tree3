from src.filter import filter_subtree
from src.parser import read_family_csv
from src.tree import build_tree
from src.visualize import visualize_family


def test_visualize_non_root_subtree_does_not_require_external_parent(tmp_path):
    persons = read_family_csv("data/family.csv")
    build_tree(persons)

    subset = filter_subtree(persons, root_wbs="1.3", max_depth=2)
    out = tmp_path / "subtree.html"

    visualize_family(subset, str(out), lineage_path="data/lineage.yaml")

    assert out.exists()
