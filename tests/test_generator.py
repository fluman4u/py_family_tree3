from src.generator import generate_family_data


def test_generate_family_data_ids_are_unique(tmp_path):
    output = tmp_path / "random.csv"
    persons = generate_family_data(num_roots=3, max_depth=5, max_children=3, output_path=str(output))
    ids = [p["id"] for p in persons]
    assert len(ids) == len(set(ids))
    assert output.exists()
