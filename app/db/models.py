from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Club(Base):
    """Tracked football club for the MVP scope."""

    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    short_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_target: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    players: Mapped[list["Player"]] = relationship(back_populates="club")
    home_matches: Mapped[list["Match"]] = relationship(
        back_populates="home_club", foreign_keys="Match.home_club_id"
    )
    away_matches: Mapped[list["Match"]] = relationship(
        back_populates="away_club", foreign_keys="Match.away_club_id"
    )
    stats: Mapped[list["Stat"]] = relationship(back_populates="club")


class Player(Base):
    """Canonical player record for the MVP scope."""

    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    preferred_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position: Mapped[str] = mapped_column(String(120), default="unknown", nullable=False)
    shirt_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(120), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(String(255), default="unassigned", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    club: Mapped[Club] = relationship(back_populates="players")
    stats: Mapped[list["Stat"]] = relationship(back_populates="player")


class Match(Base):
    """Match metadata for tracked clubs."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    competition: Mapped[str | None] = mapped_column(String(255), nullable=True)
    season: Mapped[str | None] = mapped_column(String(64), nullable=True)
    match_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    home_club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), index=True, nullable=False)
    away_club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), index=True, nullable=False)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    venue: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(255), default="unassigned", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    home_club: Mapped[Club] = relationship(back_populates="home_matches", foreign_keys=[home_club_id])
    away_club: Mapped[Club] = relationship(back_populates="away_matches", foreign_keys=[away_club_id])
    stats: Mapped[list["Stat"]] = relationship(back_populates="match")


class Stat(Base):
    """Aggregated player stat line for a single match."""

    __tablename__ = "stats"
    __table_args__ = (UniqueConstraint("match_id", "player_id", name="uq_stats_match_player"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True, nullable=False)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True, nullable=False)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), index=True, nullable=False)
    minutes_played: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    assists: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    yellow_cards: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    red_cards: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shots: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passes_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source: Mapped[str] = mapped_column(String(255), default="unassigned", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    match: Mapped[Match] = relationship(back_populates="stats")
    player: Mapped[Player] = relationship(back_populates="stats")
    club: Mapped[Club] = relationship(back_populates="stats")
