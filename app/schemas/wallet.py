from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class WalletTransactionOut(BaseModel):
    id: str
    character_fk: str
    transaction_id: int
    date: datetime
    type_id: int
    unit_price: Decimal
    quantity: int
    total_price: Decimal
    is_buy: bool

    model_config = {"from_attributes": True}


class WalletSyncResponse(BaseModel):
    character_id: str
    inserted_or_updated: int
