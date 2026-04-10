from decimal import Decimal

from pydantic import BaseModel


class BucketSummary(BaseModel):
    bucket_id: str
    total_buy_spend: Decimal
    total_sell_revenue: Decimal
    total_broker_fees: Decimal
    total_taxes: Decimal
    open_sell_order_value: Decimal
    open_buy_order_committed_value: Decimal
    realized_pnl: Decimal
    unrealized_estimate: Decimal
    total_estimate: Decimal
