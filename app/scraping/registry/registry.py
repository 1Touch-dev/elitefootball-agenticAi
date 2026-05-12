from typing import Dict, Optional
from pydantic import BaseModel, Field

class TargetEntry(BaseModel):
    source: str
    external_id: str
    scrape_url: str
    last_scraped: Optional[float] = None
    active: bool = True

class SourceRegistry:
    """System of record tracking known retrieval endpoints preventing duplicate scraping overhead."""
    def __init__(self):
        self.store: Dict[str, TargetEntry] = {}

    def register_target(self, key: str, entry: TargetEntry):
        self.store[key] = entry

    def get_pending(self):
        return [t for t in self.store.values() if t.active]
