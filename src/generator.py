import csv
import random
from itertools import count
from typing import Dict, List, Optional

FIRST_NAMES = [
    "伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
    "勇", "艳", "杰", "娟", "涛", "明", "超", "秀英", "华", "鹏",
]
LOCATIONS = ["北京", "上海", "广州", "深圳", "杭州", "南京", "西安", "成都", "武汉", "重庆"]
CLAN_NAMES = ["张", "王", "李", "刘", "陈", "杨", "黄", "赵", "周", "吴"]


PersonRow = Dict[str, Optional[object]]


def generate_family_data(
    num_roots: int = 1,
    max_depth: int = 5,
    max_children: int = 3,
    output_path: str = "data/random_family.csv",
) -> List[PersonRow]:
    persons: List[PersonRow] = []
    next_id = count(start=1)
    start_year = 1800

    def generate_person(wbs: str, generation: int, birth_year: int) -> int:
        pid = next(next_id)
        name = random.choice(CLAN_NAMES) + random.choice(FIRST_NAMES)
        gender = random.choice(["M", "F"])
        death_year = birth_year + random.randint(50, 90) if random.random() > 0.1 else None

        persons.append(
            {
                "id": pid,
                "wbs": wbs,
                "name": name,
                "gender": gender,
                "birth_year": birth_year,
                "death_year": death_year,
                "generation": generation,
                "clan_name": random.choice(CLAN_NAMES),
                "location": random.choice(LOCATIONS),
                "note": "",
            }
        )
        return pid

    def build_subtree(wbs: str, generation: int, birth_year: int) -> None:
        if generation > max_depth:
            return
        generate_person(wbs, generation, birth_year)
        num_children = random.randint(0, max_children)
        for i in range(num_children):
            child_wbs = f"{wbs}.{i + 1}"
            child_birth_year = birth_year + random.randint(20, 40)
            build_subtree(child_wbs, generation + 1, child_birth_year)

    for root_idx in range(num_roots):
        build_subtree(str(root_idx + 1), 1, start_year + random.randint(0, 50))

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "id",
            "wbs",
            "name",
            "gender",
            "birth_year",
            "death_year",
            "generation",
            "clan_name",
            "location",
            "note",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(persons)

    ids = [p["id"] for p in persons]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Generated duplicate IDs, please inspect generator logic")

    return persons


if __name__ == "__main__":
    generate_family_data()
    print("Random family data generated!")
