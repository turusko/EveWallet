from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class IndustryJob(UUIDTimestampMixin, Base):
    __tablename__ = "industry_jobs"

    character_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("eve_characters.id"), nullable=False)
    eve_job_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    blueprint_type_id: Mapped[int | None] = mapped_column(BigInteger)
    blueprint_type_name: Mapped[str | None] = mapped_column(String(255))
    product_type_id: Mapped[int | None] = mapped_column(BigInteger)
    product_type_name: Mapped[str | None] = mapped_column(String(255))
    station_id: Mapped[int | None] = mapped_column(BigInteger)
    station_name: Mapped[str | None] = mapped_column(String(255))
    installer_id: Mapped[int | None] = mapped_column(BigInteger)
    activity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    runs: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    licensed_runs: Mapped[int | None] = mapped_column(Integer)
    successful_runs: Mapped[int | None] = mapped_column(Integer)
    bucket_fk: Mapped[str | None] = mapped_column(Uuid, ForeignKey("project_buckets.id"))
