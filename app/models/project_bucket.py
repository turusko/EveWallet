from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDTimestampMixin


class ProjectBucket(UUIDTimestampMixin, Base):
    __tablename__ = "project_buckets"

    user_id: Mapped[str] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="active")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bucket_type: Mapped[str | None] = mapped_column(String(64))
    accounting_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="fifo")
    default_location_id: Mapped[int | None] = mapped_column(BigInteger)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="buckets")
