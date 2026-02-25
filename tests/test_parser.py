import pytest

from src.parser import read_family_csv


def test_parser_rejects_invalid_wbs(tmp_path):
    csv_file = tmp_path / "invalid_wbs.csv"
    csv_file.write_text(
        "id,wbs,name\n"
        "1,1,张始祖\n"
        "2,1..2,张二\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid wbs format"):
        read_family_csv(str(csv_file))


def test_parser_rejects_unknown_columns(tmp_path):
    csv_file = tmp_path / "unknown.csv"
    csv_file.write_text(
        "id,wbs,name,foo\n"
        "1,1,张始祖,bar\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown columns"):
        read_family_csv(str(csv_file))
