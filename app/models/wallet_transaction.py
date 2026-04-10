from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class WalletTransaction(UUIDTimestampMixin, Base):
    __tablename__ = "wallet_transactions"
    __table_args__ = (Index("ix_wallet_transactions_date", "date"),)

    character_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("eve_characters.id"), nullable=False)
    transaction_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    type_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type_name: Mapped[str | None] = mapped_column(String(255))
    location_id: Mapped[int | None] = mapped_column(BigInteger)
    location_name: Mapped[str | None] = mapped_column(String(255))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    is_buy: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_personal: Mapped[bool] = mapped_column(Boolean, default=True)
    client_id: Mapped[int | None] = mapped_column(BigInteger)
    client_name: Mapped[str | None] = mapped_column(String(255))
