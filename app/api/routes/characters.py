from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.character import CharacterOut
from app.services.character_service import CharacterService

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("", response_model=list[CharacterOut])
def list_characters(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return CharacterService(db).list(str(user.id))


@router.get("/{character_id}", response_model=CharacterOut)
def get_character(character_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    character = CharacterService(db).get(str(user.id), character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.delete("/{character_id}", response_model=CharacterOut)
def delete_character(character_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return CharacterService(db).unlink(str(user.id), character_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
