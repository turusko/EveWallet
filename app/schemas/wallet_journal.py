from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class WalletJournalEntryOut(BaseModel):
    id: str
    character_fk: str
    journal_ref_id: int
    date: datetime
    ref_type: str
    amount: Decimal
    description: str | None = None
    reason: str | None = None

    model_config = {"from_attributes": True}


class WalletJournalSyncResponse(BaseModel):
    character_id: str
    inserted_or_updated: int
