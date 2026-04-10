from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decrypt_if_possible
from app.models.eve_character import EveCharacter
from app.models.wallet_journal_entry import WalletJournalEntry
from app.services.auth_service import AuthService
from app.services.esi_client import ESIClient


class WalletJournalService:
    def __init__(self, db: Session):
        self.db = db
        self.client = ESIClient()
        self.auth = AuthService(db)

    async def sync(self, character: EveCharacter) -> int:
        token = await self.auth.refresh_for_character(character)
        access = decrypt_if_possible(token.access_token)
        rows = await self.client.character_wallet_journal(character.character_id, access)

        count = 0
        for row in rows:
            existing = self.db.scalar(select(WalletJournalEntry).where(WalletJournalEntry.journal_ref_id == row["id"]))
            payload = {
                "character_fk": character.id,
                "journal_ref_id": row["id"],
                "date": datetime.fromisoformat(row["date"].replace("Z", "+00:00")),
                "ref_type": row.get("ref_type", "unknown"),
                "amount": Decimal(str(row.get("amount", 0))),
                "balance": Decimal(str(row["balance"])) if row.get("balance") is not None else None,
                "tax": Decimal(str(row["tax"])) if row.get("tax") is not None else None,
                "tax_receiver_id": row.get("tax_receiver_id"),
                "context_id": row.get("context_id"),
                "context_id_type": row.get("context_id_type"),
                "description": row.get("description"),
                "first_party_id": row.get("first_party_id"),
                "second_party_id": row.get("second_party_id"),
                "reason": row.get("reason"),
            }
            if existing:
                for k, v in payload.items():
                    setattr(existing, k, v)
            else:
                self.db.add(WalletJournalEntry(**payload))
            count += 1

        character.last_synced_at = datetime.now(UTC)
        self.db.commit()
        return count

    def list(
        self,
        *,
        character_id: str | None = None,
        ref_type: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[WalletJournalEntry]:
        stmt = select(WalletJournalEntry)
        if character_id:
            stmt = stmt.where(WalletJournalEntry.character_fk == character_id)
        if ref_type:
            stmt = stmt.where(WalletJournalEntry.ref_type == ref_type)
        if start_date:
            stmt = stmt.where(WalletJournalEntry.date >= start_date)
        if end_date:
            stmt = stmt.where(WalletJournalEntry.date <= end_date)
        if min_amount is not None:
            stmt = stmt.where(WalletJournalEntry.amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.where(WalletJournalEntry.amount <= max_amount)
        return list(self.db.scalars(stmt.offset(skip).limit(limit)))
