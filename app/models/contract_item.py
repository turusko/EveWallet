from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class ContractItem(UUIDTimestampMixin, Base):
    __tablename__ = "contract_items"

    contract_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("contracts.id"), nullable=False)
    record_id: Mapped[int | None] = mapped_column(BigInteger)
    type_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type_name: Mapped[str | None] = mapped_column(String(255))
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    is_included: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_singleton: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_quantity: Mapped[int | None] = mapped_column(Integer)
