from flask import Flask, render_template, request
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import read_family_csv
from src.validate import validate_family
from src.tree import build_tree
from src.filter import filter_subtree
from src.visualize import visualize_family
from src.migration import build_migration_timeline

app = Flask(__name__)

persons = read_family_csv("data/family.csv")
validate_family(persons)
build_tree(persons)

# 初始化时生成默认族谱图
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "family.html")
root_person = next(p for p in persons.values() if p.parent_id is None)
subset = filter_subtree(persons, root_id=root_person.id, max_depth=2)
visualize_family(subset, static_path)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        root_wbs = request.form.get("root_wbs")
        depth = int(request.form.get("depth", 2))
        subset = filter_subtree(
            persons,
            root_wbs=root_wbs,
            max_depth=depth
        )
        visualize_family(subset, static_path)

    timeline = build_migration_timeline(persons)
    return render_template(
        "index.html",
        persons=persons.values(),
        timeline=timeline
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
