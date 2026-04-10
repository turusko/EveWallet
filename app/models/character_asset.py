from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class CharacterAsset(UUIDTimestampMixin, Base):
    __tablename__ = "character_assets"

    character_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("eve_characters.id"), nullable=False)
    asset_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    type_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type_name: Mapped[str | None] = mapped_column(String(255))
    location_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    location_type: Mapped[str | None] = mapped_column(String(64))
    location_name: Mapped[str | None] = mapped_column(String(255))
    location_flag: Mapped[str | None] = mapped_column(String(64))
    quantity: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_singleton: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    item_id: Mapped[int | None] = mapped_column(BigInteger)
    blueprint_copy: Mapped[bool | None] = mapped_column(Boolean)
    bucket_fk: Mapped[str | None] = mapped_column(Uuid, ForeignKey("project_buckets.id"))
    is_present: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
