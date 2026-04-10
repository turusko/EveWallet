from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class InventoryMovement(UUIDTimestampMixin, Base):
    __tablename__ = "inventory_movements"

    lot_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("inventory_lots.id"), nullable=False)
    bucket_fk: Mapped[str | None] = mapped_column(Uuid, ForeignKey("project_buckets.id"))
    movement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    ref_source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    ref_source_uuid: Mapped[str | None] = mapped_column(Uuid)
    type_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    unit_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    total_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
