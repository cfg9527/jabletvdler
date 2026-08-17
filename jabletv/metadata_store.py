from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .scraper import VideoInfo

logger = logging.getLogger(__name__)

METADATA_VERSION = 1
DB_DIR_NAME = "jable_db"


def _db_path(output_dir: str | Path) -> Path:
    return Path(output_dir) / DB_DIR_NAME


def save_metadata(video: VideoInfo, output_dir: str | Path) -> Path:
    db_dir = _db_path(output_dir)
    db_dir.mkdir(parents=True, exist_ok=True)

    data: dict[str, Any] = {"_version": METADATA_VERSION}
    data.update(asdict(video))

    filepath = db_dir / f"{video.code}.json"
    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Metadata saved: %s", filepath)
    return filepath


def load_all_metadata(output_dir: str | Path) -> list[dict[str, Any]]:
    db_dir = _db_path(output_dir)
    if not db_dir.is_dir():
        return []

    entries: list[dict[str, Any]] = []
    for p in sorted(db_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            data.pop("_version", None)
            entries.append(data)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Skipping corrupt metadata file %s: %s", p, exc)
    return entries


def search_metadata(entries: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    if not query:
        return entries

    q = query.lower()

    def matches(entry: dict[str, Any]) -> bool:
        if q in entry.get("code", "").lower():
            return True
        if q in entry.get("title", "").lower():
            return True
        if q in entry.get("category", "").lower():
            return True
        for tag in entry.get("tags", []):
            if q in tag.lower():
                return True
        for actress in entry.get("actresses", []):
            if q in actress.lower():
                return True
        return False

    return [e for e in entries if matches(e)]
