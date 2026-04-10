from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decrypt_if_possible
from app.models.eve_character import EveCharacter
from app.models.token import EveToken
from app.models.wallet_transaction import WalletTransaction
from app.services.auth_service import AuthService
from app.services.esi_client import ESIClient


class WalletService:
    def __init__(self, db: Session):
        self.db = db
        self.client = ESIClient()
        self.auth = AuthService(db)

    async def sync(self, character: EveCharacter) -> int:
        token = await self.auth.refresh_for_character(character)
        access = decrypt_if_possible(token.access_token)
        rows = await self.client.character_wallet_transactions(character.character_id, access)
        count = 0
        for row in rows:
            existing = self.db.scalar(select(WalletTransaction).where(WalletTransaction.transaction_id == row["transaction_id"]))
            payload = {
                "character_fk": character.id,
                "transaction_id": row["transaction_id"],
                "date": datetime.fromisoformat(row["date"].replace("Z", "+00:00")),
                "type_id": row["type_id"],
                "location_id": row.get("location_id"),
                "unit_price": Decimal(str(row["unit_price"])),
                "quantity": row["quantity"],
                "total_price": Decimal(str(abs(row["unit_price"] * row["quantity"]))),
                "is_buy": bool(row.get("is_buy", False)),
                "is_personal": bool(row.get("is_personal", True)),
                "client_id": row.get("client_id"),
            }
            if existing:
                for k, v in payload.items():
                    setattr(existing, k, v)
            else:
                self.db.add(WalletTransaction(**payload))
            count += 1

        character.last_synced_at = datetime.now(UTC)
        self.db.commit()
        return count

    def list(self, *, character_id: str | None = None, is_buy: bool | None = None, skip: int = 0, limit: int = 100):
        stmt = select(WalletTransaction)
        if character_id:
            stmt = stmt.where(WalletTransaction.character_fk == character_id)
        if is_buy is not None:
            stmt = stmt.where(WalletTransaction.is_buy == is_buy)
        return list(self.db.scalars(stmt.offset(skip).limit(limit)))
