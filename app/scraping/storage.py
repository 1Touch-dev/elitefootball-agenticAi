from __future__ import annotations

import json
from pathlib import Path
import re

from app.config import settings


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "unknown-player"


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_raw_html(slug: str, html: str, directory: str | Path = settings.raw_data_dir) -> str:
    output_dir = ensure_directory(directory)
    output_path = output_dir / f"{slug}.html"
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)


def save_parsed_payload(slug: str, payload: dict[str, object], directory: str | Path = settings.parsed_data_dir) -> str:
    output_dir = ensure_directory(directory)
    output_path = output_dir / f"{slug}.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(output_path)
