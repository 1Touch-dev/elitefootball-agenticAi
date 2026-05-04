"""
Queue-based scraping architecture: priority scheduling, incremental updates, caching.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Any, Callable


class ScrapePriority(IntEnum):
    HIGH = 1
    MEDIUM = 5
    LOW = 10


@dataclass(order=True)
class ScrapeJob:
    priority: int
    player_slug: str = field(compare=False)
    source: str = field(compare=False)
    url: str = field(compare=False)
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)
    added_at: float = field(default_factory=time.time, compare=False)


@dataclass
class ScrapeCache:
    cache_dir: Path

    def _key(self, source: str, slug: str) -> str:
        return hashlib.md5(f"{source}:{slug}".encode()).hexdigest()

    def has(self, source: str, slug: str, max_age_seconds: float = 3600 * 24) -> bool:
        p = self.cache_dir / f"{self._key(source, slug)}.json"
        if not p.exists():
            return False
        age = time.time() - p.stat().st_mtime
        return age < max_age_seconds

    def get(self, source: str, slug: str) -> dict[str, Any] | None:
        p = self.cache_dir / f"{self._key(source, slug)}.json"
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                return None
        return None

    def set(self, source: str, slug: str, data: dict[str, Any]) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        p = self.cache_dir / f"{self._key(source, slug)}.json"
        p.write_text(json.dumps(data, default=str))


class ScrapeQueue:
    """Priority queue for scrape jobs with incremental update support."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self._jobs: list[ScrapeJob] = []
        self.cache = ScrapeCache(cache_dir or Path("data/cache/scrape"))

    def enqueue(
        self,
        player_slug: str,
        source: str,
        url: str,
        priority: ScrapePriority = ScrapePriority.MEDIUM,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        job = ScrapeJob(
            priority=int(priority),
            player_slug=player_slug,
            source=source,
            url=url,
            metadata=metadata or {},
        )
        self._jobs.append(job)
        self._jobs.sort()

    def dequeue(self) -> ScrapeJob | None:
        if not self._jobs:
            return None
        return self._jobs.pop(0)

    def skip_if_cached(
        self,
        player_slug: str,
        source: str,
        max_age_seconds: float = 3600 * 24,
    ) -> bool:
        return self.cache.has(source, player_slug, max_age_seconds)

    def size(self) -> int:
        return len(self._jobs)

    def clear(self) -> None:
        self._jobs.clear()

    def enqueue_players(
        self,
        players: list[dict[str, Any]],
        source: str,
        url_fn: Callable[[str], str],
        priority: ScrapePriority = ScrapePriority.MEDIUM,
        skip_cached: bool = True,
        max_age_seconds: float = 3600 * 24,
    ) -> int:
        added = 0
        for player in players:
            slug = str(player.get("slug") or player.get("player_name") or "").strip().lower().replace(" ", "-")
            if not slug:
                continue
            if skip_cached and self.skip_if_cached(slug, source, max_age_seconds):
                continue
            self.enqueue(slug, source, url_fn(slug), priority, metadata={"player": player})
            added += 1
        return added

    def run(
        self,
        scrape_fn: Callable[[ScrapeJob], dict[str, Any] | None],
        on_result: Callable[[ScrapeJob, dict[str, Any]], None] | None = None,
        max_jobs: int | None = None,
    ) -> dict[str, Any]:
        processed = 0
        succeeded = 0
        failed = 0
        results: list[dict[str, Any]] = []

        SOURCE_CONFIG = {
            "transfermarkt": {"delay": 2.0},
            "fbref": {"delay": 5.0},
            "sofascore": {"delay": 1.0},
            "fbref_archive": {"delay": 2.0},
        }

        while self._jobs:
            if max_jobs is not None and processed >= max_jobs:
                break
            job = self.dequeue()
            if job is None:
                break

            # Sleep according to source delay
            cfg = SOURCE_CONFIG.get(job.source, {"delay": 1.0})
            time.sleep(cfg.get("delay", 1.0))

            try:
                result = None
                for attempt in range(3):
                    try:
                        result = scrape_fn(job)
                        if result:
                            break
                    except Exception:
                        if attempt == 2:
                            raise
                        time.sleep(2 ** attempt)
                if result:
                    self.cache.set(job.source, job.player_slug, result)
                    if on_result:
                        on_result(job, result)
                    results.append(result)
                    succeeded += 1
                else:
                    failed += 1
            except Exception as exc:
                failed += 1
                results.append({"error": str(exc), "slug": job.player_slug})
            processed += 1

        return {
            "processed": processed,
            "succeeded": succeeded,
            "failed": failed,
            "results": results,
        }
