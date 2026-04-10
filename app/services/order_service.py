from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decrypt_if_possible
from app.models.eve_character import EveCharacter
from app.models.market_order import MarketOrder
from app.services.auth_service import AuthService
from app.services.esi_client import ESIClient


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.client = ESIClient()
        self.auth = AuthService(db)

    async def sync(self, character: EveCharacter, include_history: bool = False) -> int:
        token = await self.auth.refresh_for_character(character)
        access = decrypt_if_possible(token.access_token)
        rows = await self.client.character_orders(character.character_id, access, history=False)
        if include_history:
            rows.extend(await self.client.character_orders(character.character_id, access, history=True))

        count = 0
        for row in rows:
            existing = self.db.scalar(select(MarketOrder).where(MarketOrder.order_id == row["order_id"]))
            payload = {
                "character_fk": character.id,
                "order_id": row["order_id"],
                "type_id": row["type_id"],
                "location_id": row.get("location_id"),
                "region_id": row.get("region_id"),
                "price": Decimal(str(row["price"])),
                "volume_total": row["volume_total"],
                "volume_remain": row["volume_remain"],
                "min_volume": row.get("min_volume"),
                "is_buy_order": bool(row["is_buy_order"]),
                "issued_at": datetime.fromisoformat(row["issued"].replace("Z", "+00:00")),
                "expires_at": datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")) if row.get("expires_at") else None,
                "status": row.get("state", "open"),
                "is_history": bool(history := (row.get("state") not in {None, "open", "active"} or row.get("is_history", False) or include_history)),
                "state": row.get("state"),
                "volume_filled": row.get("volume_total", 0) - row.get("volume_remain", 0),
                "last_seen_at": datetime.now(UTC),
                "closed_at": datetime.fromisoformat(row["issued"].replace("Z", "+00:00")) if history else None,
                "escrow": Decimal(str(row["escrow"])) if row.get("escrow") is not None else None,
                "broker_fee": Decimal(str(row["broker_fee"])) if row.get("broker_fee") is not None else None,
                "sales_tax": Decimal(str(row["sales_tax"])) if row.get("sales_tax") is not None else None,
            }
            if existing:
                for k, v in payload.items():
                    setattr(existing, k, v)
            else:
                self.db.add(MarketOrder(**payload))
            count += 1

        character.last_synced_at = datetime.now(UTC)
        self.db.commit()
        return count

    def list(self, *, character_id: str | None = None, is_buy_order: bool | None = None, status: str | None = None, skip: int = 0, limit: int = 100):
        stmt = select(MarketOrder)
        if character_id:
            stmt = stmt.where(MarketOrder.character_fk == character_id)
        if is_buy_order is not None:
            stmt = stmt.where(MarketOrder.is_buy_order == is_buy_order)
        if status:
            stmt = stmt.where(MarketOrder.status == status)
        return list(self.db.scalars(stmt.offset(skip).limit(limit)))
