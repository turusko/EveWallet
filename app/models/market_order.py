from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class MarketOrder(UUIDTimestampMixin, Base):
    __tablename__ = "market_orders"

    character_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("eve_characters.id"), nullable=False)
    order_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    type_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type_name: Mapped[str | None] = mapped_column(String(255))
    location_id: Mapped[int | None] = mapped_column(BigInteger)
    location_name: Mapped[str | None] = mapped_column(String(255))
    region_id: Mapped[int | None] = mapped_column(BigInteger)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    volume_total: Mapped[int] = mapped_column(Integer, nullable=False)
    volume_remain: Mapped[int] = mapped_column(Integer, nullable=False)
    min_volume: Mapped[int | None] = mapped_column(Integer)
    is_buy_order: Mapped[bool] = mapped_column(Boolean, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(50), default="open")
    is_history: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    state: Mapped[str | None] = mapped_column(String(50))
    volume_filled: Mapped[int | None] = mapped_column(Integer)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    escrow: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    broker_fee: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    sales_tax: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
