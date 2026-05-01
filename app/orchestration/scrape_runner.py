"""
Scrape runner: orchestrates a full or targeted scrape cycle using the job queue,
Crawl4AI/Playwright engine, Bronze storage, and incremental pipeline trigger.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

from app.scraping.job_queue import (
    JobPriority,
    JobStatus,
    PersistentJobQueue,
    ScrapeJob,
    build_discovery_jobs,
    build_idv_jobs,
    build_liga_pro_jobs,
)
from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)

_BRONZE_RAW_DIR = Path("data/bronze/raw")
_CHANGE_HASH_DIR = Path("data/bronze/change_hashes")


def _html_hash(html: str) -> str:
    return hashlib.sha256(html.encode("utf-8", errors="replace")).hexdigest()[:16]


def _hash_path(job: ScrapeJob) -> Path:
    return _CHANGE_HASH_DIR / f"{job.job_id}.hash"


def _has_changed(job: ScrapeJob, html: str) -> bool:
    """Return True if content changed since last scrape (or never scraped before)."""
    path = _hash_path(job)
    new_hash = _html_hash(html)
    if path.exists():
        old_hash = path.read_text().strip()
        if old_hash == new_hash:
            return False
    return True


def _save_hash(job: ScrapeJob, html: str) -> None:
    _CHANGE_HASH_DIR.mkdir(parents=True, exist_ok=True)
    _hash_path(job).write_text(_html_hash(html))


def _store_bronze(job: ScrapeJob, html: str) -> Path:
    """Persist raw HTML to Bronze layer."""
    out_dir = _BRONZE_RAW_DIR / job.player_slug / job.source
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "page.html"
    out_path.write_text(html, encoding="utf-8", errors="replace")
    return out_path


def _fetch_html(job: ScrapeJob) -> str | None:
    """Try Crawl4AI first, fall back to Playwright."""
    try:
        from app.scraping.crawl4ai_engine import crawl_page
        result = crawl_page(job.url, slug=job.player_slug, source=job.source)
        if result and result.get("html"):
            return result["html"]
    except Exception as exc:
        log_event(logger, logging.DEBUG, "scrape_runner.crawl4ai_failed",
                  job_id=job.job_id, error=str(exc)[:120])

    # Playwright fallback
    try:
        from app.scraping.browser import BrowserConfig, fetch_page_html
        return fetch_page_html(job.url, BrowserConfig(), source=job.source, slug=job.player_slug)
    except Exception as exc:
        log_event(logger, logging.WARNING, "scrape_runner.playwright_failed",
                  job_id=job.job_id, error=str(exc)[:200])
        return None


def process_job(job: ScrapeJob, queue: PersistentJobQueue) -> bool:
    """
    Fetch, change-detect, store Bronze, and return True on success.
    Marks job done/failed in the queue.
    """
    log_event(logger, logging.INFO, "scrape_runner.job_start",
              job_id=job.job_id, slug=job.player_slug,
              source=job.source, attempt=job.attempt_count)

    html = _fetch_html(job)
    if not html:
        queue.mark_failed(job.job_id, "fetch returned empty", retry=True)
        return False

    changed = _has_changed(job, html)
    if not changed:
        log_event(logger, logging.INFO, "scrape_runner.unchanged",
                  job_id=job.job_id, slug=job.player_slug, source=job.source)
        queue.mark_done(job.job_id, {"html": html, "engine": "cached"})
        return True

    _store_bronze(job, html)
    _save_hash(job, html)
    queue.mark_done(job.job_id, {"html": html, "engine": "live"})
    log_event(logger, logging.INFO, "scrape_runner.job_done",
              job_id=job.job_id, slug=job.player_slug,
              source=job.source, html_len=len(html))
    return True


def run_scrape_batch(
    queue: PersistentJobQueue,
    batch_size: int = 10,
    trigger_pipeline: bool = True,
) -> dict[str, Any]:
    """
    Dequeue and process one batch of jobs.
    Optionally triggers incremental pipeline for successfully scraped players.
    """
    # Recover stuck jobs from previous crash
    recovered = queue.reset_in_progress()
    if recovered:
        log_event(logger, logging.INFO, "scrape_runner.recovered_stuck", count=recovered)

    jobs = queue.dequeue_batch(batch_size)
    if not jobs:
        log_event(logger, logging.INFO, "scrape_runner.no_pending_jobs")
        return {"processed": 0, "succeeded": 0, "failed": 0, "unchanged": 0}

    succeeded: list[str] = []
    failed: list[str] = []
    changed_slugs: list[str] = []

    for job in jobs:
        ok = process_job(job, queue)
        if ok:
            succeeded.append(job.job_id)
            # Only trigger pipeline rebuild for jobs where content actually changed
            hash_path = _hash_path(job)
            if hash_path.exists():
                changed_slugs.append(job.player_slug)
        else:
            failed.append(job.job_id)

    result: dict[str, Any] = {
        "processed": len(jobs),
        "succeeded": len(succeeded),
        "failed": len(failed),
        "changed_slugs": list(set(changed_slugs)),
    }

    if trigger_pipeline and changed_slugs:
        unique_slugs = list(set(changed_slugs))
        log_event(logger, logging.INFO, "scrape_runner.triggering_pipeline",
                  slugs=unique_slugs)
        try:
            from app.pipeline.run_pipeline import run_incremental_pipeline
            pipeline_result = run_incremental_pipeline(unique_slugs)
            result["pipeline"] = {
                "triggered": True,
                "slugs": unique_slugs,
                "silver_rows": {
                    k: len(v) for k, v in pipeline_result["silver"]["tables"].items()
                },
            }
        except Exception as exc:
            log_event(logger, logging.ERROR, "scrape_runner.pipeline_failed",
                      error=str(exc)[:300])
            result["pipeline"] = {"triggered": False, "error": str(exc)[:200]}

    log_event(logger, logging.INFO, "scrape_runner.batch_complete", **result)
    return result


def run_tavily_discovery_cycle(max_results_per_league: int = 15) -> dict[str, Any]:
    """
    Run Tavily discovery across all target leagues and return newly found player slugs.
    Results are merged into the ALL_PLAYER_URLS registry for subsequent scraping.
    """
    try:
        from app.discovery.tavily_discovery import discover_all_leagues
        league_results = discover_all_leagues()
        total_new = 0
        new_slugs: list[str] = []
        for league, players in league_results.items():
            for p in players:
                slug = p.get("slug", "")
                tm_id = p.get("tm_id", "")
                if slug and tm_id:
                    new_slugs.append(slug)
                    total_new += 1
            log_event(logger, logging.INFO, "scrape_runner.tavily_league",
                      league=league, found=len(players))
        log_event(logger, logging.INFO, "scrape_runner.tavily_done",
                  total_new=total_new, leagues=len(league_results))
        return {"leagues": len(league_results), "new_players": total_new, "slugs": new_slugs}
    except Exception as exc:
        log_event(logger, logging.ERROR, "scrape_runner.tavily_failed", error=str(exc)[:300])
        return {"leagues": 0, "new_players": 0, "slugs": [], "error": str(exc)[:200]}


def run_full_scrape_cycle(
    tiers: list[str] | None = None,
    batch_size: int = 20,
    force_refresh: bool = False,
    trigger_pipeline: bool = True,
    run_discovery: bool = False,
) -> dict[str, Any]:
    """
    Full scrape cycle using the TM HTTP scraper for all registered players.

    tiers: unused (kept for API compatibility) — always scrapes ALL_PLAYER_URLS.
    force_refresh: ignore 24h cache TTL and re-scrape everything.
    trigger_pipeline: rebuild Gold after scraping completes.
    run_discovery: if True, run Tavily discovery first to find new players.
    """
    discovery_result: dict[str, Any] = {}
    if run_discovery:
        discovery_result = run_tavily_discovery_cycle()
        log_event(logger, logging.INFO, "scrape_runner.discovery_complete",
                  **{k: v for k, v in discovery_result.items() if k != "slugs"})

    # Use the real TM HTTP scraper (Crawl4AI / Playwright unavailable on this server)
    from app.scraping.tm_http_scraper import scrape_all_players
    start = time.perf_counter()
    results = scrape_all_players(force_refresh=force_refresh)
    elapsed = round(time.perf_counter() - start, 1)

    ok = sum(1 for r in results if r.get("status") == "ok")
    cached = sum(1 for r in results if r.get("status") == "cached")
    errors = [r for r in results if r.get("status") == "error"]

    log_event(logger, logging.INFO, "scrape_runner.scrape_complete",
              ok=ok, cached=cached, errors=len(errors), elapsed=elapsed)

    pipeline_result: dict[str, Any] = {}
    if trigger_pipeline and (ok > 0):
        try:
            from app.pipeline.run_pipeline import run_pipeline
            pipeline_result = run_pipeline()
            log_event(logger, logging.INFO, "scrape_runner.pipeline_triggered", ok=ok)
        except Exception as exc:
            log_event(logger, logging.ERROR, "scrape_runner.pipeline_failed",
                      error=str(exc)[:300])
            pipeline_result = {"error": str(exc)[:200]}

    summary = {
        "tiers": list(tiers or ["all"]),
        "enqueued": len(results),
        "ok": ok,
        "cached": cached,
        "errors": len(errors),
        "elapsed_seconds": elapsed,
        "discovery": discovery_result,
        "pipeline_triggered": bool(pipeline_result),
    }
    log_event(logger, logging.INFO, "scrape_runner.cycle_complete", **{
        k: v for k, v in summary.items() if k != "discovery"
    })
    return summary

    # Legacy queue-based flow (unused — kept for reference)
    queue = PersistentJobQueue()
    active_tiers = set(tiers or ["idv", "liga_pro", "discovery"])

    enqueued = 0
    if "idv" in active_tiers:
        n = build_idv_jobs(queue, force_refresh=force_refresh)
        enqueued += n
        log_event(logger, logging.INFO, "scrape_runner.enqueued_idv", count=n)

    if "liga_pro" in active_tiers:
        n = build_liga_pro_jobs(queue, force_refresh=force_refresh)
        enqueued += n
        log_event(logger, logging.INFO, "scrape_runner.enqueued_liga_pro", count=n)

    if "discovery" in active_tiers:
        n = build_discovery_jobs(queue, force_refresh=force_refresh)
        enqueued += n
        log_event(logger, logging.INFO, "scrape_runner.enqueued_discovery", count=n)

    log_event(logger, logging.INFO, "scrape_runner.cycle_start",
              enqueued=enqueued, tiers=list(active_tiers),
              pending=queue.pending_count())

    all_results: list[dict[str, Any]] = []
    start = time.perf_counter()
    max_batches = 200  # safety cap

    for _ in range(max_batches):
        if queue.pending_count() == 0:
            break
        batch_result = run_scrape_batch(
            queue, batch_size=batch_size, trigger_pipeline=trigger_pipeline
        )
        all_results.append(batch_result)
        if batch_result["processed"] == 0:
            break

    elapsed = round(time.perf_counter() - start, 1)
    total_processed = sum(r["processed"] for r in all_results)
    total_succeeded = sum(r["succeeded"] for r in all_results)
    total_failed = sum(r["failed"] for r in all_results)

    summary = {
        "tiers": list(active_tiers),
        "enqueued": enqueued,
        "batches": len(all_results),
        "total_processed": total_processed,
        "total_succeeded": total_succeeded,
        "total_failed": total_failed,
        "elapsed_seconds": elapsed,
        "queue_stats": queue.stats(),
    }
    log_event(logger, logging.INFO, "scrape_runner.cycle_complete", **summary)
    return summary
