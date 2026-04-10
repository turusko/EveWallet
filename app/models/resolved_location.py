from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class ResolvedLocation(UUIDTimestampMixin, Base):
    __tablename__ = "resolved_locations"

    location_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    location_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resolved_name: Mapped[str] = mapped_column(String(255), nullable=False)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
