from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CharacterAssetOut(ORMBase):
    id: str
    character_fk: str
    asset_id: int
    type_id: int
    type_name: str | None = None
    location_id: int
    location_name: str | None = None
    quantity: int
    bucket_fk: str | None = None
    last_seen_at: datetime


class InventoryLotOut(ORMBase):
    id: str
    bucket_fk: str | None = None
    type_id: int
    type_name: str | None = None
    acquired_at: datetime
    quantity_total: Decimal
    quantity_remaining: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    location_name: str | None = None


class InventoryMovementOut(ORMBase):
    id: str
    lot_fk: str
    movement_type: str
    type_id: int
    quantity: Decimal
    total_value: Decimal | None = None
    occurred_at: datetime


class IndustryJobOut(ORMBase):
    id: str
    eve_job_id: int
    status: str
    product_type_id: int | None = None
    product_type_name: str | None = None
    runs: int
    cost: Decimal | None = None
    completed_date: datetime | None = None
    bucket_fk: str | None = None


class ContractOut(ORMBase):
    id: str
    contract_id: int
    type: str
    status: str
    price: Decimal | None = None
    reward: Decimal | None = None
    issued_at: datetime | None = None
    bucket_fk: str | None = None


class BucketProfitOut(ORMBase):
    bucket_id: str
    sales_revenue: Decimal
    realised_cogs: Decimal
    realised_gross_profit: Decimal
    broker_fees: Decimal
    sales_taxes: Decimal
    contract_costs: Decimal
    industry_costs: Decimal
    realised_net_profit: Decimal
    inventory_value_on_hand: Decimal
    open_sell_order_value: Decimal
    open_buy_commitment: Decimal
    unrealised_inventory_margin_estimate: Decimal
    unmatched_sales_quantity: Decimal
    warnings: list[str]
    last_sync_at: datetime | None = None
