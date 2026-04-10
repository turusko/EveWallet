from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.eve_character import EveCharacter
from app.schemas.order import MarketOrderOut, OrderSyncResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/sync/{character_id}", response_model=OrderSyncResponse)
async def sync_orders(
    character_id: str,
    include_history: bool = Query(default=False),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    character = db.get(EveCharacter, character_id)
    if not character or str(character.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Character not found")
    count = await OrderService(db).sync(character, include_history=include_history)
    return OrderSyncResponse(character_id=character_id, inserted_or_updated=count)


@router.get("", response_model=list[MarketOrderOut])
def list_orders(
    character_id: str | None = None,
    is_buy_order: bool | None = None,
    status: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return OrderService(db).list(
        character_id=character_id,
        is_buy_order=is_buy_order,
        status=status,
        skip=skip,
        limit=limit,
    )
