from __future__ import annotations

import logging
from urllib.parse import urlparse

from app.scraping.browser import BrowserConfig, fetch_page_html
from app.scraping.parsers import parse_player_profile, parse_transfer_history
from app.scraping.storage import save_parsed_payload, save_raw_html, slugify
from app.scraping.validation import validate_transfermarkt_payload
from app.services.logging_service import get_logger, log_event, log_exception


logger = get_logger(__name__)


def _slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return "transfermarkt-player"
    return slugify(path.split("/")[-1])


def scrape_transfermarkt_player(url: str, *, slug: str | None = None, headless: bool = True) -> dict[str, object]:
    runtime_slug = slug or _slug_from_url(url)
    context = {"source": "transfermarkt", "slug": runtime_slug, "url": url, "headless": headless}
    log_event(logger, logging.INFO, "scrape.start", **context)
    try:
        html = fetch_page_html(url, BrowserConfig(headless=headless), source="transfermarkt", slug=runtime_slug)
        raw_path = save_raw_html(runtime_slug, html)
        log_event(logger, logging.INFO, "scrape.raw_saved", raw_html_path=raw_path, html_length=len(html), **context)

        profile = parse_player_profile(html, url)
        transfers = parse_transfer_history(html, url)
        diagnostics = validate_transfermarkt_payload(profile, transfers)
        payload = {
            "profile": profile,
            "transfers": transfers,
            "diagnostics": diagnostics,
        }
        profile_fields = diagnostics["record_counts"]["profile_fields_present"]
        transfer_count = diagnostics["record_counts"]["transfer_rows"]
        log_event(
            logger,
            logging.INFO,
            "scrape.records_extracted",
            profile_fields=profile_fields,
            transfer_count=transfer_count,
            extraction_status=diagnostics["extraction_status"],
            missing_required_fields=diagnostics["missing_required_fields"],
            **context,
        )
        if diagnostics["extraction_status"] != "success_complete":
            log_event(
                logger,
                logging.WARNING,
                "scrape.empty_result",
                profile_fields=profile_fields,
                transfer_count=transfer_count,
                extraction_status=diagnostics["extraction_status"],
                missing_required_fields=diagnostics["missing_required_fields"],
                **context,
            )

        parsed_path = save_parsed_payload(runtime_slug, payload)
        log_event(logger, logging.INFO, "scrape.parsed_saved", parsed_data_path=parsed_path, **context)
        log_event(logger, logging.INFO, "scrape.success", parsed_data_path=parsed_path, raw_html_path=raw_path, extraction_status=diagnostics["extraction_status"], **context)

        return {
            "slug": runtime_slug,
            "raw_html_path": raw_path,
            "parsed_data_path": parsed_path,
            "payload": payload,
        }
    except Exception as exc:
        log_exception(logger, "scrape.failed", exc, stage="transfermarkt_pipeline", **context)
        raise
