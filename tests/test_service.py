from src.parser import read_family_csv
from src.service import FamilyTreeService


def test_service_subtree_payload_contains_nodes_and_edges():
    persons = read_family_csv("data/family.csv")
    service = FamilyTreeService.from_persons(persons)

    payload = service.subtree_payload(root_wbs="1.3", max_depth=3)

    assert "nodes" in payload
    assert "edges" in payload
    assert payload["nodes"]
