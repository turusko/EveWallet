from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class IndustryJobMaterial(UUIDTimestampMixin, Base):
    __tablename__ = "industry_job_materials"

    job_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("industry_jobs.id"), nullable=False)
    type_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type_name: Mapped[str | None] = mapped_column(String(255))
    quantity_required: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    total_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
