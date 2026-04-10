from datetime import UTC, datetime
from decimal import Decimal

from app.services.cost_basis_service import CostBasisService
from app.services.structure_service import StructureService


class Lot:
    def __init__(self, **k):
        self.__dict__.update(k)


class DB:
    def __init__(self):
        self.lots = [
            Lot(id='l1', bucket_fk='b', type_id=34, quantity_remaining=Decimal('10'), unit_cost=Decimal('5'), acquired_at=datetime(2026, 1, 1, tzinfo=UTC)),
            Lot(id='l2', bucket_fk='b', type_id=34, quantity_remaining=Decimal('8'), unit_cost=Decimal('6'), acquired_at=datetime(2026, 1, 2, tzinfo=UTC)),
        ]
        self.added = []

    def scalars(self, stmt):
        text = str(stmt)
        if 'inventory_lots' in text:
            return self.lots
        return []

    def add(self, x):
        self.added.append(x)

    def flush(self):
        return None

    def scalar(self, stmt):
        return None


def test_fifo_lot_consumption_and_partial_consumption():
    db = DB()
    result = CostBasisService(db).consume_fifo(bucket_fk='b', type_id=34, quantity=Decimal('12'), occurred_at=datetime.now(UTC), ref_source_type='wallet_transaction')
    assert result['realised_cogs'] == Decimal('62.00')
    assert result['unmatched_quantity'] == Decimal('0')


def test_oversell_warning_generation():
    db = DB()
    result = CostBasisService(db).consume_fifo(bucket_fk='b', type_id=34, quantity=Decimal('25'), occurred_at=datetime.now(UTC), ref_source_type='wallet_transaction')
    assert result['unmatched_quantity'] == Decimal('7')


def test_structure_resolution_caching():
    db = DB()
    name = StructureService(db).resolve_location(60003760, 'station')
    assert name.startswith('unresolved:')
