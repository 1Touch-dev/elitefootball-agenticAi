from __future__ import annotations
from datetime import timedelta
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.base import CanonicalBaseSchema

class EventCoordinates(BaseModel):
    """Universal X/Y pitch location Normalized to 0-100 scales."""
    x: float = Field(..., ge=0.0, le=100.0)
    y: float = Field(..., ge=0.0, le=100.0)

class EventType(str, Enum):
    PASS = "pass"
    SHOT = "shot"
    CARRY = "carry"
    INTERCEPTION = "interception"
    TACKLE = "tackle"
    CLEARANCE = "clearance"
    PRESSURE = "pressure"
    DRIBBLE = "dribble"
    FOUL = "foul"
    SUBSTITUTION = "substitution"
    CARD = "card"
    OTHER = "other"

class GameEvent(CanonicalBaseSchema):
    """Ultra-granular structural definition for atomized gameplay interactions."""
    event_uuid: UUID
    match_uuid: UUID
    
    period: int = Field(1, description="1st half=1, 2nd half=2, ET1=3, ET2=4")
    timestamp: timedelta = Field(..., description="Elapsed time since period start")
    minute: int
    second: int
    
    event_type: EventType
    
    acting_player_uuid: Optional[UUID] = None
    receiving_player_uuid: Optional[UUID] = None
    
    club_uuid: Optional[UUID] = None
    
    possession_chain_id: Optional[int] = None
    
    start_location: Optional[EventCoordinates] = None
    end_location: Optional[EventCoordinates] = None
    
    is_successful: Optional[bool] = None
    
    raw_qualifiers: Dict[str, Any] = Field(default_factory=dict, description="Provider specific binary qualifiers (e.g. 'through ball')")
