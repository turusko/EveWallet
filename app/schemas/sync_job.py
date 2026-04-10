from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SyncJobOut(BaseModel):
    id: UUID
    user_id: UUID
    job_type: str
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    details_json: dict | None

    model_config = {"from_attributes": True}
