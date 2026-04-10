from sqlalchemy import Boolean, ForeignKey, Integer, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class AssignmentRule(UUIDTimestampMixin, Base):
    __tablename__ = "assignment_rules"

    user_id: Mapped[str] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    bucket_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("project_buckets.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    stop_processing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    conditions_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
