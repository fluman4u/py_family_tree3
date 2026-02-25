from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Person:
    id: int
    parent_id: Optional[int]
    wbs: str
    name: str
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    generation: Optional[int] = None
    clan_name: Optional[str] = None
    location: Optional[str] = None
    note: Optional[str] = None
    children: list["Person"] = field(default_factory=list)

    @property
    def depth(self) -> int:
        return len(self.wbs.split("."))

    def __repr__(self):
        return f"<Person {self.wbs} {self.name}>"
