from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import logging
from pathlib import Path
import re
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.db import base as db_base
from app.db.models import Club, Match, Player, Stat
from app.pipeline.io import write_json
from app.services.logging_service import get_logger, log_event, log_exception


logger = get_logger(__name__)


@dataclass(frozen=True)
class PersistenceContext:
    run_id: str
    report_path: Path


def ensure_database_ready() -> None:
    """Ensure ORM metadata is present before ingestion occurs."""
    log_event(logger, logging.INFO, "db.schema.ensure.start", database_url=settings.database_url)
    db_base.Base.metadata.create_all(bind=db_base.engine)
    log_event(logger, logging.INFO, "db.schema.ensure.complete", database_url=settings.database_url)


def ingest_silver_tables(silver_tables: dict[str, list[dict[str, object]]]) -> dict[str, object]:
    ensure_database_ready()
    context = PersistenceContext(
        run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        report_path=Path(settings.bronze_data_dir) / "persistence_report.json",
    )
    report = _new_report(silver_tables, context)
    session = db_base.SessionLocal()
    log_event(logger, logging.INFO, "db.ingest.start", run_id=context.run_id)
    try:
        club_lookup = _upsert_clubs(session, silver_tables, report)
        player_lookup = _upsert_players(session, silver_tables.get("players", []), club_lookup, report)
        match_lookup = _upsert_matches(session, silver_tables.get("matches", []), club_lookup, report)
        _upsert_stats(
            session,
            silver_tables.get("player_match_stats", []),
            club_lookup=club_lookup,
            player_lookup=player_lookup,
            match_lookup=match_lookup,
            report=report,
        )
        session.commit()
        report["verification"] = verify_persistence(session)
        report["status"] = _finalize_status(report)
        report["report_path"] = write_json(context.report_path, report)
        log_event(
            logger,
            logging.INFO,
            "db.ingest.complete",
            run_id=context.run_id,
            status=report["status"],
            clubs=report["entities"]["clubs"],
            players=report["entities"]["players"],
            matches=report["entities"]["matches"],
            stats=report["entities"]["stats"],
        )
        return report
    except Exception as exc:
        session.rollback()
        report["status"] = "write_failed"
        report.setdefault("errors", []).append({"entity": "persistence", "error": type(exc).__name__, "message": str(exc)})
        report["report_path"] = write_json(context.report_path, report)
        log_exception(logger, "db.ingest.failed", exc, run_id=context.run_id, report_path=str(context.report_path))
        raise
    finally:
        session.close()


def verify_persistence(session: Session) -> dict[str, object]:
    counts = {
        "clubs": int(session.scalar(select(func.count()).select_from(Club)) or 0),
        "players": int(session.scalar(select(func.count()).select_from(Player)) or 0),
        "matches": int(session.scalar(select(func.count()).select_from(Match)) or 0),
        "stats": int(session.scalar(select(func.count()).select_from(Stat)) or 0),
    }
    sample_players = [
        {
            "id": player.id,
            "full_name": player.full_name,
            "club_id": player.club_id,
            "source": player.source,
        }
        for player in session.scalars(select(Player).order_by(Player.id).limit(5)).all()
    ]
    sample_matches = [
        {
            "id": match.id,
            "external_id": match.external_id,
            "match_date": match.match_date.isoformat() if match.match_date else None,
            "source": match.source,
        }
        for match in session.scalars(select(Match).order_by(Match.id).limit(5)).all()
    ]
    sample_stats = [
        {
            "id": stat.id,
            "match_id": stat.match_id,
            "player_id": stat.player_id,
            "club_id": stat.club_id,
            "goals": stat.goals,
            "source": stat.source,
        }
        for stat in session.scalars(select(Stat).order_by(Stat.id).limit(5)).all()
    ]
    result = {
        "query_ok": True,
        "counts": counts,
        "samples": {
            "players": sample_players,
            "matches": sample_matches,
            "stats": sample_stats,
        },
    }
    log_event(logger, logging.INFO, "db.verify.complete", counts=counts)
    return result


def _new_report(silver_tables: dict[str, list[dict[str, object]]], context: PersistenceContext) -> dict[str, object]:
    return {
        "run_id": context.run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "source_counts": {name: len(rows) for name, rows in silver_tables.items()},
        "entities": {
            "clubs": _empty_counts(),
            "players": _empty_counts(),
            "matches": _empty_counts(),
            "stats": _empty_counts(),
        },
        "errors": [],
        "verification": {},
    }


