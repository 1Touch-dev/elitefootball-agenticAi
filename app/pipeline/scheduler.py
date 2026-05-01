"""
Pipeline scheduler — daily scrape + pipeline rebuild via APScheduler.

Usage:
  from app.pipeline.scheduler import start_scheduler, stop_scheduler
  # or run standalone: python -m app.pipeline.scheduler
"""
from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.logging_service import get_logger, log_event

logger = get_logger(__name__)

_scheduler: BackgroundScheduler | None = None
_lock = threading.Lock()

# State for last run results
_last_run: dict[str, Any] = {}


def _run_daily_pipeline() -> None:
    """Full scrape + pipeline rebuild. Runs as scheduled job."""
    start = datetime.utcnow()
    log_event(logger, logging.INFO, "scheduler.daily_pipeline.start",
              ts=start.isoformat())
    try:
        from app.orchestration.scrape_runner import run_full_scrape_cycle
        result = run_full_scrape_cycle(
            force_refresh=False,
            trigger_pipeline=True,
            run_discovery=False,
        )
        _last_run.update({
            "status": "ok",
            "ts": start.isoformat(),
            "ok": result.get("ok", 0),
            "cached": result.get("cached", 0),
            "errors": result.get("errors", 0),
            "elapsed_seconds": result.get("elapsed_seconds"),
            "pipeline_triggered": result.get("pipeline_triggered"),
        })
        log_event(logger, logging.INFO, "scheduler.daily_pipeline.done", **_last_run)
    except Exception as exc:
        _last_run.update({
            "status": "error",
            "ts": start.isoformat(),
            "error": str(exc)[:300],
        })
        log_event(logger, logging.ERROR, "scheduler.daily_pipeline.failed",
                  error=str(exc)[:300])


def _run_discovery_weekly() -> None:
    """Weekly Tavily discovery to find new players."""
    log_event(logger, logging.INFO, "scheduler.discovery.start")
    try:
        from app.orchestration.scrape_runner import run_tavily_discovery_cycle
        result = run_tavily_discovery_cycle()
        log_event(logger, logging.INFO, "scheduler.discovery.done",
                  new_players=result.get("new_players", 0))
    except Exception as exc:
        log_event(logger, logging.ERROR, "scheduler.discovery.failed",
                  error=str(exc)[:300])


def start_scheduler(
    daily_hour: int = 3,
    daily_minute: int = 30,
    discovery_day: str = "sun",
) -> BackgroundScheduler:
    """
    Start background scheduler.
    Daily pipeline at 03:30 UTC; discovery sweep on Sundays at 02:00 UTC.
    """
    global _scheduler
    with _lock:
        if _scheduler is not None and _scheduler.running:
            return _scheduler

        sched = BackgroundScheduler(timezone="UTC")

        sched.add_job(
            _run_daily_pipeline,
            trigger=CronTrigger(hour=daily_hour, minute=daily_minute, timezone="UTC"),
            id="daily_pipeline",
            name="Daily scrape + pipeline rebuild",
            replace_existing=True,
            misfire_grace_time=3600,
        )

        sched.add_job(
            _run_discovery_weekly,
            trigger=CronTrigger(day_of_week=discovery_day, hour=2, minute=0, timezone="UTC"),
            id="weekly_discovery",
            name="Weekly Tavily player discovery",
            replace_existing=True,
            misfire_grace_time=7200,
        )

        sched.start()
        _scheduler = sched
        log_event(logger, logging.INFO, "scheduler.started",
                  daily_at=f"{daily_hour:02d}:{daily_minute:02d} UTC",
                  discovery_day=discovery_day)
        return sched


def stop_scheduler() -> None:
    global _scheduler
    with _lock:
        if _scheduler and _scheduler.running:
            _scheduler.shutdown(wait=False)
            _scheduler = None
            log_event(logger, logging.INFO, "scheduler.stopped")


def get_scheduler_status() -> dict[str, Any]:
    """Return scheduler state + last run info for health endpoint."""
    with _lock:
        running = _scheduler is not None and _scheduler.running
        jobs = []
        if running and _scheduler:
            for job in _scheduler.get_jobs():
                next_run = job.next_run_time
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run_utc": next_run.isoformat() if next_run else None,
                })
    return {
        "scheduler_running": running,
        "jobs": jobs,
        "last_run": dict(_last_run),
    }


def trigger_now(force_refresh: bool = False) -> dict[str, Any]:
    """Manually trigger pipeline rebuild immediately (for API/admin use)."""
    from app.orchestration.scrape_runner import run_full_scrape_cycle
    return run_full_scrape_cycle(
        force_refresh=force_refresh,
        trigger_pipeline=True,
        run_discovery=False,
    )


if __name__ == "__main__":
    import time
    print("Starting scheduler (Ctrl+C to stop)...")
    start_scheduler()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        stop_scheduler()
        print("Scheduler stopped.")
