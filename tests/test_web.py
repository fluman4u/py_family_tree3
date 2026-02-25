import pytest

from web.app import _parse_depth, create_app


@pytest.mark.parametrize("value", ["0", "2", "10"])
def test_parse_depth_valid(value):
    assert _parse_depth(value) == int(value)


@pytest.mark.parametrize("value", ["-1", "11", "abc", ""])
def test_parse_depth_invalid(value):
    with pytest.raises(ValueError):
        _parse_depth(value)


def test_tree_api_returns_payload():
    app, _, _ = create_app()
    client = app.test_client()

    resp = client.get("/api/tree?root_wbs=1.3&depth=2")

    assert resp.status_code == 200
    data = resp.get_json()
    assert "nodes" in data
    assert "edges" in data


def test_form_state_is_preserved_after_submit():
    app, _, _ = create_app()
    client = app.test_client()

    resp = client.post("/", data={"root_wbs": "1.3", "depth": "4"})

    html = resp.data.decode("utf-8")
    assert resp.status_code == 200
    assert 'value="1.3" selected' in html
    assert 'name="depth" value="4"' in html
