from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.contract import Contract
from app.models.eve_character import EveCharacter
from app.schemas.phase3 import ContractOut
from app.services.bucket_service import BucketService
from app.services.contract_service import ContractService

router = APIRouter(prefix='/contracts', tags=['contracts'])


@router.post('/sync/{character_id}')
async def sync_contracts(character_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    character = db.get(EveCharacter, character_id)
    if not character or str(character.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail='Character not found')
    count = await ContractService(db).sync(character_id, payload=[])
    db.commit()
    return {'inserted_or_updated': count}


@router.get('', response_model=list[ContractOut])
def list_contracts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    owned = [str(c.id) for c in db.scalars(select(EveCharacter).where(EveCharacter.user_id == user.id))]
    return list(db.scalars(select(Contract).where(Contract.character_fk.in_(owned))))


@router.get('/{contract_id}', response_model=ContractOut)
def get_contract(contract_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = db.get(Contract, contract_id)
    if not c:
        raise HTTPException(status_code=404, detail='Contract not found')
    return c


@router.post('/{contract_id}/assign/{bucket_id}')
def assign_contract(contract_id: str, bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = db.get(Contract, contract_id)
    if not c:
        raise HTTPException(status_code=404, detail='Contract not found')
    bucket = BucketService(db).get(str(user.id), bucket_id)
    if not bucket:
        raise HTTPException(status_code=404, detail='Bucket not found')
    c.bucket_fk = bucket_id
    db.commit()
    return {'status': 'assigned'}
