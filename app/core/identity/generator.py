import uuid
import hashlib
from typing import Optional
from app.schemas.provider import ProviderSource

class IdentityCore:
    """Produces consistent distributed ID generations securing structural integration."""
    
    # RFC 4122 namespaces for predictable offline generations
    PLAYER_NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")
    CLUB_NS = uuid.UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")
    MATCH_NS = uuid.UUID("6ba7b812-9dad-11d1-80b4-00c04fd430c8")

    @staticmethod
    def generate_deterministic_uuid(namespace: uuid.UUID, external_id: str, source: ProviderSource) -> uuid.UUID:
        """Creates stable v5 UUID unique to source+external_id combo allowing distributed ingestion."""
        seed = f"{source.value}:{str(external_id).strip()}"
        return uuid.uuid5(namespace, seed)

    @classmethod
    def generate_player_uuid(cls, external_id: str, source: ProviderSource) -> uuid.UUID:
        return cls.generate_deterministic_uuid(cls.PLAYER_NS, external_id, source)

    @classmethod
    def generate_club_uuid(cls, external_id: str, source: ProviderSource) -> uuid.UUID:
        return cls.generate_deterministic_uuid(cls.CLUB_NS, external_id, source)
