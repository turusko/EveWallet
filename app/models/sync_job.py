from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class SyncJob(UUIDTimestampMixin, Base):
    __tablename__ = "sync_jobs"

    user_id: Mapped[str] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    details_json: Mapped[dict | None] = mapped_column(JSONB)
