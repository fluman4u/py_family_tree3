from typing import Dict, List, Optional

from .model import Person


def find_by_wbs(persons: Dict[int, Person], wbs: str) -> Person:
    for p in persons.values():
        if p.wbs == wbs:
            return p
    raise ValueError(f"WBS not found: {wbs}")


def filter_subtree(
    persons: Dict[int, Person],
    root_id: Optional[int] = None,
    root_wbs: Optional[str] = None,
    max_depth: Optional[int] = None,
    gen_min: Optional[int] = None,
    gen_max: Optional[int] = None,
) -> List[Person]:
    if root_wbs is not None:
        root = find_by_wbs(persons, root_wbs)
    elif root_id is not None:
        if root_id not in persons:
            raise ValueError(f"root_id not found: {root_id}")
        root = persons[root_id]
    else:
        raise ValueError("Either root_id or root_wbs must be provided")

    result = []

    def dfs(node: Person, depth: int):
        gen = node.generation or node.depth
        if gen_min is not None and gen < gen_min:
            return
        if gen_max is not None and gen > gen_max:
            return
        if max_depth is not None and depth > max_depth:
            return
        result.append(node)
        for c in node.children:
            dfs(c, depth + 1)

    dfs(root, 0)
    return result
