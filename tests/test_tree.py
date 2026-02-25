from src.parser import read_family_csv
from src.tree import build_tree


def test_build_tree_is_idempotent():
    persons = read_family_csv("data/family.csv")
    build_tree(persons)
    first_edges = sum(len(p.children) for p in persons.values())

    build_tree(persons)
    second_edges = sum(len(p.children) for p in persons.values())

    assert first_edges == second_edges
