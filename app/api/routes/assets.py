from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.character_asset import CharacterAsset
from app.models.eve_character import EveCharacter
from app.schemas.phase3 import CharacterAssetOut
from app.services.asset_service import AssetService

router = APIRouter(prefix='/assets', tags=['assets'])


@router.post('/sync/{character_id}')
async def sync_assets(character_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    character = db.get(EveCharacter, character_id)
    if not character or str(character.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail='Character not found')
    inserted = await AssetService(db).sync(character, assets_payload=[])
    db.commit()
    return {'inserted_or_updated': inserted}


@router.get('', response_model=list[CharacterAssetOut])
def list_assets(character_id: str | None = None, bucket_id: str | None = None, type_id: int | None = None, location_id: int | None = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(get_current_user)):
    owned = [str(c.id) for c in db.scalars(select(EveCharacter).where(EveCharacter.user_id == user.id))]
    stmt = select(CharacterAsset).where(CharacterAsset.character_fk.in_(owned))
    if character_id:
        stmt = stmt.where(CharacterAsset.character_fk == character_id)
    if bucket_id:
        stmt = stmt.where(CharacterAsset.bucket_fk == bucket_id)
    if type_id:
        stmt = stmt.where(CharacterAsset.type_id == type_id)
    if location_id:
        stmt = stmt.where(CharacterAsset.location_id == location_id)
    return list(db.scalars(stmt.offset(skip).limit(limit)))
