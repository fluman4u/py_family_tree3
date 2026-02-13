from collections import defaultdict
from typing import Dict
from .model import Person


def build_migration_timeline(persons: Dict[int, Person]):
    timeline = defaultdict(list)
    for p in persons.values():
        if p.birth_year and p.location:
            timeline[p.birth_year].append({
                "name": p.name,
                "location": p.location,
                "wbs": p.wbs
            })
    return dict(sorted(timeline.items()))
