from __future__ import annotations
from typing import Optional
from uuid import UUID
from app.schemas.base import CanonicalBaseSchema

class Club(CanonicalBaseSchema):
    club_uuid: UUID
    official_name: str
    short_name: Optional[str] = None
    country: str
    city: Optional[str] = None
    stadium_name: Optional[str] = None
    is_target_club: bool = False
