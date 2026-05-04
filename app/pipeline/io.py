from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, payload: Any) -> str:
    output_path = Path(path)
    ensure_directory(output_path.parent)

    # Apply incremental updates to gold layer to prevent accidental overwrites
    if "data/gold" in str(output_path).replace("\\", "/") and output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(payload, list) and isinstance(existing, list):
                def get_key(r: Any) -> Any:
                    if not isinstance(r, dict):
                        return None
                    for k in ("player_name", "slug", "player_slug", "id", "club", "external_id"):
                        if k in r and r[k] is not None:
                            return (k, str(r[k]).strip().lower())
                    return None
                existing_map = {}
                for row in existing:
                    k = get_key(row)
                    if k:
                        existing_map[k] = row
                    else:
                        existing_map[id(row)] = row
                for row in payload:
                    k = get_key(row)
                    if k:
                        existing_map[k] = row
                    else:
                        existing_map[id(row)] = row
                payload = list(existing_map.values())
            elif isinstance(payload, dict) and isinstance(existing, dict):
                payload = {**existing, **payload}
        except Exception:
            pass

    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(output_path)


def list_files(directory: str | Path, pattern: str) -> list[Path]:
    path = Path(directory)
    if not path.exists():
        return []
    return sorted(path.glob(pattern))
