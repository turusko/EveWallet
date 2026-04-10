from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class BucketCreate(BaseModel):
    name: str
    description: str | None = None


class BucketUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class BucketOut(BaseModel):
    id: str
    name: str
    description: str | None
    status: str
    archived_at: datetime | None

    model_config = {"from_attributes": True}


class AssignmentItem(BaseModel):
    source_type: Literal["wallet_transaction", "market_order"]
    source_uuid: str


class AssignmentRequest(BaseModel):
    items: list[AssignmentItem]
    note: str | None = None
