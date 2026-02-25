from typing import List, Mapping, Optional

from .model import Person


def find_by_wbs(persons: Mapping[int, Person], wbs: str) -> Person:
    """Locate a person by WBS code."""
    for person in persons.values():
        if person.wbs == wbs:
            return person
    raise ValueError(f"WBS not found: {wbs}")


def filter_subtree(
    persons: Mapping[int, Person],
    root_id: Optional[int] = None,
    root_wbs: Optional[str] = None,
    max_depth: Optional[int] = None,
    gen_min: Optional[int] = None,
    gen_max: Optional[int] = None,
) -> List[Person]:
    """Return subtree members filtered by root, depth and generation range."""
    if root_wbs is not None:
        root = find_by_wbs(persons, root_wbs)
    elif root_id is not None:
        if root_id not in persons:
            raise ValueError(f"root_id not found: {root_id}")
        root = persons[root_id]
    else:
        raise ValueError("Either root_id or root_wbs must be provided")

    result: List[Person] = []

    def dfs(node: Person, depth: int) -> None:
        gen = node.generation or node.depth
        if max_depth is not None and depth > max_depth:
            return
        if gen_max is not None and gen > gen_max:
            return
        if gen_min is None or gen >= gen_min:
            result.append(node)
        for child in node.children:
            dfs(child, depth + 1)

    dfs(root, 0)
    return result
