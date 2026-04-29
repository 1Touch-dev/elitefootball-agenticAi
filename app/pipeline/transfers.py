"""
Transfer data layer: processes raw transfer records into Silver + Gold artifacts.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from app.config import settings
from app.pipeline.io import write_json


def _normalize(v: str | None) -> str:
    return str(v or "").strip().lower()


def _parse_fee(raw: Any) -> float | None:
    """Parse fee strings like '€5.2m', '500k', '12000000' to float EUR."""
    if raw is None:
        return None
    s = str(raw).strip().lower().replace(",", "").replace("€", "").replace("£", "").replace("$", "")
    try:
        if "m" in s:
            return float(s.replace("m", "")) * 1_000_000
        if "k" in s:
            return float(s.replace("k", "")) * 1_000
        return float(s)
    except (ValueError, TypeError):
        return None


def build_silver_transfers(raw_transfers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize raw transfer records into Silver schema."""
    silver_rows: list[dict[str, Any]] = []
    for raw in raw_transfers:
        fee = _parse_fee(raw.get("fee") or raw.get("transfer_fee"))
        silver_rows.append({
            "player_name": str(raw.get("player_name") or "").strip(),
            "from_club": str(raw.get("from_club") or raw.get("from") or "").strip(),
            "to_club": str(raw.get("to_club") or raw.get("to") or "").strip(),
            "fee_eur": fee,
            "season": str(raw.get("season") or "").strip(),
            "transfer_type": str(raw.get("transfer_type") or raw.get("type") or "transfer").strip(),
            "loan": bool(raw.get("loan") or "loan" in _normalize(raw.get("transfer_type") or "")),
            "source": str(raw.get("source") or "transfermarkt").strip(),
        })
    return silver_rows


def build_gold_transfer_features(
    silver_transfers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Aggregate transfer records per player into Gold features:
    - total_transfers, total_fee_eur, avg_fee_eur
    - resale_multiplier (last exit fee / last entry fee)
    - club_history list
    """
    by_player: dict[str, list[dict]] = defaultdict(list)
    for row in silver_transfers:
        k = _normalize(row.get("player_name"))
        if k:
            by_player[k].append(row)

    output_rows: list[dict[str, Any]] = []
    for player_key, transfers in by_player.items():
        non_loan = [t for t in transfers if not t.get("loan")]
        fees = [t["fee_eur"] for t in non_loan if t.get("fee_eur") is not None]
        total_fee = sum(fees) if fees else None
        avg_fee = total_fee / len(fees) if fees else None

        # Resale: compare last known entry (to_club→from=old) vs exit
        entry_fee = fees[0] if fees else None
        exit_fee = fees[-1] if len(fees) > 1 else None
        resale_mult = round(exit_fee / entry_fee, 2) if entry_fee and exit_fee and entry_fee > 0 else None

        club_history = []
        for t in sorted(transfers, key=lambda x: x.get("season") or ""):
            club_history.append({
                "from": t.get("from_club"),
                "to": t.get("to_club"),
                "season": t.get("season"),
                "fee_eur": t.get("fee_eur"),
                "loan": t.get("loan"),
            })

        display_name = (transfers[0].get("player_name") or player_key)

        output_rows.append({
            "player_name": display_name,
            "total_transfers": len(transfers),
            "total_fee_eur": round(total_fee, 0) if total_fee is not None else None,
            "avg_fee_eur": round(avg_fee, 0) if avg_fee is not None else None,
            "resale_multiplier": resale_mult,
            "club_history": club_history,
        })

    return output_rows


def run_transfer_pipeline(
    raw_transfers: list[dict[str, Any]] | None = None,
    silver_path: Path | None = None,
    gold_path: Path | None = None,
) -> dict[str, Any]:
    """End-to-end: raw → silver → gold transfer artifacts."""
    raw = raw_transfers or []

    silver_rows = build_silver_transfers(raw)
    gold_rows = build_gold_transfer_features(silver_rows)

    silver_out = silver_path or Path(settings.silver_data_dir) / "transfers.json"
    gold_out = gold_path or Path(settings.gold_data_dir) / "transfer_features.json"

    write_json(silver_out, silver_rows)
    write_json(gold_out, gold_rows)

    return {
        "silver_path": str(silver_out),
        "gold_path": str(gold_out),
        "silver_rows": len(silver_rows),
        "gold_rows": len(gold_rows),
    }
