from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
import json
import re


class _TagStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get_data(self) -> str:
        return " ".join(part.strip() for part in self.parts if part.strip())


def strip_tags(value: str) -> str:
    parser = _TagStripper()
    parser.feed(value)
    return normalize_space(unescape(parser.get_data()))


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def extract_meta_content(html: str, attr_name: str, attr_value: str) -> str | None:
    pattern = rf'<meta[^>]+{attr_name}=["\']{re.escape(attr_value)}["\'][^>]+content=["\']([^"\']+)["\']'
    match = re.search(pattern, html, re.IGNORECASE)
    return normalize_space(unescape(match.group(1))) if match else None


def extract_title(html: str) -> str | None:
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return normalize_space(strip_tags(match.group(1))) if match else None


def extract_json_ld(html: str) -> dict[str, object]:
    match = re.search(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return {}

    raw_payload = match.group(1).strip()
    try:
        return json.loads(raw_payload)
    except json.JSONDecodeError:
        return {}


def extract_labeled_value(html: str, label: str) -> str | None:
    pattern = rf"{re.escape(label)}\s*</[^>]+>\s*<[^>]+>(.*?)</"
    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    if match:
        return normalize_space(strip_tags(match.group(1)))

    text_pattern = rf"{re.escape(label)}\s*:?\s*([^<\n]+)"
    text_match = re.search(text_pattern, strip_tags(html), re.IGNORECASE)
    return normalize_space(text_match.group(1)) if text_match else None


def parse_player_profile(html: str, source_url: str) -> dict[str, object]:
    json_ld = extract_json_ld(html)
    player_name = (
        json_ld.get("name")
        if isinstance(json_ld, dict)
        else None
    ) or extract_meta_content(html, "property", "og:title") or extract_title(html)

    profile = {
        "source": "transfermarkt",
        "source_url": source_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "player_name": player_name,
        "preferred_name": extract_labeled_value(html, "Name in home country"),
        "position": extract_labeled_value(html, "Position"),
        "date_of_birth": extract_labeled_value(html, "Date of birth"),
        "nationality": extract_labeled_value(html, "Citizenship"),
        "current_club": extract_labeled_value(html, "Current club"),
        "market_value": extract_labeled_value(html, "Market value"),
    }
    return profile


def parse_transfer_history(html: str, source_url: str) -> list[dict[str, object]]:
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.IGNORECASE | re.DOTALL)
    transfers: list[dict[str, object]] = []

    for row in rows:
        columns = [strip_tags(column) for column in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.IGNORECASE | re.DOTALL)]
        cleaned = [column for column in columns if column]
        if len(cleaned) < 4:
            continue
        if not any(token in " ".join(cleaned).lower() for token in ["season", "club", "loan", "transfer", "joined"]):
            continue

        transfers.append(
            {
                "season": cleaned[0] if len(cleaned) > 0 else None,
                "date": cleaned[1] if len(cleaned) > 1 else None,
                "from_club": cleaned[2] if len(cleaned) > 2 else None,
                "to_club": cleaned[3] if len(cleaned) > 3 else None,
                "market_value": cleaned[4] if len(cleaned) > 4 else None,
                "fee": cleaned[5] if len(cleaned) > 5 else None,
                "source_url": source_url,
            }
        )

    return transfers
