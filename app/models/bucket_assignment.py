from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class BucketAssignment(UUIDTimestampMixin, Base):
    __tablename__ = "bucket_assignments"
    __table_args__ = (UniqueConstraint("source_type", "source_uuid", name="uq_assignment_source"),)

    bucket_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("project_buckets.id"), nullable=False)
    source_type: Mapped[str] = mapped_column(
        Enum("wallet_transaction", "wallet_journal", "market_order", name="source_type_enum", create_type=False), nullable=False
    )
    source_uuid: Mapped[str] = mapped_column(Uuid, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_by_user_id: Mapped[str] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    note: Mapped[str | None] = mapped_column(String(500))
    assignment_method: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    assignment_rule_id: Mapped[str | None] = mapped_column(Uuid, ForeignKey("assignment_rules.id"))
    locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
