from typing import Dict, List
from .model import Person


def build_tree(persons: Dict[int, Person]) -> List[Person]:
    for p in persons.values():
        if p.parent_id:
            parent = persons[p.parent_id]
            parent.children.append(p)
    roots = [p for p in persons.values() if p.parent_id is None]
    return roots
