from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.eve_character import EveCharacter
from app.schemas.auth import CallbackResponse, LoginResponse, TokenRefreshResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login", response_model=LoginResponse)
def login(db: Session = Depends(get_db)):
    service = AuthService(db)
    url, state = service.login_url()
    return LoginResponse(authorization_url=url, state=state)


@router.get("/callback", response_model=CallbackResponse)
async def callback(code: str = Query(...), db: Session = Depends(get_db)):
    service = AuthService(db)
    user, character, linked = await service.handle_callback(code)
    return CallbackResponse(user_id=str(user.id), character_id=character.character_id, character_name=character.character_name, linked=linked)


@router.post("/refresh/{character_id}", response_model=TokenRefreshResponse)
async def refresh(character_id: str, db: Session = Depends(get_db)):
    service = AuthService(db)
    character = db.scalar(select(EveCharacter).where(EveCharacter.id == character_id))
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    token = await service.refresh_for_character(character)
    return TokenRefreshResponse(character_id=character_id, expires_at=token.expires_at)
