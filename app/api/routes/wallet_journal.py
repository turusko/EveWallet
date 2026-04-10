from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.bucket_assignment import BucketAssignment
from app.models.eve_character import EveCharacter
from app.schemas.wallet_journal import WalletJournalEntryOut, WalletJournalSyncResponse
from app.services.wallet_journal_service import WalletJournalService

router = APIRouter(prefix="/wallet-journal", tags=["wallet-journal"])


@router.post("/sync/{character_id}", response_model=WalletJournalSyncResponse)
async def sync_wallet_journal(character_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    character = db.get(EveCharacter, character_id)
    if not character or str(character.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Character not found")
    count = await WalletJournalService(db).sync(character)
    return WalletJournalSyncResponse(character_id=character_id, inserted_or_updated=count)


@router.get("", response_model=list[WalletJournalEntryOut])
def list_wallet_journal(
    character_id: str | None = None,
    bucket_id: str | None = None,
    ref_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if bucket_id:
        ids = list(
            db.scalars(
                select(BucketAssignment.source_uuid).where(
                    BucketAssignment.bucket_fk == bucket_id,
                    BucketAssignment.source_type == "wallet_journal",
                )
            )
        )
        rows = WalletJournalService(db).list(
            character_id=character_id,
            ref_type=ref_type,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            skip=0,
            limit=10000,
        )
        filtered = [r for r in rows if r.id in ids]
        return filtered[skip : skip + limit]
    return WalletJournalService(db).list(
        character_id=character_id,
        ref_type=ref_type,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        skip=skip,
        limit=limit,
    )
