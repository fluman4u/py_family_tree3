import yaml
from typing import Optional


class LineageSystem:
    def __init__(self, poem: list):
        self.poem = poem

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(data["lineage_poem"])

    def generation_char(self, generation: int) -> Optional[str]:
        if generation <= 0:
            return None
        return self.poem[(generation - 1) % len(self.poem)]

    def annotate_name(self, name: str, generation: int) -> str:
        char = self.generation_char(generation)
        if not char:
            return name
        return name[0] + char + name[1:]
