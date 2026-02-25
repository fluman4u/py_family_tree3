import logging
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Tuple

from flask import Flask, jsonify, render_template, request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.repository import CsvFamilyRepository
from src.service import FamilyTreeService
from src.visualize import visualize_family

MIN_DEPTH = 0
MAX_DEPTH = 10

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    if logging.getLogger().handlers:
        return
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def _bundle_root() -> Path:
    """Return project root in source mode or _MEIPASS in bundled mode."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def _runtime_static_dir() -> Path:
    """Writable static directory for generated graph HTML files."""
    static_dir = Path(tempfile.gettempdir()) / "py_family_tree3_static"
    static_dir.mkdir(parents=True, exist_ok=True)
    return static_dir


def _prepare_runtime_static_assets(bundle_root: Path, static_dir: Path) -> None:
    """Copy bundled static assets once so pyvis relative assets can be served."""
    bundled_static = bundle_root / "web" / "static"
    if not bundled_static.exists():
        return
    for child in bundled_static.iterdir():
        target = static_dir / child.name
        if target.exists():
            continue
        if child.is_dir():
            shutil.copytree(child, target)
        else:
            shutil.copy2(child, target)


def _parse_depth(value: str) -> int:
    try:
        depth = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("depth 必须是整数") from exc

    if not (MIN_DEPTH <= depth <= MAX_DEPTH):
        raise ValueError(f"depth 必须在 {MIN_DEPTH} 到 {MAX_DEPTH} 之间")
    return depth


def create_app() -> Tuple[Flask, FamilyTreeService, str]:
    _configure_logging()

    bundle_root = _bundle_root()
    template_dir = bundle_root / "web" / "templates"
    static_dir = _runtime_static_dir()
    _prepare_runtime_static_assets(bundle_root, static_dir)

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir),
        static_url_path="/static",
    )

    repo = CsvFamilyRepository(path=str(bundle_root / "data" / "family.csv"))
    service = FamilyTreeService.from_persons(repo.load_persons())

    lineage_path = str(bundle_root / "data" / "lineage.yaml")
    root_person = service.default_root()

    default_file = "family_default.html"
    default_path = os.path.join(static_dir, default_file)

    def ensure_default_graph() -> None:
        if os.path.exists(default_path):
            return
        subset = service.subtree(root_id=root_person.id, max_depth=2)
        visualize_family(subset, default_path, lineage_path=lineage_path)
        logger.info("Generated default family graph at %s", default_path)

    ensure_default_graph()

    @app.route("/", methods=["GET", "POST"])
    def index():
        error = None
        graph_file = default_file

        if request.method == "POST":
            root_wbs = request.form.get("root_wbs")
            depth_raw = request.form.get("depth", "2")
            try:
                depth = _parse_depth(depth_raw)
                subset = service.subtree(root_wbs=root_wbs, max_depth=depth)
                graph_file = f"family_{uuid.uuid4().hex}.html"
                output_path = os.path.join(static_dir, graph_file)
                visualize_family(subset, output_path, lineage_path=lineage_path)
                logger.info(
                    "Rendered subtree graph: root_wbs=%s depth=%s file=%s",
                    root_wbs,
                    depth,
                    graph_file,
                )
            except ValueError as exc:
                error = str(exc)
                logger.warning(
                    "Invalid web input: root_wbs=%s depth=%s err=%s",
                    root_wbs,
                    depth_raw,
                    exc,
                )
            except Exception as exc:  # monitoring hook
                error = "生成图谱时发生内部错误"
                graph_file = default_file
                logger.exception("Unexpected rendering failure: %s", exc)

        timeline = service.migration_timeline()
        return render_template(
            "index.html",
            persons=service.persons.values(),
            timeline=timeline,
            graph_file=graph_file,
            error=error,
            min_depth=MIN_DEPTH,
            max_depth=MAX_DEPTH,
        )

    @app.route("/api/tree", methods=["GET"])
    def tree_api():
        root_wbs = request.args.get("root_wbs")
        depth_raw = request.args.get("depth", "2")
        gen_min_raw = request.args.get("gen_min")
        gen_max_raw = request.args.get("gen_max")
        try:
            depth = _parse_depth(depth_raw)
            gen_min = int(gen_min_raw) if gen_min_raw else None
            gen_max = int(gen_max_raw) if gen_max_raw else None
            payload = service.subtree_payload(
                root_wbs=root_wbs or root_person.wbs,
                max_depth=depth,
                gen_min=gen_min,
                gen_max=gen_max,
            )
            return jsonify(payload)
        except ValueError as exc:
            logger.warning("/api/tree bad request: %s", exc)
            return jsonify({"error": str(exc)}), 400
        except Exception as exc:  # monitoring hook
            logger.exception("/api/tree unexpected error: %s", exc)
            return jsonify({"error": "internal server error"}), 500

    return app, service, default_path


app, _service, _default_path = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
