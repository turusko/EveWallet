from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class Contract(UUIDTimestampMixin, Base):
    __tablename__ = "contracts"

    character_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("eve_characters.id"), nullable=False)
    contract_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    issuer_id: Mapped[int | None] = mapped_column(BigInteger)
    issuer_name: Mapped[str | None] = mapped_column(String(255))
    assignee_id: Mapped[int | None] = mapped_column(BigInteger)
    acceptor_id: Mapped[int | None] = mapped_column(BigInteger)
    start_location_id: Mapped[int | None] = mapped_column(BigInteger)
    start_location_name: Mapped[str | None] = mapped_column(String(255))
    end_location_id: Mapped[int | None] = mapped_column(BigInteger)
    end_location_name: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    reward: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    collateral: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    buyout: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    volume: Mapped[Decimal | None] = mapped_column(Numeric(20, 4))
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_accepted: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    date_completed: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bucket_fk: Mapped[str | None] = mapped_column(Uuid, ForeignKey("project_buckets.id"))
