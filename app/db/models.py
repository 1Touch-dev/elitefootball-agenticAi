from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerProfile(Base):
    """Starter player profile model for the MVP scope."""

    __tablename__ = "player_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_name: Mapped[str] = mapped_column(String(255), index=True)
    position: Mapped[str] = mapped_column(String(120), default="unknown")
    source: Mapped[str] = mapped_column(String(255), default="unassigned")
