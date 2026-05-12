from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import Field
from app.schemas.base import CanonicalBaseSchema

class Match(CanonicalBaseSchema):
    match_uuid: UUID
    competition_uuid: UUID
    season_uuid: UUID
    
    match_date: datetime
    
    home_club_uuid: UUID
    away_club_uuid: UUID
    
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    
    venue_name: Optional[str] = None
    attendance: Optional[int] = None
    
    status: str = Field(default="scheduled", description="scheduled, live, finished, cancelled")
