from __future__ import annotations
from typing import Optional
from uuid import UUID
from pydantic import Field
from app.schemas.base import CanonicalBaseSchema

class ProviderMapping(CanonicalBaseSchema):
    """Consolidated tracking object linking internal UUIDs to disparate commercial datasets."""
    internal_uuid: UUID
    transfermarkt_id: Optional[str] = None
    fbref_id: Optional[str] = None
    sofascore_id: Optional[str] = None
    wyscout_id: Optional[str] = None
    opta_id: Optional[str] = None
    statsbomb_id: Optional[str] = None
    local_club_id: Optional[str] = None
    
    alias_names: list[str] = Field(default_factory=list)
    confidence_score: float = 1.0
