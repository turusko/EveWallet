from decimal import Decimal

from app.schemas.report import BucketSummary
from app.services.report_service import ReportService


class Dummy:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeDB:
    def __init__(self, assignments, txs, orders):
        self.assignments = assignments
        self.txs = txs
        self.orders = orders

    def scalars(self, stmt):
        text = str(stmt)
        if "bucket_assignments" in text:
            if "wallet_transaction" in text:
                return self.assignments["tx"]
            return self.assignments["orders"]
        if "wallet_transactions" in text:
            return self.txs
        return self.orders


def test_bucket_summary_math():
    assignments = {
        "tx": [Dummy(source_uuid="a")],
        "orders": [Dummy(source_uuid="b")],
    }
    txs = [Dummy(total_price=Decimal("100"), is_buy=True), Dummy(total_price=Decimal("220"), is_buy=False)]
    orders = [
        Dummy(price=Decimal("10"), volume_remain=5, is_buy_order=False, status="open", broker_fee=Decimal("2"), sales_tax=Decimal("1")),
        Dummy(price=Decimal("7"), volume_remain=3, is_buy_order=True, status="open", broker_fee=Decimal("0"), sales_tax=Decimal("0")),
    ]

    summary = ReportService(FakeDB(assignments, txs, orders)).bucket_summary("00000000-0000-0000-0000-000000000001")
    assert isinstance(summary, BucketSummary)
    assert summary.realized_pnl == Decimal("117")
    assert summary.unrealized_estimate == Decimal("29")
