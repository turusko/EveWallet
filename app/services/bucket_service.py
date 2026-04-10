from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.bucket_assignment import BucketAssignment
from app.models.eve_character import EveCharacter
from app.models.market_order import MarketOrder
from app.models.project_bucket import ProjectBucket
from app.models.wallet_journal_entry import WalletJournalEntry
from app.models.wallet_transaction import WalletTransaction
from app.schemas.bucket import AssignmentItem, BucketCreate, BucketUpdate


class BucketService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, payload: BucketCreate) -> ProjectBucket:
        bucket = ProjectBucket(user_id=user_id, name=payload.name, description=payload.description)
        self.db.add(bucket)
        self.db.commit()
        self.db.refresh(bucket)
        return bucket

    def list(self, user_id: str) -> list[ProjectBucket]:
        return list(self.db.scalars(select(ProjectBucket).where(ProjectBucket.user_id == user_id)))

    def get(self, user_id: str, bucket_id: str) -> ProjectBucket | None:
        return self.db.scalar(select(ProjectBucket).where(ProjectBucket.id == bucket_id, ProjectBucket.user_id == user_id))

    def update(self, user_id: str, bucket_id: str, payload: BucketUpdate) -> ProjectBucket:
        bucket = self.get(user_id, bucket_id)
        if not bucket:
            raise ValueError("Bucket not found")
        for key, value in payload.model_dump(exclude_none=True).items():
            setattr(bucket, key, value)
        self.db.commit()
        self.db.refresh(bucket)
        return bucket

    def archive(self, user_id: str, bucket_id: str) -> ProjectBucket:
        bucket = self.get(user_id, bucket_id)
        if not bucket:
            raise ValueError("Bucket not found")
        bucket.status = "archived"
        bucket.archived_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(bucket)
        return bucket

    def _validate_source_belongs_to_user(self, user_id: str, item: AssignmentItem) -> None:
        source_id = UUID(item.source_uuid)
        if item.source_type == "wallet_transaction":
            stmt = (
                select(WalletTransaction.id)
                .join(EveCharacter, WalletTransaction.character_fk == EveCharacter.id)
                .where(WalletTransaction.id == source_id, EveCharacter.user_id == UUID(user_id))
            )
        elif item.source_type == "market_order":
            stmt = (
                select(MarketOrder.id)
                .join(EveCharacter, MarketOrder.character_fk == EveCharacter.id)
                .where(MarketOrder.id == source_id, EveCharacter.user_id == UUID(user_id))
            )
        else:
            stmt = (
                select(WalletJournalEntry.id)
                .join(EveCharacter, WalletJournalEntry.character_fk == EveCharacter.id)
                .where(WalletJournalEntry.id == source_id, EveCharacter.user_id == UUID(user_id))
            )
        if not self.db.scalar(stmt):
            raise ValueError(f"Source does not belong to user: {item.source_uuid}")

    def assign(self, user_id: str, bucket_id: str, items: list[AssignmentItem], note: str | None = None) -> int:
        bucket = self.get(user_id, bucket_id)
        if not bucket:
            raise ValueError("Bucket not found")
        count = 0
        for item in items:
            self._validate_source_belongs_to_user(user_id, item)
            existing = self.db.scalar(
                select(BucketAssignment).where(
                    BucketAssignment.source_type == item.source_type,
                    BucketAssignment.source_uuid == UUID(item.source_uuid),
                )
            )
            if existing:
                continue
            self.db.add(
                BucketAssignment(
                    bucket_fk=bucket.id,
                    source_type=item.source_type,
                    source_uuid=UUID(item.source_uuid),
                    assigned_by_user_id=UUID(user_id),
                    note=note,
                    assignment_method="manual",
                )
            )
            count += 1
        self.db.commit()
        return count

    def unassign(self, user_id: str, bucket_id: str, items: list[AssignmentItem]) -> int:
        bucket = self.get(user_id, bucket_id)
        if not bucket:
            raise ValueError("Bucket not found")
        count = 0
        for item in items:
            result = self.db.execute(
                delete(BucketAssignment).where(
                    BucketAssignment.bucket_fk == bucket.id,
                    BucketAssignment.source_type == item.source_type,
                    BucketAssignment.source_uuid == UUID(item.source_uuid),
                )
            )
            count += result.rowcount
        self.db.commit()
        return count
