from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.eve_character import EveCharacter
from app.schemas.wallet import WalletSyncResponse, WalletTransactionOut
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.post("/sync/{character_id}", response_model=WalletSyncResponse)
async def sync_wallet(character_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    character = db.get(EveCharacter, character_id)
    if not character or str(character.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Character not found")
    count = await WalletService(db).sync(character)
    return WalletSyncResponse(character_id=character_id, inserted_or_updated=count)


@router.get("/transactions", response_model=list[WalletTransactionOut])
def list_transactions(
    character_id: str | None = None,
    is_buy: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return WalletService(db).list(character_id=character_id, is_buy=is_buy, skip=skip, limit=limit)
