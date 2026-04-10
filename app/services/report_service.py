from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.bucket_assignment import BucketAssignment
from app.models.market_order import MarketOrder
from app.models.wallet_transaction import WalletTransaction
from app.schemas.report import BucketSummary


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def bucket_summary(self, bucket_id: str) -> BucketSummary:
        b_id = UUID(bucket_id)
        tx_assignments = list(
            self.db.scalars(
                select(BucketAssignment).where(
                    BucketAssignment.bucket_fk == b_id, BucketAssignment.source_type == "wallet_transaction"
                )
            )
        )
        tx_ids = [a.source_uuid for a in tx_assignments]
        txs = list(self.db.scalars(select(WalletTransaction).where(WalletTransaction.id.in_(tx_ids)))) if tx_ids else []

        order_assignments = list(
            self.db.scalars(
                select(BucketAssignment).where(BucketAssignment.bucket_fk == b_id, BucketAssignment.source_type == "market_order")
            )
        )
        order_ids = [a.source_uuid for a in order_assignments]
        orders = list(self.db.scalars(select(MarketOrder).where(MarketOrder.id.in_(order_ids)))) if order_ids else []

        buy_spend = sum((t.total_price for t in txs if t.is_buy), Decimal("0"))
        sell_revenue = sum((t.total_price for t in txs if not t.is_buy), Decimal("0"))
        broker_fees = sum((o.broker_fee or Decimal("0") for o in orders), Decimal("0"))
        taxes = sum((o.sales_tax or Decimal("0") for o in orders), Decimal("0"))
        open_sell = sum((o.price * o.volume_remain for o in orders if o.status == "open" and not o.is_buy_order), Decimal("0"))
        open_buy = sum((o.price * o.volume_remain for o in orders if o.status == "open" and o.is_buy_order), Decimal("0"))
        realized = sell_revenue - buy_spend - broker_fees - taxes
        unrealized = open_sell - open_buy

        return BucketSummary(
            bucket_id=bucket_id,
            total_buy_spend=buy_spend,
            total_sell_revenue=sell_revenue,
            total_broker_fees=broker_fees,
            total_taxes=taxes,
            open_sell_order_value=open_sell,
            open_buy_order_committed_value=open_buy,
            realized_pnl=realized,
            unrealized_estimate=unrealized,
            total_estimate=realized + unrealized,
        )
