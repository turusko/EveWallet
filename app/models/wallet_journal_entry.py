from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDTimestampMixin


class WalletJournalEntry(UUIDTimestampMixin, Base):
    __tablename__ = "wallet_journal_entries"
    __table_args__ = (Index("ix_wallet_journal_entries_date", "date"),)

    character_fk: Mapped[str] = mapped_column(Uuid, ForeignKey("eve_characters.id"), nullable=False)
    journal_ref_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ref_type: Mapped[str] = mapped_column(String(80), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    balance: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    tax: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    tax_receiver_id: Mapped[int | None] = mapped_column(BigInteger)
    context_id: Mapped[int | None] = mapped_column(BigInteger)
    context_id_type: Mapped[str | None] = mapped_column(String(80))
    description: Mapped[str | None] = mapped_column(Text)
    first_party_id: Mapped[int | None] = mapped_column(BigInteger)
    second_party_id: Mapped[int | None] = mapped_column(BigInteger)
    reason: Mapped[str | None] = mapped_column(Text)
