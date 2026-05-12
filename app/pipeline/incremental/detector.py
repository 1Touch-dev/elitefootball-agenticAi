import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any

class ChangeDetector:
    """Engine logic monitoring filesystem mutation vectors allowing incremental processing."""
    
    @staticmethod
    def compute_hash(data: Any) -> str:
        """Generates immutable checksum of logical payload for drift validation."""
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def has_changed(new_data: Any, previous_hash: Optional[str]) -> bool:
        if not previous_hash:
            return True
        return ChangeDetector.compute_hash(new_data) != previous_hash
