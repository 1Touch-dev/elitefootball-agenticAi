"""
Persistent priority job queue for scraping operations.
Persists state to JSON so jobs survive process restarts.
Priority tiers: HIGH=1 (IDV), MEDIUM=5 (Liga Pro), LOW=10 (discovery).
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Any

from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)

_DEFAULT_QUEUE_PATH = Path("data/bronze/job_queue.json")
_CACHE_TTL_SECONDS = 86_400  # 24 hours


class JobPriority(IntEnum):
    HIGH = 1      # IDV squad — always fresh
    MEDIUM = 5    # Liga Pro rivals + tracked players
    LOW = 10      # Discovery crawl + external comparables


class JobStatus(str):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ScrapeJob:
    job_id: str
    player_slug: str
    source: str                    # "transfermarkt" | "fbref" | "sofascore"
    url: str
    priority: int                  # JobPriority value
    status: str = JobStatus.PENDING
    added_at: float = field(default_factory=time.time)
    last_attempted_at: float | None = None
    last_scraped_at: float | None = None
    attempt_count: int = 0
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def make_id(player_slug: str, source: str) -> str:
        return hashlib.md5(f"{player_slug}:{source}".encode()).hexdigest()[:12]

    def is_fresh(self, ttl: float = _CACHE_TTL_SECONDS) -> bool:
        if self.last_scraped_at is None:
            return False
        return (time.time() - self.last_scraped_at) < ttl

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PersistentJobQueue:
    """
    Priority-ordered queue with JSON persistence.
    Jobs are ordered by (priority ASC, added_at ASC).
    """

    def __init__(self, queue_path: Path = _DEFAULT_QUEUE_PATH) -> None:
        self._path = queue_path
        self._jobs: dict[str, ScrapeJob] = {}
        self._load()

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text())
            for item in raw:
                job = ScrapeJob(**item)
                self._jobs[job.job_id] = job
            log_event(logger, logging.INFO, "job_queue.loaded",
                      path=str(self._path), count=len(self._jobs))
        except Exception as exc:
            log_event(logger, logging.WARNING, "job_queue.load_failed",
                      path=str(self._path), error=str(exc))

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        try:
            payload = [job.to_dict() for job in self._jobs.values()]
            self._path.write_text(json.dumps(payload, indent=2, default=str))
        except Exception as exc:
            log_event(logger, logging.WARNING, "job_queue.save_failed",
                      path=str(self._path), error=str(exc))

    # ── Queue operations ──────────────────────────────────────────────────────

    def enqueue(
        self,
        player_slug: str,
        source: str,
        url: str,
        priority: JobPriority = JobPriority.MEDIUM,
        metadata: dict[str, Any] | None = None,
        force_refresh: bool = False,
    ) -> ScrapeJob:
        job_id = ScrapeJob.make_id(player_slug, source)
        existing = self._jobs.get(job_id)

        if existing and not force_refresh:
            if existing.is_fresh():
                log_event(logger, logging.DEBUG, "job_queue.skip_fresh",
                          job_id=job_id, slug=player_slug, source=source)
                return existing
            if existing.status == JobStatus.PENDING:
                return existing

        job = ScrapeJob(
            job_id=job_id,
            player_slug=player_slug,
            source=source,
            url=url,
            priority=int(priority),
            metadata=metadata or {},
        )
        self._jobs[job_id] = job
        self._save()
        log_event(logger, logging.DEBUG, "job_queue.enqueued",
                  job_id=job_id, slug=player_slug, source=source, priority=priority)
        return job

    def dequeue_batch(self, n: int = 10) -> list[ScrapeJob]:
        """Return up to n pending jobs ordered by priority then age."""
        pending = [j for j in self._jobs.values() if j.status == JobStatus.PENDING]
        pending.sort(key=lambda j: (j.priority, j.added_at))
        batch = pending[:n]
        for job in batch:
            job.status = JobStatus.IN_PROGRESS
            job.last_attempted_at = time.time()
            job.attempt_count += 1
        if batch:
            self._save()
        return batch

    def mark_done(self, job_id: str, result: dict[str, Any] | None = None) -> None:
        if job := self._jobs.get(job_id):
            job.status = JobStatus.DONE
            job.last_scraped_at = time.time()
            if result:
                job.metadata["last_result_summary"] = {
                    "html_len": len(result.get("html", "")),
                    "engine": result.get("engine"),
                }
            self._save()

    def mark_failed(self, job_id: str, error: str, retry: bool = True) -> None:
        if job := self._jobs.get(job_id):
            job.error = error
            if retry and job.attempt_count < 3:
                job.status = JobStatus.PENDING
                job.last_attempted_at = time.time()
            else:
                job.status = JobStatus.FAILED
            self._save()

    def mark_skipped(self, job_id: str, reason: str = "cached") -> None:
        if job := self._jobs.get(job_id):
            job.status = JobStatus.SKIPPED
            job.metadata["skip_reason"] = reason
            self._save()

    def reset_in_progress(self) -> int:
        """Reset any stuck IN_PROGRESS jobs back to PENDING (e.g. after crash)."""
        reset = 0
        for job in self._jobs.values():
            if job.status == JobStatus.IN_PROGRESS:
                age = time.time() - (job.last_attempted_at or job.added_at)
                if age > 300:  # stuck for 5+ minutes
                    job.status = JobStatus.PENDING
                    reset += 1
        if reset:
            self._save()
        return reset

    def stats(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for job in self._jobs.values():
            counts[job.status] = counts.get(job.status, 0) + 1
        return {
            "total": len(self._jobs),
            "by_status": counts,
            "by_priority": {
                "high": sum(1 for j in self._jobs.values() if j.priority == JobPriority.HIGH),
                "medium": sum(1 for j in self._jobs.values() if j.priority == JobPriority.MEDIUM),
                "low": sum(1 for j in self._jobs.values() if j.priority == JobPriority.LOW),
            },
        }

    def clear_done(self) -> int:
        before = len(self._jobs)
        self._jobs = {k: v for k, v in self._jobs.items()
                      if v.status not in (JobStatus.DONE, JobStatus.SKIPPED)}
        removed = before - len(self._jobs)
        if removed:
            self._save()
        return removed

    def pending_count(self) -> int:
        return sum(1 for j in self._jobs.values() if j.status == JobStatus.PENDING)

    def all_jobs(self) -> list[ScrapeJob]:
        return list(self._jobs.values())


def build_idv_jobs(queue: PersistentJobQueue, force_refresh: bool = False) -> int:
    """Enqueue all IDV players at HIGH priority."""
    from scripts.player_urls import IDV_PLAYER_URLS
    added = 0
    for slug, urls in IDV_PLAYER_URLS.items():
        if tm_url := urls.get("transfermarkt"):
            queue.enqueue(slug, "transfermarkt", tm_url,
                          JobPriority.HIGH, metadata=urls, force_refresh=force_refresh)
            added += 1
        if fb_url := urls.get("fbref"):
            queue.enqueue(slug, "fbref", fb_url,
                          JobPriority.HIGH, metadata=urls, force_refresh=force_refresh)
            added += 1
    return added


def build_liga_pro_jobs(queue: PersistentJobQueue, force_refresh: bool = False) -> int:
    """Enqueue Liga Pro rivals at MEDIUM priority."""
    from scripts.player_urls import LIGA_PRO_RIVAL_URLS
    added = 0
    for slug, urls in LIGA_PRO_RIVAL_URLS.items():
        if tm_url := urls.get("transfermarkt"):
            queue.enqueue(slug, "transfermarkt", tm_url,
                          JobPriority.MEDIUM, metadata=urls, force_refresh=force_refresh)
            added += 1
    return added


def build_discovery_jobs(queue: PersistentJobQueue, force_refresh: bool = False) -> int:
    """Enqueue all remaining players at LOW priority."""
    from scripts.player_urls import ALL_PLAYER_URLS, IDV_PLAYER_URLS, LIGA_PRO_RIVAL_URLS
    high_medium = set(IDV_PLAYER_URLS) | set(LIGA_PRO_RIVAL_URLS)
    added = 0
    for slug, urls in ALL_PLAYER_URLS.items():
        if slug in high_medium:
            continue
        if tm_url := urls.get("transfermarkt"):
            queue.enqueue(slug, "transfermarkt", tm_url,
                          JobPriority.LOW, metadata=urls, force_refresh=force_refresh)
            added += 1
    return added
