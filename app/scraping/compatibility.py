from __future__ import annotations

from dataclasses import asdict, dataclass
import logging
import re
import time
from typing import Any

import requests

from app.services.logging_service import get_logger, log_event, log_exception


logger = get_logger(__name__)
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
DEFAULT_TIMEOUT_SECONDS = 20
CHALLENGE_MARKERS = (
    "just a moment",
    "challenges.cloudflare.com",
    "cf-mitigated",
    "captcha",
    "access denied",
)
TRANSFERMARKT_MARKERS = ("market value", "detailed squad", "transfermarkt")
FBREF_MARKERS = ("match logs", "stats", "fbref", "data-stat")


@dataclass(frozen=True)
class CompatibilityProbeResult:
    source: str
    url: str
    method: str
    status_code: int | None
    final_url: str | None
    content_type: str | None
    title: str | None
    html_length: int
    elapsed_ms: float
    challenge_detected: bool
    anti_bot_mitigation_required: bool
    selector_like_markers_found: int
    marker_hits: list[str]
    cookies_seen: list[str]
    headers_seen: dict[str, str]
    classification: str
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class StaticProbeError(RuntimeError):
    """Raised when static compatibility probing fails entirely."""


def _extract_title(html: str) -> str | None:
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return " ".join(match.group(1).split())


def _count_marker_hits(html: str, markers: tuple[str, ...]) -> tuple[int, list[str]]:
    normalized = html.lower()
    hits = [marker for marker in markers if marker.lower() in normalized]
    return len(hits), hits


def _select_markers_for_source(source: str) -> tuple[str, ...]:
    if source.lower() == "transfermarkt":
        return TRANSFERMARKT_MARKERS
    if source.lower() == "fbref":
        return FBREF_MARKERS
    return ()


def _classify_response(*, source: str, status_code: int | None, html: str, marker_hits: list[str], headers_seen: dict[str, str]) -> tuple[str, bool, bool, list[str]]:
    notes: list[str] = []
    normalized_html = html.lower()
    challenge_detected = status_code in {401, 403, 429} or any(marker in normalized_html for marker in CHALLENGE_MARKERS) or headers_seen.get("cf-mitigated", "").lower() == "challenge"
    if challenge_detected:
        notes.append("Challenge or access-protection markers detected in response.")
        return "challenge_page", True, True, notes + ["Anti-bot mitigation likely needed."]

    if status_code is None:
        notes.append("No HTTP status code was captured.")
        return "request_failed", False, True, notes

    if status_code >= 400:
        notes.append(f"HTTP error status observed: {status_code}.")
        return "http_error", False, True, notes

    if not html.strip():
        notes.append("Empty body returned from source.")
        return "empty_body", False, True, notes

    if marker_hits:
        notes.append("Source markers found directly in initial HTML.")
        return "ok_static_html", False, False, notes

    if source.lower() == "fbref" and "<!--" in html:
        notes.append("HTML contains comment-wrapped structures; parser comment stripping remains relevant.")
        return "static_html_comment_wrapped", False, False, notes

    notes.append("Initial HTML returned, but expected source markers were not found.")
    return "selector_missing", False, True, notes


def probe_static_request(
    source: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    session: requests.Session | None = None,
) -> CompatibilityProbeResult:
    request_headers = {"User-Agent": DEFAULT_USER_AGENT, **(headers or {})}
    runner = session or requests.Session()
    start = time.perf_counter()
    log_event(logger, logging.INFO, "compatibility.static_probe.start", source=source, url=url, timeout_seconds=timeout_seconds)

    try:
        response = runner.get(url, headers=request_headers, timeout=timeout_seconds, allow_redirects=True)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    except requests.RequestException as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        log_exception(logger, "compatibility.static_probe.failed", exc, source=source, url=url, timeout_seconds=timeout_seconds, elapsed_ms=elapsed_ms)
        raise StaticProbeError(f"Static probe failed for {source}: {url}") from exc

    html = response.text or ""
    title = _extract_title(html)
    markers = _select_markers_for_source(source)
    marker_count, marker_hits = _count_marker_hits(html, markers)
    headers_seen = {
        key.lower(): value
        for key, value in response.headers.items()
        if key.lower() in {"content-type", "server", "cf-mitigated", "set-cookie", "x-cache", "x-cache-status"}
    }
    classification, challenge_detected, javascript_likely_required, notes = _classify_response(
        source=source,
        status_code=response.status_code,
        html=html,
        marker_hits=marker_hits,
        headers_seen=headers_seen,
    )
    cookies_seen = sorted(response.cookies.keys())
    if response.headers.get("Set-Cookie") and "set-cookie" not in headers_seen:
        headers_seen["set-cookie"] = response.headers.get("Set-Cookie", "")

    result = CompatibilityProbeResult(
        source=source,
        url=url,
        method="static_http",
        status_code=response.status_code,
        final_url=str(response.url),
        content_type=response.headers.get("Content-Type"),
        title=title,
        html_length=len(html),
        elapsed_ms=elapsed_ms,
        challenge_detected=challenge_detected,
        anti_bot_mitigation_required=javascript_likely_required,
        selector_like_markers_found=marker_count,
        marker_hits=marker_hits,
        cookies_seen=cookies_seen,
        headers_seen=headers_seen,
        classification=classification,
        notes=notes,
    )
    log_event(
        logger,
        logging.INFO,
        "compatibility.static_probe.complete",
        source=source,
        url=url,
        status_code=result.status_code,
        classification=result.classification,
        challenge_detected=result.challenge_detected,
        marker_hits=result.marker_hits,
        elapsed_ms=result.elapsed_ms,
    )
    return result
