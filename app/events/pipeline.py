from typing import List
from uuid import UUID
from app.schemas.event import GameEvent
from app.storage import get_default_provider

class EventDataPipeline:
    """Formal channel managing microsecond resolution capture and partitioning of gameplay mechanics."""
    
    def __init__(self):
        self.storage = get_default_provider()

    def process_match_events(self, match_id: UUID, events: List[GameEvent]):
        """Coordinates batch write minimizing I/O amplification and applying standardized pitch partitioning."""
        # Partition directory hierarchy: silver/events/match_id=XYZ/data.parquet
        target_partition = f"silver/events/match_id={match_id}/part-000.json"
        
        dumpable = [evt.model_dump(mode='json') for evt in events]
        return self.storage.write_json(target_partition, dumpable)
