from datetime import UTC, datetime
from uuid import UUID

import httpx

try:
    from redis import Redis
    from rq import Queue
except Exception:  # pragma: no cover
    Redis = None
    Queue = None
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.eve_character import EveCharacter
from app.models.sync_job import SyncJob
from app.schemas.rule import RuleRunRequest
from app.services.assignment_rule_service import AssignmentRuleService
from app.services.order_service import OrderService
from app.services.wallet_journal_service import WalletJournalService
from app.services.wallet_service import WalletService


class SyncSchedulerService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def _create_job(self, user_id: str, job_type: str, details: dict | None = None) -> SyncJob:
        job = SyncJob(user_id=user_id, job_type=job_type, status="queued", details_json=details or {})
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    async def _run_sync(self, user_id: str, character_ids: list[str], run_rules: bool = True) -> dict:
        stats = {"wallet_transactions": 0, "wallet_journal": 0, "orders": 0, "rules_assignments": 0}
        for c_id in character_ids:
            character = self.db.get(EveCharacter, c_id)
            if not character or str(character.user_id) != user_id:
                continue
            for _ in range(2):
                try:
                    stats["wallet_transactions"] += await WalletService(self.db).sync(character)
                    stats["wallet_journal"] += await WalletJournalService(self.db).sync(character)
                    stats["orders"] += await OrderService(self.db).sync(character, include_history=True)
                    break
                except httpx.HTTPError:
                    continue
        if run_rules:
            stats["rules_assignments"] = AssignmentRuleService(self.db).run(
                user_id,
                payload=RuleRunRequest(character_ids=character_ids, bucket_id=None, only_unassigned=True, force_reassign=False),
            )
        return stats

    async def sync_character(self, user_id: str, character_id: str, run_rules: bool = True) -> SyncJob:
        job = self._create_job(user_id, "character_sync", {"character_id": character_id})
        if self.settings.sync_use_background_worker and Queue and Redis:
            q = Queue(connection=Redis.from_url(self.settings.redis_url))
            q.enqueue("app.worker.run_sync_job", str(job.id), user_id, [character_id], run_rules)
            return job
        await self.run_job_now(job.id, user_id, [character_id], run_rules)
        self.db.refresh(job)
        return job

    async def sync_all(self, user_id: str, run_rules: bool = True) -> SyncJob:
        character_ids = [str(x) for x in self.db.scalars(select(EveCharacter.id).where(EveCharacter.user_id == UUID(user_id)))]
        job = self._create_job(user_id, "all_characters_sync", {"character_ids": character_ids})
        if self.settings.sync_use_background_worker and Queue and Redis:
            q = Queue(connection=Redis.from_url(self.settings.redis_url))
            q.enqueue("app.worker.run_sync_job", str(job.id), user_id, character_ids, run_rules)
            return job
        await self.run_job_now(job.id, user_id, character_ids, run_rules)
        self.db.refresh(job)
        return job

    async def run_job_now(self, job_id: str, user_id: str, character_ids: list[str], run_rules: bool = True) -> None:
        job = self.db.get(SyncJob, job_id)
        if not job:
            return
        job.status = "running"
        job.started_at = datetime.now(UTC)
        self.db.commit()
        try:
            stats = await self._run_sync(user_id, character_ids, run_rules)
            job.status = "success"
            job.details_json = {**(job.details_json or {}), **stats}
        except Exception as exc:
            job.status = "failed"
            job.details_json = {**(job.details_json or {}), "error": str(exc)}
        job.finished_at = datetime.now(UTC)
        self.db.commit()

    def list_jobs(self, user_id: str) -> list[SyncJob]:
        return list(self.db.scalars(select(SyncJob).where(SyncJob.user_id == user_id).order_by(SyncJob.created_at.desc())))

    def get_job(self, user_id: str, job_id: str) -> SyncJob | None:
        return self.db.scalar(select(SyncJob).where(SyncJob.id == job_id, SyncJob.user_id == user_id))
