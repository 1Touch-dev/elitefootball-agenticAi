"""
APScheduler-based automation: daily IDV scrape, weekly all-tracked, monthly discovery.
Run this module directly to start the scheduler as a standalone process.
"""
from __future__ import annotations

import logging
import signal
import sys
from typing import Any

from app.services.logging_service import get_logger, log_event


logger = get_logger(__name__)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    _APSCHEDULER_AVAILABLE = True
except ImportError:
    BackgroundScheduler = None  # type: ignore[assignment,misc]
    CronTrigger = None          # type: ignore[assignment]
    _APSCHEDULER_AVAILABLE = False


# ── Job functions ──────────────────────────────────────────────────────────────

def _job_daily_idv() -> None:
    """Daily: re-scrape all IDV players at HIGH priority."""
    log_event(logger, logging.INFO, "scheduler.job.start", job="daily_idv")
    try:
        from app.orchestration.scrape_runner import run_full_scrape_cycle
        result = run_full_scrape_cycle(tiers=["idv"], trigger_pipeline=True)
        log_event(logger, logging.INFO, "scheduler.job.done",
                  job="daily_idv", **result)
    except Exception as exc:
        log_event(logger, logging.ERROR, "scheduler.job.failed",
                  job="daily_idv", error=str(exc)[:300])


def _job_weekly_tracked() -> None:
    """Weekly: scrape IDV + Liga Pro rivals."""
    log_event(logger, logging.INFO, "scheduler.job.start", job="weekly_tracked")
    try:
        from app.orchestration.scrape_runner import run_full_scrape_cycle
        result = run_full_scrape_cycle(tiers=["idv", "liga_pro"], trigger_pipeline=True)
        log_event(logger, logging.INFO, "scheduler.job.done",
                  job="weekly_tracked", **result)
    except Exception as exc:
        log_event(logger, logging.ERROR, "scheduler.job.failed",
                  job="weekly_tracked", error=str(exc)[:300])


def _job_monthly_discovery() -> None:
    """Monthly: full discovery crawl across all 150+ registered players."""
    log_event(logger, logging.INFO, "scheduler.job.start", job="monthly_discovery")
    try:
        from app.orchestration.scrape_runner import run_full_scrape_cycle
        result = run_full_scrape_cycle(
            tiers=["idv", "liga_pro", "discovery"], trigger_pipeline=True
        )
        log_event(logger, logging.INFO, "scheduler.job.done",
                  job="monthly_discovery", **result)
    except Exception as exc:
        log_event(logger, logging.ERROR, "scheduler.job.failed",
                  job="monthly_discovery", error=str(exc)[:300])


def _job_queue_cleanup() -> None:
    """Weekly: purge DONE/SKIPPED jobs to keep queue file lean."""
    log_event(logger, logging.INFO, "scheduler.job.start", job="queue_cleanup")
    try:
        from app.scraping.job_queue import PersistentJobQueue
        queue = PersistentJobQueue()
        removed = queue.clear_done()
        log_event(logger, logging.INFO, "scheduler.job.done",
                  job="queue_cleanup", removed=removed, remaining=queue.stats()["total"])
    except Exception as exc:
        log_event(logger, logging.ERROR, "scheduler.job.failed",
                  job="queue_cleanup", error=str(exc)[:200])


# ── Scheduler lifecycle ────────────────────────────────────────────────────────

_scheduler: Any = None


def build_scheduler() -> Any:
    """Construct and configure the APScheduler instance."""
    if not _APSCHEDULER_AVAILABLE:
        raise RuntimeError(
            "APScheduler is not installed. Run: pip install apscheduler"
        )

    sched = BackgroundScheduler(timezone="America/Guayaquil")  # IDV is in Ecuador (ECT = UTC-5)

    # Daily at 03:00 — IDV players only
    sched.add_job(
        _job_daily_idv,
        CronTrigger(hour=3, minute=0),
        id="daily_idv",
        name="Daily IDV scrape",
        replace_existing=True,
    )

    # Every Monday at 04:00 — IDV + Liga Pro
    sched.add_job(
        _job_weekly_tracked,
        CronTrigger(day_of_week="mon", hour=4, minute=0),
        id="weekly_tracked",
        name="Weekly tracked-player scrape",
        replace_existing=True,
    )

    # 1st of every month at 05:00 — full discovery
    sched.add_job(
        _job_monthly_discovery,
        CronTrigger(day=1, hour=5, minute=0),
        id="monthly_discovery",
        name="Monthly full discovery crawl",
        replace_existing=True,
    )

    # Every Sunday at 02:00 — queue maintenance
    sched.add_job(
        _job_queue_cleanup,
        CronTrigger(day_of_week="sun", hour=2, minute=0),
        id="queue_cleanup",
        name="Weekly job queue cleanup",
        replace_existing=True,
    )

    return sched


def start_scheduler() -> Any:
    global _scheduler
    if _scheduler and _scheduler.running:
        log_event(logger, logging.WARNING, "scheduler.already_running")
        return _scheduler
    _scheduler = build_scheduler()
    _scheduler.start()
    log_event(logger, logging.INFO, "scheduler.started",
              jobs=[j.id for j in _scheduler.get_jobs()])
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        log_event(logger, logging.INFO, "scheduler.stopped")
    _scheduler = None


def get_scheduler_status() -> dict[str, Any]:
    """Return current scheduler state for /admin/status."""
    if not _APSCHEDULER_AVAILABLE:
        return {"available": False, "running": False}
    if not _scheduler:
        return {"available": True, "running": False, "jobs": []}
    jobs = []
    for job in _scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(next_run) if next_run else None,
        })
    return {
        "available": True,
        "running": _scheduler.running,
        "jobs": jobs,
    }


# ── Standalone entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import time

    sched = start_scheduler()

    def _shutdown(sig, frame):
        log_event(logger, logging.INFO, "scheduler.signal_received", signal=sig)
        stop_scheduler()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    log_event(logger, logging.INFO, "scheduler.running", message="Press Ctrl+C to stop")
    while True:
        time.sleep(60)
