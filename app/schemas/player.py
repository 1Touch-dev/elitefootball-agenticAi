from __future__ import annotations
from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import Field, EmailStr
from app.schemas.base import CanonicalBaseSchema

class PlayerBio(CanonicalBaseSchema):
    """Definitive architectural state representation for a player entity."""
    player_uuid: UUID
    full_name: str
    preferred_name: Optional[str] = None
    
    date_of_birth: Optional[date] = None
    place_of_birth: Optional[str] = None
    nationalities: List[str] = Field(default_factory=list)
    
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    preferred_foot: Optional[str] = Field(None, pattern=r"^(right|left|both)$")
    
    primary_position: str
    secondary_positions: List[str] = Field(default_factory=list)
    
    current_club_uuid: Optional[UUID] = None
    contract_until: Optional[date] = None
    is_active: bool = True
