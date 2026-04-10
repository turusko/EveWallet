from decimal import Decimal

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.bucket_assignment import BucketAssignment
from app.models.contract import Contract
from app.models.industry_job import IndustryJob
from app.models.inventory_lot import InventoryLot
from app.models.inventory_movement import InventoryMovement
from app.models.market_order import MarketOrder
from app.models.wallet_journal_entry import WalletJournalEntry
from app.models.wallet_transaction import WalletTransaction
from app.schemas.phase3 import BucketProfitOut

BROKER_FEE_REF_TYPES = {"brokers_fee", "broker_fee"}
TAX_REF_TYPES = {"transaction_tax", "sales_tax"}


class ReportServicePhase3:
    def __init__(self, db: Session):
        self.db = db

    def bucket_profit(self, bucket_id: str) -> BucketProfitOut:
        assignments = list(self.db.scalars(select(BucketAssignment).where(BucketAssignment.bucket_fk == bucket_id)))
        tx_ids = [a.source_uuid for a in assignments if a.source_type == 'wallet_transaction']
        journal_ids = [a.source_uuid for a in assignments if a.source_type == 'wallet_journal']
        txs = list(self.db.scalars(select(WalletTransaction).where(WalletTransaction.id.in_(tx_ids)))) if tx_ids else []
        journals = list(self.db.scalars(select(WalletJournalEntry).where(WalletJournalEntry.id.in_(journal_ids)))) if journal_ids else []
        sales_revenue = sum((t.total_price for t in txs if not t.is_buy), Decimal('0'))
        realised_cogs = sum((m.total_value for m in self.db.scalars(select(InventoryMovement).where(and_(InventoryMovement.bucket_fk == bucket_id, InventoryMovement.movement_type == 'sell'))) if m.total_value), Decimal('0'))
        gross = sales_revenue - realised_cogs
        broker = abs(sum((j.amount for j in journals if j.ref_type in BROKER_FEE_REF_TYPES), Decimal('0')))
        taxes = abs(sum((j.amount for j in journals if j.ref_type in TAX_REF_TYPES), Decimal('0')))
        contract_costs = sum((c.price or Decimal('0') for c in self.db.scalars(select(Contract).where(Contract.bucket_fk == bucket_id))), Decimal('0'))
        industry_costs = sum((j.cost or Decimal('0') for j in self.db.scalars(select(IndustryJob).where(IndustryJob.bucket_fk == bucket_id))), Decimal('0'))
        inv_val = sum((l.quantity_remaining * l.unit_cost for l in self.db.scalars(select(InventoryLot).where(and_(InventoryLot.bucket_fk == bucket_id, InventoryLot.quantity_remaining > 0)))), Decimal('0'))
        orders = list(self.db.scalars(select(MarketOrder).where(MarketOrder.id.in_([a.source_uuid for a in assignments if a.source_type == 'market_order']))))
        open_sell = sum((o.price * o.volume_remain for o in orders if o.status == 'open' and not o.is_buy_order), Decimal('0'))
        open_buy = sum((o.price * o.volume_remain for o in orders if o.status == 'open' and o.is_buy_order), Decimal('0'))
        unmatched = Decimal('0')
        warnings = []
        if unmatched > 0:
            warnings.append('Unmatched sales quantity exists; COGS is partial.')
        return BucketProfitOut(bucket_id=bucket_id, sales_revenue=sales_revenue, realised_cogs=realised_cogs, realised_gross_profit=gross, broker_fees=broker, sales_taxes=taxes, contract_costs=contract_costs, industry_costs=industry_costs, realised_net_profit=gross - broker - taxes - contract_costs - industry_costs, inventory_value_on_hand=inv_val, open_sell_order_value=open_sell, open_buy_commitment=open_buy, unrealised_inventory_margin_estimate=open_sell - inv_val, unmatched_sales_quantity=unmatched, warnings=warnings)
