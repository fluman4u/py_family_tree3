from typing import Dict

from .model import Person


def validate_family(persons: Dict[int, Person]):
    wbs_map = {}
    for p in persons.values():
        # WBS 唯一性
        if p.wbs in wbs_map:
            raise ValueError(f"Duplicated WBS: {p.wbs}")
        wbs_map[p.wbs] = p.id
        
        # 世代校验
        if p.generation is not None:
            if p.generation != p.depth:
                raise ValueError(
                    f"Generation mismatch for {p.name}: "
                    f"generation={p.generation}, wbs={p.wbs}"
                )
        
        # parent 校验（从 WBS 推导的关系）
        if p.parent_id:
            if p.parent_id not in persons:
                raise ValueError(f"{p.name}: parent_id {p.parent_id} not found")
            parent = persons[p.parent_id]
            if not p.wbs.startswith(parent.wbs + "."):
                raise ValueError(
                    f"WBS-parent mismatch: {p.wbs} not under {parent.wbs}"
                )
