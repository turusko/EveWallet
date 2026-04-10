from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.character_asset import CharacterAsset
from app.models.inventory_lot import InventoryLot
from app.models.inventory_movement import InventoryMovement


class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_lot(self, *, bucket_fk: str | None, character_fk: str | None, source_type: str, source_uuid: str | None, type_id: int, type_name: str | None, quantity: Decimal, unit_cost: Decimal, acquired_at: datetime, location_id: int | None = None, location_name: str | None = None) -> InventoryLot:
        total = (quantity * unit_cost).quantize(Decimal('0.01'))
        lot = InventoryLot(bucket_fk=bucket_fk, character_fk=character_fk, source_type=source_type, source_uuid=source_uuid, type_id=type_id, type_name=type_name, acquired_at=acquired_at, quantity_total=quantity, quantity_remaining=quantity, unit_cost=unit_cost, total_cost=total, location_id=location_id, location_name=location_name)
        self.db.add(lot)
        self.db.flush()
        self.db.add(InventoryMovement(lot_fk=lot.id, bucket_fk=bucket_fk, movement_type='acquire', ref_source_type=source_type, ref_source_uuid=source_uuid, type_id=type_id, quantity=quantity, unit_value=unit_cost, total_value=total, occurred_at=acquired_at))
        self.db.flush()
        return lot

    def list_lots(self, bucket_id: str | None = None):
        stmt = select(InventoryLot)
        if bucket_id:
            stmt = stmt.where(InventoryLot.bucket_fk == bucket_id)
        return list(self.db.scalars(stmt.order_by(InventoryLot.acquired_at.desc())))

    def list_movements(self, bucket_id: str | None = None):
        stmt = select(InventoryMovement)
        if bucket_id:
            stmt = stmt.where(InventoryMovement.bucket_fk == bucket_id)
        return list(self.db.scalars(stmt.order_by(InventoryMovement.occurred_at.desc())))

    def reconcile_assets(self, bucket_id: str):
        lots = list(self.db.scalars(select(InventoryLot).where(and_(InventoryLot.bucket_fk == bucket_id, InventoryLot.quantity_remaining > 0))))
        by_type = {}
        for l in lots:
            by_type[l.type_id] = by_type.get(l.type_id, Decimal('0')) + l.quantity_remaining
        assets = list(self.db.scalars(select(CharacterAsset).where(CharacterAsset.bucket_fk == bucket_id, CharacterAsset.is_present.is_(True))))
        warnings = []
        for a in assets:
            if Decimal(a.quantity) < by_type.get(a.type_id, Decimal('0')):
                warnings.append(f'lot quantity exceeds assets for type {a.type_id}')
        return {"warnings": warnings, "checked_at": datetime.now(UTC)}
