from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class IndustryJobOutput(UUIDTimestampMixin, Base):
    __tablename__ = "industry_job_outputs"

    job_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("industry_jobs.id"), nullable=False)
    type_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type_name: Mapped[str | None] = mapped_column(String(255))
    quantity_produced: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    total_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    lot_fk: Mapped[str | None] = mapped_column(Uuid, ForeignKey("inventory_lots.id"))
