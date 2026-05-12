import pytest
import uuid
from app.schemas.base import ProviderSource
from app.core.identity.generator import IdentityCore
from app.storage import get_default_provider

def test_canonical_schema_importability():
    from app.schemas.player import PlayerBio
    # Verify instantiation succeeds safely
    p = PlayerBio(
        player_uuid=uuid.uuid4(),
        full_name="Test Validation",
        primary_position="FW"
    )
    assert p.full_name == "Test Validation"
    assert p.schema_version == "1.0.0"

def test_deterministic_id_generation():
    uid1 = IdentityCore.generate_player_uuid("12345", ProviderSource.FBREF)
    uid2 = IdentityCore.generate_player_uuid("12345", ProviderSource.FBREF)
    assert uid1 == uid2
    
    uid3 = IdentityCore.generate_player_uuid("12345", ProviderSource.OPTA)
    assert uid1 != uid3

def test_storage_provider_resolves():
    prov = get_default_provider()
    assert prov is not None
    assert hasattr(prov, "read_json")
