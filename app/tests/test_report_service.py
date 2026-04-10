from datetime import datetime, UTC
from decimal import Decimal

from app.schemas.report import BucketSummary
from app.services.report_service import ReportService


class Dummy:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeDB:
    def __init__(self, assignments, txs, journals, orders):
        self.assignments = assignments
        self.txs = txs
        self.journals = journals
        self.orders = orders

    def scalars(self, stmt):
        text = str(stmt)
        if "bucket_assignments" in text:
            return self.assignments
        if "wallet_transactions" in text:
            return self.txs
        if "wallet_journal_entries" in text:
            return self.journals
        if "market_orders" in text:
            return self.orders
        if "eve_characters" in text:
            return [Dummy(id="c1", last_synced_at=datetime(2026, 1, 1, tzinfo=UTC))]
        return []

    def scalar(self, stmt):
        if "eve_characters" in str(stmt):
            return datetime(2026, 1, 1, tzinfo=UTC)
        return None

    def get(self, model, key):
        return Dummy(name="bucket", status="active")


def test_bucket_summary_math():
    assignments = [
        Dummy(source_type="wallet_transaction", source_uuid="a", assignment_method="rule", bucket_fk="b"),
        Dummy(source_type="wallet_journal", source_uuid="j1", assignment_method="rule", bucket_fk="b"),
        Dummy(source_type="wallet_journal", source_uuid="j2", assignment_method="rule", bucket_fk="b"),
        Dummy(source_type="market_order", source_uuid="o1", assignment_method="rule", bucket_fk="b"),
    ]
    txs = [Dummy(character_fk="c1", total_price=Decimal("100"), is_buy=True), Dummy(character_fk="c1", total_price=Decimal("220"), is_buy=False)]
    journals = [
        Dummy(character_fk="c1", amount=Decimal("-2"), ref_type="brokers_fee"),
        Dummy(character_fk="c1", amount=Decimal("-1"), ref_type="transaction_tax"),
    ]
    orders = [Dummy(character_fk="c1", price=Decimal("10"), volume_remain=5, is_buy_order=False, status="open")]

    summary = ReportService(FakeDB(assignments, txs, journals, orders)).bucket_summary("00000000-0000-0000-0000-000000000001")
    assert isinstance(summary, BucketSummary)
    assert summary.realised_pnl == Decimal("117")
    assert summary.unrealised_estimate == Decimal("50")
