import pytest

from web.app import _parse_depth


@pytest.mark.parametrize("value", ["0", "2", "10"])
def test_parse_depth_valid(value):
    assert _parse_depth(value) == int(value)


@pytest.mark.parametrize("value", ["-1", "11", "abc", ""])
def test_parse_depth_invalid(value):
    with pytest.raises(ValueError):
        _parse_depth(value)
