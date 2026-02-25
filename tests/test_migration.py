from src.migration import build_migration_timeline
from src.parser import read_family_csv


def test_migration_timeline_sorted_by_year():
    persons = read_family_csv("data/family.csv")
    timeline = build_migration_timeline(persons)

    years = list(timeline.keys())
    assert years == sorted(years)
