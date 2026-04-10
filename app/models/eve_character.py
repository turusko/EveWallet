from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDTimestampMixin


class EveCharacter(UUIDTimestampMixin, Base):
    __tablename__ = "eve_characters"

    user_id: Mapped[str] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    character_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    character_name: Mapped[str] = mapped_column(String(255), nullable=False)
    character_owner_hash: Mapped[str | None] = mapped_column(String(255))
    scopes: Mapped[str] = mapped_column(Text, default="")
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    unlinked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="characters")
    token: Mapped["EveToken"] = relationship(back_populates="character", uselist=False, cascade="all,delete-orphan")
