from datetime import datetime
from decimal import Decimal

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.inventory_lot import InventoryLot
from app.models.inventory_movement import InventoryMovement


class CostBasisService:
    def __init__(self, db: Session):
        self.db = db

    def consume_fifo(self, *, bucket_fk: str, type_id: int, quantity: Decimal, occurred_at: datetime, ref_source_type: str, ref_source_uuid: str | None = None, sale_unit_price: Decimal | None = None) -> dict:
        remaining = quantity
        cogs = Decimal('0')
        unmatched = Decimal('0')
        lots = list(self.db.scalars(select(InventoryLot).where(and_(InventoryLot.bucket_fk == bucket_fk, InventoryLot.type_id == type_id, InventoryLot.quantity_remaining > 0)).order_by(InventoryLot.acquired_at.asc())))
        for lot in lots:
            if remaining <= 0:
                break
            take = min(remaining, lot.quantity_remaining)
            lot.quantity_remaining -= take
            value = (take * lot.unit_cost).quantize(Decimal('0.01'))
            cogs += value
            self.db.add(InventoryMovement(lot_fk=lot.id, bucket_fk=bucket_fk, movement_type='sell', ref_source_type=ref_source_type, ref_source_uuid=ref_source_uuid, type_id=type_id, quantity=take, unit_value=sale_unit_price or lot.unit_cost, total_value=value, occurred_at=occurred_at))
            remaining -= take
        if remaining > 0:
            unmatched = remaining
        self.db.flush()
        return {"realised_cogs": cogs, "unmatched_quantity": unmatched}
