from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.industry_job import IndustryJob
from app.services.inventory_service import InventoryService


class IndustryService:
    def __init__(self, db: Session):
        self.db = db

    async def sync(self, character_id: str, payload: list[dict] | None = None) -> int:
        rows = payload or []
        inserted = 0
        inv = InventoryService(self.db)
        for r in rows:
            existing = self.db.scalar(select(IndustryJob).where(IndustryJob.eve_job_id == int(r['job_id'])))
            if existing:
                job = existing
            else:
                job = IndustryJob(character_fk=character_id, eve_job_id=int(r['job_id']), activity_id=int(r.get('activity_id', 1)), status=r.get('status', 'active'), runs=int(r.get('runs', 1)))
                self.db.add(job)
                inserted += 1
            job.product_type_id = r.get('product_type_id')
            job.product_type_name = r.get('product_type_name')
            job.cost = Decimal(str(r.get('cost', '0')))
            job.status = r.get('status', 'active')
            if job.status == 'delivered' and job.bucket_fk and job.product_type_id:
                q = Decimal(str(r.get('quantity_produced', 0)))
                if q > 0:
                    inv.create_lot(bucket_fk=str(job.bucket_fk), character_fk=character_id, source_type='industry_output', source_uuid=str(job.id), type_id=job.product_type_id, type_name=job.product_type_name, quantity=q, unit_cost=(job.cost or Decimal('0')) / q if q else Decimal('0'), acquired_at=datetime.now(UTC))
        self.db.flush()
        return inserted
