from typing import Dict, List

from .model import Person


def build_tree(persons: Dict[int, Person]) -> List[Person]:
    """Build parent/child relations from parent_id and return root nodes.

    This function is idempotent: repeated calls on the same `persons` mapping
    produce the same child relationships.
    """
    for p in persons.values():
        p.children = []

    for p in persons.values():
        if p.parent_id is not None:
            parent = persons[p.parent_id]
            parent.children.append(p)

    roots = [p for p in persons.values() if p.parent_id is None]
    return roots
