from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the bootstrap application."""

    app_name: str = "elitefootball-agenticAi"
    environment: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./elitefootball.db")
    idv_team_key: str = os.getenv("IDV_TEAM_KEY", "idv")


settings = Settings()
