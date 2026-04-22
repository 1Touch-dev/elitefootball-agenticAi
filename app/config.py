from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the bootstrap application."""

    app_name: str = "elitefootball-agenticAi"
    environment: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./elitefootball.db")
    idv_team_key: str = os.getenv("IDV_TEAM_KEY", "idv")
    scrape_delay_seconds: float = float(os.getenv("SCRAPE_DELAY_SECONDS", "2.0"))
    scrape_timeout_ms: int = int(os.getenv("SCRAPE_TIMEOUT_MS", "30000"))
    raw_data_dir: str = os.getenv("RAW_DATA_DIR", "data/raw/transfermarkt")
    parsed_data_dir: str = os.getenv("PARSED_DATA_DIR", "data/parsed/transfermarkt")
    fbref_raw_data_dir: str = os.getenv("FBREF_RAW_DATA_DIR", "data/raw/fbref")
    fbref_parsed_data_dir: str = os.getenv("FBREF_PARSED_DATA_DIR", "data/parsed/fbref")
    bronze_data_dir: str = os.getenv("BRONZE_DATA_DIR", "data/bronze")
    silver_data_dir: str = os.getenv("SILVER_DATA_DIR", "data/silver")
    gold_data_dir: str = os.getenv("GOLD_DATA_DIR", "data/gold")
    repo_root: str = os.getenv("REPO_ROOT", os.getcwd())
    safety_approval_ttl_seconds: int = int(os.getenv("SAFETY_APPROVAL_TTL_SECONDS", "900"))


settings = Settings()