def _empty_counts() -> dict[str, int]:
    return {"attempted": 0, "inserted": 0, "updated": 0, "skipped": 0, "failed": 0}


def _normalize_name(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(str(value).split()).strip()
    return cleaned or None


def _normalize_code(value: str | None) -> str | None:
    if not value:
        return None
    compact = re.sub(r"[^A-Za-z0-9]+", "", value).upper()
    return compact or None


def _derive_short_code(name: str, used_codes: set[str]) -> str:
    tokens = [token for token in re.split(r"[^A-Za-z0-9]+", name.upper()) if token]
    base = "".join(token[0] for token in tokens[:4]) or _normalize_code(name) or "CLB"
    base = base[:8]
    candidate = base
    counter = 2
    while candidate in used_codes:
        suffix = str(counter)
        candidate = f"{base[: max(1, 8 - len(suffix))]}{suffix}"
        counter += 1
    used_codes.add(candidate)
    return candidate


def _parse_date(value: Any) -> date | None:
    normalized = _normalize_name(value)
    if not normalized:
        return None
    try:
        return datetime.fromisoformat(normalized.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _parse_datetime(value: Any) -> datetime | None:
    normalized = _normalize_name(value)
    if not normalized:
        return None
    try:
        parsed = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = datetime.strptime(normalized, "%Y-%m-%d")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _register_error(report: dict[str, object], entity: str, message: str, row: dict[str, object]) -> None:
    report["entities"][entity]["failed"] += 1
    report["errors"].append({"entity": entity, "message": message, "row": row})
    log_event(logger, logging.WARNING, "db.validation.failed", entity=entity, message=message)


def _upsert_clubs(session: Session, silver_tables: dict[str, list[dict[str, object]]], report: dict[str, object]) -> dict[str, Club]:
    counts = report["entities"]["clubs"]
    club_names: list[str] = []
    for row in silver_tables.get("players", []):
        name = _normalize_name(row.get("current_club"))
        if name:
            club_names.append(name)
    for row in silver_tables.get("matches", []):
        for key in ("home_club", "away_club"):
            name = _normalize_name(row.get(key))
            if name:
                club_names.append(name)
    for row in silver_tables.get("player_match_stats", []):
        name = _normalize_name(row.get("club_name"))
        if name:
            club_names.append(name)

    existing = {club.name: club for club in session.scalars(select(Club)).all()}
    used_codes = {club.short_code for club in existing.values()}
    for name in sorted(set(club_names)):
        counts["attempted"] += 1
        club = existing.get(name)
        if club is None:
            club = Club(name=name, short_code=_derive_short_code(name, used_codes), is_target=(name == "Independiente del Valle"))
            session.add(club)
            session.flush()
            existing[name] = club
            counts["inserted"] += 1
        else:
            counts["updated"] += 1
    log_event(logger, logging.INFO, "db.upsert.clubs.complete", counts=counts)
    return existing


def _upsert_players(session: Session, rows: list[dict[str, object]], club_lookup: dict[str, Club], report: dict[str, object]) -> dict[tuple[str, int, str], Player]:
    counts = report["entities"]["players"]
    existing_players = {
        (_normalize_name(player.full_name) or "", player.club_id, player.source): player
        for player in session.scalars(select(Player)).all()
    }
    for row in rows:
        counts["attempted"] += 1
        club_name = _normalize_name(row.get("current_club"))
        full_name = _normalize_name(row.get("player_name"))
        source = _normalize_name(row.get("source")) or "transfermarkt"
        if not club_name or club_name not in club_lookup:
            _register_error(report, "players", "club resolution failed", row)
            continue
        if not full_name:
            _register_error(report, "players", "player_name missing", row)
            continue
        key = (full_name, club_lookup[club_name].id, source)
        existing = existing_players.get(key)
        if existing is None:
            existing = Player(
                club_id=club_lookup[club_name].id,
                full_name=full_name,
                preferred_name=_normalize_name(row.get("preferred_name")),
                position=_normalize_name(row.get("position")) or "unknown",
                nationality=_normalize_name(row.get("nationality")),
                date_of_birth=_parse_date(row.get("date_of_birth")),
                source=source,
            )
            session.add(existing)
            session.flush()
            existing_players[key] = existing
            counts["inserted"] += 1
        else:
            existing.preferred_name = _normalize_name(row.get("preferred_name")) or existing.preferred_name
            existing.position = _normalize_name(row.get("position")) or existing.position
            existing.nationality = _normalize_name(row.get("nationality")) or existing.nationality
            existing.date_of_birth = _parse_date(row.get("date_of_birth")) or existing.date_of_birth
            counts["updated"] += 1
    log_event(logger, logging.INFO, "db.upsert.players.complete", counts=counts)
    return existing_players


def _match_lookup_key(row: dict[str, object], club_lookup: dict[str, Club]) -> tuple[object, ...] | None:
    external_id = _normalize_name(row.get("external_id"))
    if external_id:
        return ("external_id", external_id)
    match_date = _parse_datetime(row.get("match_date"))
    home_name = _normalize_name(row.get("home_club"))
    away_name = _normalize_name(row.get("away_club"))
    if not match_date or not home_name or not away_name:
        return None
    home_id = club_lookup.get(home_name).id if home_name in club_lookup else None
    away_id = club_lookup.get(away_name).id if away_name in club_lookup else None
    if home_id is None or away_id is None:
        return None
    return ("composite", match_date.isoformat(), home_id, away_id, _normalize_name(row.get("competition")) or "")


def _upsert_matches(session: Session, rows: list[dict[str, object]], club_lookup: dict[str, Club], report: dict[str, object]) -> dict[tuple[object, ...], Match]:
    counts = report["entities"]["matches"]
    existing_matches: dict[tuple[object, ...], Match] = {}
    for match in session.scalars(select(Match)).all():
        if match.external_id:
            existing_matches[("external_id", match.external_id)] = match
        existing_matches[("composite", match.match_date.isoformat(), match.home_club_id, match.away_club_id, match.competition or "")] = match

    for row in rows:
        counts["attempted"] += 1
        home_name = _normalize_name(row.get("home_club"))
        away_name = _normalize_name(row.get("away_club"))
        match_date = _parse_datetime(row.get("match_date"))
        if not home_name or home_name not in club_lookup:
            _register_error(report, "matches", "home club resolution failed", row)
            continue
        if not away_name or away_name not in club_lookup:
            _register_error(report, "matches", "away club resolution failed", row)
            continue
        if not match_date:
            _register_error(report, "matches", "match_date missing or invalid", row)
            continue
        key = _match_lookup_key(row, club_lookup)
        if key is None:
            _register_error(report, "matches", "match lookup key could not be derived", row)
            continue
        existing = existing_matches.get(key)
        if existing is None:
            existing = Match(
                external_id=_normalize_name(row.get("external_id")),
                competition=_normalize_name(row.get("competition")),
                season=_normalize_name(row.get("season")),
                match_date=match_date,
                home_club_id=club_lookup[home_name].id,
                away_club_id=club_lookup[away_name].id,
                home_score=row.get("home_score"),
                away_score=row.get("away_score"),
                venue=_normalize_name(row.get("venue")),
                source=_normalize_name(row.get("source")) or "fbref",
            )
            session.add(existing)
            session.flush()
            counts["inserted"] += 1
        else:
            existing.competition = _normalize_name(row.get("competition")) or existing.competition
            existing.season = _normalize_name(row.get("season")) or existing.season
            existing.home_score = row.get("home_score") if row.get("home_score") is not None else existing.home_score
            existing.away_score = row.get("away_score") if row.get("away_score") is not None else existing.away_score
            existing.venue = _normalize_name(row.get("venue")) or existing.venue
            counts["updated"] += 1
        existing_matches[("composite", existing.match_date.isoformat(), existing.home_club_id, existing.away_club_id, existing.competition or "")] = existing
        if existing.external_id:
            existing_matches[("external_id", existing.external_id)] = existing
    log_event(logger, logging.INFO, "db.upsert.matches.complete", counts=counts)
    return existing_matches


def _resolve_player_key(row: dict[str, object], club_lookup: dict[str, Club]) -> tuple[str, int, str] | None:
    full_name = _normalize_name(row.get("player_name"))
    club_name = _normalize_name(row.get("club_name"))
    source = _normalize_name(row.get("source")) or "transfermarkt"
    if not full_name or not club_name or club_name not in club_lookup:
        return None
    preferred = (full_name, club_lookup[club_name].id, source)
    if source != "transfermarkt":
        return preferred
    return preferred


def _upsert_stats(
    session: Session,
    rows: list[dict[str, object]],
    *,
    club_lookup: dict[str, Club],
    player_lookup: dict[tuple[str, int, str], Player],
    match_lookup: dict[tuple[object, ...], Match],
    report: dict[str, object],
) -> None:
    counts = report["entities"]["stats"]
    existing_stats = {(stat.match_id, stat.player_id): stat for stat in session.scalars(select(Stat)).all()}

    for row in rows:
        counts["attempted"] += 1
        club_name = _normalize_name(row.get("club_name"))
        player_name = _normalize_name(row.get("player_name"))
        if not club_name or club_name not in club_lookup:
            _register_error(report, "stats", "club resolution failed", row)
            continue
        if not player_name:
            _register_error(report, "stats", "player_name missing", row)
            continue

        club = club_lookup[club_name]
        player = player_lookup.get((player_name, club.id, "transfermarkt"))
        if player is None:
            player = player_lookup.get((player_name, club.id, "fbref"))
        if player is None:
            player = Player(club_id=club.id, full_name=player_name, position="unknown", source="fbref")
            session.add(player)
            session.flush()
            player_lookup[(player_name, club.id, "fbref")] = player
            report["entities"]["players"]["attempted"] += 1
            report["entities"]["players"]["inserted"] += 1

        match_row = {
            "external_id": row.get("match_external_id"),
            "match_date": row.get("match_date"),
            "home_club": row.get("home_club"),
            "away_club": row.get("away_club"),
            "competition": row.get("competition"),
        }
        match_key = None
        if _normalize_name(row.get("match_external_id")):
            match_key = ("external_id", _normalize_name(row.get("match_external_id")))
        else:
            match_date = _parse_datetime(row.get("match_date"))
            if match_date:
                for key, match in match_lookup.items():
                    if key[0] == "composite" and key[1] == match_date.isoformat() and club.id in {match.home_club_id, match.away_club_id}:
                        match_key = key
                        break
        if match_key is None or match_key not in match_lookup:
            _register_error(report, "stats", "match resolution failed", row)
            continue

        match = match_lookup[match_key]
        stat_key = (match.id, player.id)
        existing = existing_stats.get(stat_key)
        if existing is None:
            existing = Stat(
                match_id=match.id,
                player_id=player.id,
                club_id=club.id,
                minutes_played=row.get("minutes"),
                goals=row.get("goals") or 0,
                assists=row.get("assists") or 0,
                yellow_cards=row.get("yellow_cards") or 0,
                red_cards=row.get("red_cards") or 0,
                shots=row.get("shots") or 0,
                passes_completed=row.get("passes_completed") or 0,
                source=_normalize_name(row.get("source")) or "fbref",
            )
            session.add(existing)
            session.flush()
            existing_stats[stat_key] = existing
            counts["inserted"] += 1
        else:
            existing.club_id = club.id
            existing.minutes_played = row.get("minutes") if row.get("minutes") is not None else existing.minutes_played
            existing.goals = row.get("goals") if row.get("goals") is not None else existing.goals
            existing.assists = row.get("assists") if row.get("assists") is not None else existing.assists
            existing.yellow_cards = row.get("yellow_cards") if row.get("yellow_cards") is not None else existing.yellow_cards
            existing.red_cards = row.get("red_cards") if row.get("red_cards") is not None else existing.red_cards
            existing.shots = row.get("shots") if row.get("shots") is not None else existing.shots
            existing.passes_completed = row.get("passes_completed") if row.get("passes_completed") is not None else existing.passes_completed
            counts["updated"] += 1
    log_event(logger, logging.INFO, "db.upsert.stats.complete", counts=counts)


def _finalize_status(report: dict[str, object]) -> str:
    entities = report["entities"]
    failed = sum(entity["failed"] for entity in entities.values())
    updated = sum(entity["updated"] for entity in entities.values())
    inserted = sum(entity["inserted"] for entity in entities.values())
    if failed and not (inserted or updated):
        return "validation_failed"
    if failed:
        return "success_partial"
    return "success_complete"
