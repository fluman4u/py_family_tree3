from typing import Dict, List

from .model import Person


def expand_subtree(
    persons: Dict[int, Person],
    root_id: int,
    max_depth: int
) -> List[Person]:
    root = persons[root_id]
    result = []

    def dfs(node: Person, depth: int):
        if depth > max_depth:
            return
        result.append(node)
        for child in node.children:
            dfs(child, depth + 1)

    dfs(root, 0)
    return result
