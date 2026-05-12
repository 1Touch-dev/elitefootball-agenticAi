from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class ProviderSource(str, Enum):
    TRANSFERMARKT = "transfermarkt"
    FBREF = "fbref"
    SOFASCORE = "sofascore"
    WYSCOUT = "wyscout"
    OPTA = "opta"
    STATSBOMB = "statsbomb"
    CLUB_INTERNAL = "club_internal"
    UNKNOWN = "unknown"

class CanonicalBaseSchema(BaseModel):
    """Base configuration for all canonical football data schemas."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    schema_version: str = Field(default="1.0.0", description="Semantic schema version tracking")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    source_system: ProviderSource = Field(default=ProviderSource.UNKNOWN)
    external_source_id: Optional[str] = Field(None, description="Original unique ID from source provider")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary container for nested provider specific blobs")
