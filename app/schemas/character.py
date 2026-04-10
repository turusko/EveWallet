from datetime import datetime

from pydantic import BaseModel


class CharacterOut(BaseModel):
    id: str
    character_id: int
    character_name: str
    scopes: str
    last_synced_at: datetime | None = None

    model_config = {"from_attributes": True}
