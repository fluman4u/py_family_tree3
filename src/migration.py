from collections import defaultdict
from typing import Dict, List, Mapping

from .model import Person


def build_migration_timeline(persons: Mapping[int, Person]) -> Dict[int, List[Dict[str, str]]]:
    """Build a birth-year sorted migration timeline from person records."""
    timeline: Dict[int, List[Dict[str, str]]] = defaultdict(list)
    for person in persons.values():
        if person.birth_year and person.location:
            timeline[person.birth_year].append(
                {
                    "name": person.name,
                    "location": person.location,
                    "wbs": person.wbs,
                }
            )
    return dict(sorted(timeline.items()))
