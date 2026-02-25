# Family Tree Visualization System

A Python-based family tree visualization project with CSV-driven data management, validation, web rendering, lineage annotation, and migration timeline analysis.

## Quick Start

```bash
pip install -r requirements.txt
python app.py          # CLI mode, outputs family.html
python web/app.py      # Web mode at http://127.0.0.1:5000
pytest -q              # Run regression tests
```

## Key Updates in Current Version

- Generator now uses monotonic ID allocation to avoid duplicate IDs.
- `build_tree` is idempotent and safe for repeated calls.
- CSV parser now validates unknown columns, WBS format, and integer fields more strictly.
- Web layer validates `depth` (`0~10`) and uses per-request graph file names to avoid overwrite conflicts.
- Added regression tests under `tests/`.

## Data Notes

- Required CSV columns: `id`, `wbs`, `name`.
- `parent_id` is optional and treated as a compatibility column; parent relation is inferred from `wbs`.
- Current sample dataset (`data/family.csv`) is expanded to 10 generations, with 3 sibling nodes in each generation from gen2 to gen10.

## License

MIT
