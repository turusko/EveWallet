from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RuleCreate(BaseModel):
    bucket_fk: UUID
    name: str
    enabled: bool = True
    priority: int = 100
    stop_processing: bool = True
    conditions_json: dict = Field(default_factory=dict)


class RuleUpdate(BaseModel):
    bucket_fk: UUID | None = None
    name: str | None = None
    enabled: bool | None = None
    priority: int | None = None
    stop_processing: bool | None = None
    conditions_json: dict | None = None


class RuleOut(BaseModel):
    id: UUID
    user_id: UUID
    bucket_fk: UUID
    name: str
    enabled: bool
    priority: int
    stop_processing: bool
    conditions_json: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RuleRunRequest(BaseModel):
    character_ids: list[UUID] | None = None
    bucket_id: UUID | None = None
    only_unassigned: bool = True
    force_reassign: bool = False


class RuleRunResponse(BaseModel):
    assignments_created: int
