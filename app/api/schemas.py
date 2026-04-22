from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str


class PlayerListItem(BaseModel):
    player_name: str
    preferred_name: str | None = None
    position: str | None = None
    current_club: str | None = None
    nationality: str | None = None
    date_of_birth: str | None = None
    features: dict[str, Any] | None = None
    kpi: dict[str, Any] | None = None
    valuation: dict[str, Any] | None = None


class PlayerListResponse(BaseModel):
    count: int
    items: list[PlayerListItem]


class PlayerStatRow(BaseModel):
    match_date: str | None = None
    club_name: str | None = None
    minutes: int | None = None
    goals: int = 0
    assists: int = 0
    shots: int = 0
    passes_completed: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    source: str | None = None


class PlayerStatsResponse(BaseModel):
    player_name: str
    count: int
    items: list[PlayerStatRow]


class SimilarPlayerRow(BaseModel):
    player_name: str
    position: str | None = None
    distance: float
    similarity_score: float


class CompareResponse(BaseModel):
    player_name: str
    position: str | None = None
    comparison_features: dict[str, Any] = Field(default_factory=dict)
    similar_players: list[SimilarPlayerRow]


class ValuationRow(BaseModel):
    player_name: str
    position: str | None = None
    current_club: str | None = None
    competition: str | None = None
    valuation_score: float
    valuation_tier: str
    components: dict[str, Any] = Field(default_factory=dict)
    inputs: dict[str, Any] = Field(default_factory=dict)
    model_version: str


class ValuationListResponse(BaseModel):
    count: int
    items: list[ValuationRow]
