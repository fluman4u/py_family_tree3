import os
import sys
import uuid
from typing import Dict, Tuple

from flask import Flask, render_template, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.filter import filter_subtree
from src.migration import build_migration_timeline
from src.parser import read_family_csv
from src.tree import build_tree
from src.validate import validate_family
from src.visualize import visualize_family

MIN_DEPTH = 0
MAX_DEPTH = 10


def _parse_depth(value: str) -> int:
    try:
        depth = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("depth 必须是整数") from exc

    if not (MIN_DEPTH <= depth <= MAX_DEPTH):
        raise ValueError(f"depth 必须在 {MIN_DEPTH} 到 {MAX_DEPTH} 之间")
    return depth


def create_app() -> Tuple[Flask, Dict[int, object], str]:
    app = Flask(__name__)

    persons = read_family_csv("data/family.csv")
    validate_family(persons)
    build_tree(persons)

    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    os.makedirs(static_dir, exist_ok=True)

    root_person = next((p for p in persons.values() if p.parent_id is None), None)
    if root_person is None:
        raise RuntimeError("No root person found in data")

    default_file = "family_default.html"
    default_path = os.path.join(static_dir, default_file)

    @app.route("/", methods=["GET", "POST"])
    def index():
        error = None
        graph_file = default_file

        if request.method == "GET" and not os.path.exists(default_path):
            subset = filter_subtree(persons, root_id=root_person.id, max_depth=2)
            visualize_family(subset, default_path)

        if request.method == "POST":
            root_wbs = request.form.get("root_wbs")
            depth_raw = request.form.get("depth", "2")
            try:
                depth = _parse_depth(depth_raw)
                subset = filter_subtree(persons, root_wbs=root_wbs, max_depth=depth)
                graph_file = f"family_{uuid.uuid4().hex}.html"
                output_path = os.path.join(static_dir, graph_file)
                visualize_family(subset, output_path)
            except ValueError as exc:
                error = str(exc)

        timeline = build_migration_timeline(persons)
        return render_template(
            "index.html",
            persons=persons.values(),
            timeline=timeline,
            graph_file=graph_file,
            error=error,
            min_depth=MIN_DEPTH,
            max_depth=MAX_DEPTH,
        )

    return app, persons, default_path


app, _persons, _default_path = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
