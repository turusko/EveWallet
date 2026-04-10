from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class InventoryLot(UUIDTimestampMixin, Base):
    __tablename__ = "inventory_lots"

    bucket_fk: Mapped[str | None] = mapped_column(Uuid, ForeignKey("project_buckets.id"))
    character_fk: Mapped[str | None] = mapped_column(Uuid, ForeignKey("eve_characters.id"))
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_uuid: Mapped[str | None] = mapped_column(Uuid)
    type_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type_name: Mapped[str | None] = mapped_column(String(255))
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    quantity_total: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    quantity_remaining: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    location_id: Mapped[int | None] = mapped_column(BigInteger)
    location_name: Mapped[str | None] = mapped_column(String(255))
