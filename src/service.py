from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

from .filter import filter_subtree
from .migration import build_migration_timeline
from .model import Person
from .tree import build_tree
from .validate import validate_family


@dataclass
class FamilyTreeService:
    persons: Dict[int, Person]

    @classmethod
    def from_persons(cls, persons: Mapping[int, Person]) -> "FamilyTreeService":
        loaded = dict(persons)
        validate_family(loaded)
        build_tree(loaded)
        return cls(persons=loaded)

    def roots(self) -> List[Person]:
        return [p for p in self.persons.values() if p.parent_id is None]

    def default_root(self) -> Person:
        root = next((p for p in self.persons.values() if p.parent_id is None), None)
        if root is None:
            raise RuntimeError("No root person found in data")
        return root

    def subtree(
        self,
        *,
        root_id: Optional[int] = None,
        root_wbs: Optional[str] = None,
        max_depth: Optional[int] = None,
        gen_min: Optional[int] = None,
        gen_max: Optional[int] = None,
    ) -> List[Person]:
        return filter_subtree(
            self.persons,
            root_id=root_id,
            root_wbs=root_wbs,
            max_depth=max_depth,
            gen_min=gen_min,
            gen_max=gen_max,
        )

    def migration_timeline(self) -> Dict[int, List[Dict[str, str]]]:
        return build_migration_timeline(self.persons)

    def subtree_payload(
        self,
        *,
        root_id: Optional[int] = None,
        root_wbs: Optional[str] = None,
        max_depth: Optional[int] = None,
        gen_min: Optional[int] = None,
        gen_max: Optional[int] = None,
    ) -> Dict[str, Any]:
        nodes = self.subtree(
            root_id=root_id,
            root_wbs=root_wbs,
            max_depth=max_depth,
            gen_min=gen_min,
            gen_max=gen_max,
        )
        node_ids = {p.id for p in nodes}
        edges = [
            {"from": p.parent_id, "to": p.id}
            for p in nodes
            if p.parent_id is not None and p.parent_id in node_ids
        ]
        return {
            "nodes": [
                {
                    "id": p.id,
                    "parent_id": p.parent_id,
                    "wbs": p.wbs,
                    "name": p.name,
                    "generation": p.generation or p.depth,
                    "birth_year": p.birth_year,
                    "death_year": p.death_year,
                    "location": p.location,
                    "note": p.note,
                }
                for p in nodes
            ],
            "edges": edges,
        }
