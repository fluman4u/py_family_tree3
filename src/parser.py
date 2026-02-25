import csv
import re
from typing import Dict, Optional

from .model import Person

REQUIRED_FIELDS = {"id", "wbs", "name"}
OPTIONAL_FIELDS = {
    "gender",
    "birth_year",
    "death_year",
    "generation",
    "clan_name",
    "location",
    "note",
}
ALLOWED_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS | {"parent_id"}
WBS_PATTERN = re.compile(r"^\d+(?:\.\d+)*$")


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
        return None
    return ".".join(parts[:-1])


def _parse_int(row: dict, field: str, lineno: int) -> Optional[int]:
    value = row.get(field)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Line {lineno}: field '{field}' must be integer, got {value!r}") from exc


def read_family_csv(path: str) -> Dict[int, Person]:
    persons: Dict[int, Person] = {}
    wbs_to_id: Dict[str, int] = {}

    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = set(reader.fieldnames or [])
        missing_required = REQUIRED_FIELDS - fieldnames
        if missing_required:
            raise ValueError(f"CSV missing required columns: {sorted(missing_required)}")

        unknown_fields = fieldnames - ALLOWED_FIELDS
        if unknown_fields:
            raise ValueError(f"CSV contains unknown columns: {sorted(unknown_fields)}")

        for lineno, row in enumerate(reader, start=2):
            row = {k: _clean(v) for k, v in row.items()}
            for field in REQUIRED_FIELDS:
                if not row.get(field):
                    raise ValueError(f"Line {lineno}: missing required field '{field}'")

            pid = _parse_int(row, "id", lineno)
            assert pid is not None

            wbs = row["wbs"]
            if not WBS_PATTERN.match(wbs):
                raise ValueError(f"Line {lineno}: invalid wbs format {wbs!r}; expected digits separated by '.'")

            if any(segment.startswith("0") and segment != "0" for segment in wbs.split(".")):
                raise ValueError(f"Line {lineno}: invalid wbs segment with leading zero in {wbs!r}")

            if wbs in wbs_to_id:
                raise ValueError(f"Line {lineno}: duplicated wbs {wbs}")
            wbs_to_id[wbs] = pid

            generation = _parse_int(row, "generation", lineno)
            birth_year = _parse_int(row, "birth_year", lineno)
            death_year = _parse_int(row, "death_year", lineno)

            if pid in persons:
                raise ValueError(f"Line {lineno}: duplicated id {pid}")

            persons[pid] = Person(
                id=pid,
                parent_id=None,
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

    for pid, person in persons.items():
        parent_wbs = _get_parent_wbs(person.wbs)
        if parent_wbs:
            if parent_wbs in wbs_to_id:
                person.parent_id = wbs_to_id[parent_wbs]
            else:
                raise ValueError(
                    f"Person {person.name} (wbs={person.wbs}): parent wbs {parent_wbs} not found"
                )

    return persons
