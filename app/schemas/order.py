from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class MarketOrderOut(BaseModel):
    id: str
    character_fk: str
    order_id: int
    type_id: int
    price: Decimal
    volume_total: int
    volume_remain: int
    is_buy_order: bool
    status: str
    issued_at: datetime

    model_config = {"from_attributes": True}


class OrderSyncResponse(BaseModel):
    character_id: str
    inserted_or_updated: int
