import csv
from typing import Dict, List, Optional
from .model import Person

REQUIRED_FIELDS = {"id", "wbs", "name"}
OPTIONAL_FIELDS = {
    "gender", "birth_year", "death_year",
    "generation", "clan_name", "location", "note"
}


def _clean(value):
    if value is None:
        return None
    v = value.strip()
    if v in ("", "NA", "N/A", "None", "null", "NULL"):
        return None
    return v


def _get_parent_wbs(wbs: str) -> Optional[str]:
    """从 WBS 推导父节点 WBS"""
    parts = wbs.split(".")
    if len(parts) == 1:
        return None  # 始祖节点
    return ".".join(parts[:-1])


def read_family_csv(path: str) -> Dict[int, Person]:
    persons: Dict[int, Person] = {}
    wbs_to_id: Dict[str, int] = {}
    
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for lineno, row in enumerate(reader, start=2):
            row = {k: _clean(v) for k, v in row.items()}
            # 必填字段校验
            for field in REQUIRED_FIELDS:
                if not row.get(field):
                    raise ValueError(f"Line {lineno}: missing required field '{field}'")
            try:
                pid = int(row["id"])
            except ValueError:
                raise ValueError(f"Line {lineno}: id must be integer")
            
            wbs = row["wbs"]
            if wbs in wbs_to_id:
                raise ValueError(f"Line {lineno}: duplicated wbs {wbs}")
            wbs_to_id[wbs] = pid
            
            generation = int(row["generation"]) if row.get("generation") else None
            birth_year = int(row["birth_year"]) if row.get("birth_year") else None
            death_year = int(row["death_year"]) if row.get("death_year") else None
            
            if pid in persons:
                raise ValueError(f"Line {lineno}: duplicated id {pid}")
            
            persons[pid] = Person(
                id=pid,
                parent_id=None,  # 暂时设为 None，后面再推导
                wbs=wbs,
                name=row["name"],
                gender=row.get("gender"),
                birth_year=birth_year,
                death_year=death_year,
                generation=generation,
                clan_name=row.get("clan_name"),
                location=row.get("location"),
                note=row.get("note"),
            )
    
    # 第二轮：从 WBS 推导 parent_id
    for pid, person in persons.items():
        parent_wbs = _get_parent_wbs(person.wbs)
        if parent_wbs:
            if parent_wbs in wbs_to_id:
                person.parent_id = wbs_to_id[parent_wbs]
            else:
                raise ValueError(f"Person {person.name} (wbs={person.wbs}): parent wbs {parent_wbs} not found")
    
    return persons
