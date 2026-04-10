from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class BucketSummary(BaseModel):
    bucket_id: str
    buy_spend: Decimal
    sell_revenue: Decimal
    broker_fees: Decimal
    sales_taxes: Decimal
    wallet_adjustments: Decimal
    open_sell_order_value: Decimal
    open_buy_committed_value: Decimal
    realised_pnl: Decimal
    unrealised_estimate: Decimal
    net_estimate: Decimal
    active_order_count: int
    closed_order_count: int
    last_sync_at: datetime | None
    notes: str = "Realised P&L is a simple cashflow-based estimate (not FIFO lot matching)."
