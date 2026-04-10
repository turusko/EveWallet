import csv
import io
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bucket_assignment import BucketAssignment
from app.models.eve_character import EveCharacter
from app.models.market_order import MarketOrder
from app.models.project_bucket import ProjectBucket
from app.models.wallet_journal_entry import WalletJournalEntry
from app.models.wallet_transaction import WalletTransaction
from app.schemas.report import BucketSummary

BROKER_FEE_REF_TYPES = {"brokers_fee", "broker_fee"}
TAX_REF_TYPES = {"transaction_tax", "sales_tax"}


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def _bucket_data(self, bucket_id: str):
        b_id = UUID(bucket_id)
        assignments = list(self.db.scalars(select(BucketAssignment).where(BucketAssignment.bucket_fk == b_id)))
        tx_ids = [a.source_uuid for a in assignments if a.source_type == "wallet_transaction"]
        journal_ids = [a.source_uuid for a in assignments if a.source_type == "wallet_journal"]
        order_ids = [a.source_uuid for a in assignments if a.source_type == "market_order"]
        txs = list(self.db.scalars(select(WalletTransaction).where(WalletTransaction.id.in_(tx_ids)))) if tx_ids else []
        journals = list(self.db.scalars(select(WalletJournalEntry).where(WalletJournalEntry.id.in_(journal_ids)))) if journal_ids else []
        orders = list(self.db.scalars(select(MarketOrder).where(MarketOrder.id.in_(order_ids)))) if order_ids else []
        return assignments, txs, journals, orders

    def bucket_summary(self, bucket_id: str) -> BucketSummary:
        _, txs, journals, orders = self._bucket_data(bucket_id)

        buy_spend = sum((t.total_price for t in txs if t.is_buy), Decimal("0"))
        sell_revenue = sum((t.total_price for t in txs if not t.is_buy), Decimal("0"))
        broker_fees = sum((j.amount for j in journals if j.ref_type in BROKER_FEE_REF_TYPES), Decimal("0"))
        sales_taxes = sum((j.amount for j in journals if j.ref_type in TAX_REF_TYPES), Decimal("0"))
        wallet_adjustments = sum((j.amount for j in journals if j.ref_type not in (BROKER_FEE_REF_TYPES | TAX_REF_TYPES)), Decimal("0"))

        open_sell = sum((o.price * o.volume_remain for o in orders if o.status == "open" and not o.is_buy_order), Decimal("0"))
        open_buy = sum((o.price * o.volume_remain for o in orders if o.status == "open" and o.is_buy_order), Decimal("0"))

        realised = sell_revenue - buy_spend - abs(broker_fees) - abs(sales_taxes)
        unrealised = open_sell - open_buy
        active_orders = [o for o in orders if o.status == "open"]
        closed_orders = [o for o in orders if o.status != "open"]

        char_ids = list({*(t.character_fk for t in txs), *(j.character_fk for j in journals), *(o.character_fk for o in orders)})
        last_sync = None
        if char_ids:
            last_sync = self.db.scalar(
                select(EveCharacter.last_synced_at).where(EveCharacter.id.in_(char_ids)).order_by(EveCharacter.last_synced_at.desc())
            )

        return BucketSummary(
            bucket_id=bucket_id,
            buy_spend=buy_spend,
            sell_revenue=sell_revenue,
            broker_fees=abs(broker_fees),
            sales_taxes=abs(sales_taxes),
            wallet_adjustments=wallet_adjustments,
            open_sell_order_value=open_sell,
            open_buy_committed_value=open_buy,
            realised_pnl=realised,
            unrealised_estimate=unrealised,
            net_estimate=realised + unrealised,
            active_order_count=len(active_orders),
            closed_order_count=len(closed_orders),
            last_sync_at=last_sync,
        )

    def export_bucket_csv(self, bucket_id: str) -> str:
        summary = self.bucket_summary(bucket_id)
        assignments, txs, journals, orders = self._bucket_data(bucket_id)
        chars = {str(c.id): c.character_name for c in self.db.scalars(select(EveCharacter))}
        methods = {(a.source_type, str(a.source_uuid)): (a.assignment_method, str(a.bucket_fk)) for a in assignments}

        out = io.StringIO()
        writer = csv.writer(out)
        bucket = self.db.get(ProjectBucket, bucket_id)
        writer.writerow(["bucket_name", bucket.name if bucket else bucket_id])
        writer.writerow(["status", bucket.status if bucket else "unknown"])
        writer.writerow(["realised_pnl", summary.realised_pnl])
        writer.writerow(["unrealised_estimate", summary.unrealised_estimate])
        writer.writerow(["net_estimate", summary.net_estimate])
        writer.writerow(["buy_spend", summary.buy_spend])
        writer.writerow(["sell_revenue", summary.sell_revenue])
        writer.writerow(["broker_fees", summary.broker_fees])
        writer.writerow(["sales_taxes", summary.sales_taxes])
        writer.writerow(["wallet_adjustments", summary.wallet_adjustments])
        writer.writerow(["open_sell_order_value", summary.open_sell_order_value])
        writer.writerow(["open_buy_committed_value", summary.open_buy_committed_value])
        writer.writerow([])
        writer.writerow(
            [
                "source_type",
                "date",
                "character_name",
                "item_or_ref_type",
                "amount",
                "quantity",
                "unit_price",
                "location_name",
                "assigned_bucket",
                "assignment_method",
            ]
        )
        for t in txs:
            method, bucket_fk = methods[("wallet_transaction", str(t.id))]
            writer.writerow(
                [
                    "wallet_transaction",
                    t.date.isoformat(),
                    chars.get(str(t.character_fk), "unknown"),
                    str(t.type_id),
                    t.total_price,
                    t.quantity,
                    t.unit_price,
                    t.location_name or "",
                    bucket_fk,
                    method,
                ]
            )
        for j in journals:
            method, bucket_fk = methods[("wallet_journal", str(j.id))]
            writer.writerow(
                [
                    "wallet_journal",
                    j.date.isoformat(),
                    chars.get(str(j.character_fk), "unknown"),
                    j.ref_type,
                    j.amount,
                    "",
                    "",
                    "",
                    bucket_fk,
                    method,
                ]
            )
        for o in orders:
            method, bucket_fk = methods[("market_order", str(o.id))]
            writer.writerow(
                [
                    "market_order",
                    o.issued_at.isoformat(),
                    chars.get(str(o.character_fk), "unknown"),
                    str(o.type_id),
                    o.price * o.volume_remain,
                    o.volume_remain,
                    o.price,
                    o.location_name or "",
                    bucket_fk,
                    method,
                ]
            )
        return out.getvalue()

    def export_all_buckets_csv(self, user_id: str) -> str:
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["bucket_id", "bucket_name", "realised_pnl", "unrealised_estimate", "net_estimate", "wallet_adjustments"])
        for bucket in self.db.scalars(select(ProjectBucket).where(ProjectBucket.user_id == user_id)):
            s = self.bucket_summary(str(bucket.id))
            writer.writerow([bucket.id, bucket.name, s.realised_pnl, s.unrealised_estimate, s.net_estimate, s.wallet_adjustments])
        return out.getvalue()
