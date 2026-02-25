from dataclasses import dataclass
from typing import Dict, Mapping

from .model import Person
from .parser import read_family_csv


@dataclass
class CsvFamilyRepository:
    """CSV-backed repository for loading family data."""

    path: str

    def load_persons(self) -> Dict[int, Person]:
        return read_family_csv(self.path)


FamilyRepository = Mapping[int, Person]
