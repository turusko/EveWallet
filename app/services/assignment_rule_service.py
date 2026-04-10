from decimal import Decimal
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.assignment_rule import AssignmentRule
from app.models.bucket_assignment import BucketAssignment
from app.models.eve_character import EveCharacter
from app.models.market_order import MarketOrder
from app.models.project_bucket import ProjectBucket
from app.models.wallet_journal_entry import WalletJournalEntry
from app.models.wallet_transaction import WalletTransaction
from app.schemas.rule import RuleCreate, RuleRunRequest, RuleUpdate


class AssignmentRuleService:
    def __init__(self, db: Session):
        self.db = db

    def _validate_bucket_access(self, user_id: str, bucket_fk: UUID) -> None:
        bucket = self.db.scalar(select(ProjectBucket).where(ProjectBucket.id == bucket_fk, ProjectBucket.user_id == user_id))
        if not bucket:
            raise ValueError("Bucket not found for user")

    def _validate_conditions(self, conditions: dict) -> None:
        if not isinstance(conditions, dict):
            raise ValueError("conditions_json must be an object")

    def create(self, user_id: str, payload: RuleCreate) -> AssignmentRule:
        self._validate_bucket_access(user_id, payload.bucket_fk)
        self._validate_conditions(payload.conditions_json)
        rule = AssignmentRule(user_id=user_id, **payload.model_dump())
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def list(self, user_id: str) -> list[AssignmentRule]:
        return list(self.db.scalars(select(AssignmentRule).where(AssignmentRule.user_id == user_id).order_by(AssignmentRule.priority.asc())))

    def get(self, user_id: str, rule_id: str) -> AssignmentRule | None:
        return self.db.scalar(select(AssignmentRule).where(AssignmentRule.id == rule_id, AssignmentRule.user_id == user_id))

    def update(self, user_id: str, rule_id: str, payload: RuleUpdate) -> AssignmentRule:
        rule = self.get(user_id, rule_id)
        if not rule:
            raise ValueError("Rule not found")
        updates = payload.model_dump(exclude_none=True)
        if "bucket_fk" in updates:
            self._validate_bucket_access(user_id, updates["bucket_fk"])
        if "conditions_json" in updates:
            self._validate_conditions(updates["conditions_json"])
        for k, v in updates.items():
            setattr(rule, k, v)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete(self, user_id: str, rule_id: str) -> None:
        rule = self.get(user_id, rule_id)
        if not rule:
            raise ValueError("Rule not found")
        self.db.delete(rule)
        self.db.commit()

    def _rule_matches_tx(self, rule: AssignmentRule, row: WalletTransaction) -> bool:
        c = rule.conditions_json
        return all(
            [
                ("character_ids" not in c or str(row.character_fk) in {str(x) for x in c["character_ids"]}),
                ("is_buy" not in c or row.is_buy == c["is_buy"]),
                ("type_ids" not in c or row.type_id in c["type_ids"]),
                ("location_ids" not in c or row.location_id in c["location_ids"]),
                ("client_ids" not in c or row.client_id in c["client_ids"]),
                ("min_total_price" not in c or row.total_price >= Decimal(str(c["min_total_price"]))),
                ("max_total_price" not in c or row.total_price <= Decimal(str(c["max_total_price"]))),
                ("date_from" not in c or row.date.date() >= datetime.fromisoformat(c["date_from"]).date()),
                ("date_to" not in c or row.date.date() <= datetime.fromisoformat(c["date_to"]).date()),
            ]
        )

    def _rule_matches_journal(self, rule: AssignmentRule, row: WalletJournalEntry) -> bool:
        c = rule.conditions_json
        text_blob = f"{row.description or ''} {row.reason or ''}".lower()
        return all(
            [
                ("character_ids" not in c or str(row.character_fk) in {str(x) for x in c["character_ids"]}),
                ("ref_types" not in c or row.ref_type in c["ref_types"]),
                ("first_party_ids" not in c or row.first_party_id in c["first_party_ids"]),
                ("second_party_ids" not in c or row.second_party_id in c["second_party_ids"]),
                ("min_amount" not in c or row.amount >= Decimal(str(c["min_amount"]))),
                ("max_amount" not in c or row.amount <= Decimal(str(c["max_amount"]))),
                ("date_from" not in c or row.date.date() >= datetime.fromisoformat(c["date_from"]).date()),
                ("date_to" not in c or row.date.date() <= datetime.fromisoformat(c["date_to"]).date()),
                ("text_contains" not in c or c["text_contains"].lower() in text_blob),
            ]
        )

    def _rule_matches_order(self, rule: AssignmentRule, row: MarketOrder) -> bool:
        c = rule.conditions_json
        return all(
            [
                ("character_ids" not in c or str(row.character_fk) in {str(x) for x in c["character_ids"]}),
                ("is_buy_order" not in c or row.is_buy_order == c["is_buy_order"]),
                ("type_ids" not in c or row.type_id in c["type_ids"]),
                ("location_ids" not in c or row.location_id in c["location_ids"]),
                ("status" not in c or row.status == c["status"]),
                ("is_history" not in c or row.is_history == c["is_history"]),
                ("date_from" not in c or row.issued_at.date() >= datetime.fromisoformat(c["date_from"]).date()),
                ("date_to" not in c or row.issued_at.date() <= datetime.fromisoformat(c["date_to"]).date()),
            ]
        )

    def run(self, user_id: str, payload: RuleRunRequest) -> int:
        rules = list(
            self.db.scalars(
                select(AssignmentRule).where(AssignmentRule.user_id == user_id, AssignmentRule.enabled.is_(True)).order_by(AssignmentRule.priority.asc())
            )
        )
        if payload.bucket_id:
            rules = [r for r in rules if str(r.bucket_fk) == str(payload.bucket_id)]

        char_stmt = select(EveCharacter.id).where(EveCharacter.user_id == UUID(user_id))
        if payload.character_ids:
            char_stmt = char_stmt.where(EveCharacter.id.in_(payload.character_ids))
        character_ids = list(self.db.scalars(char_stmt))

        assigned_count = 0
        for source_type, model, matcher in [
            ("wallet_transaction", WalletTransaction, self._rule_matches_tx),
            ("wallet_journal", WalletJournalEntry, self._rule_matches_journal),
            ("market_order", MarketOrder, self._rule_matches_order),
        ]:
            rows = list(self.db.scalars(select(model).where(model.character_fk.in_(character_ids))))
            for row in rows:
                existing = self.db.scalar(
                    select(BucketAssignment).where(BucketAssignment.source_type == source_type, BucketAssignment.source_uuid == row.id)
                )
                if existing and (payload.only_unassigned and not payload.force_reassign):
                    continue
                if existing and payload.force_reassign and existing.assignment_method == "manual":
                    continue
                for rule in rules:
                    if matcher(rule, row):
                        if existing and payload.force_reassign and existing.assignment_method == "rule":
                            self.db.delete(existing)
                            self.db.flush()
                        if not existing:
                            self.db.add(
                                BucketAssignment(
                                    bucket_fk=rule.bucket_fk,
                                    source_type=source_type,
                                    source_uuid=row.id,
                                    assigned_by_user_id=UUID(user_id),
                                    assignment_method="rule",
                                    assignment_rule_id=rule.id,
                                    note=f"rule:{rule.name}",
                                )
                            )
                            assigned_count += 1
                        if rule.stop_processing:
                            break

        self.db.commit()
        return assigned_count
