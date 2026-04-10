from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.eve_character import EveCharacter
from app.models.industry_job import IndustryJob
from app.schemas.phase3 import IndustryJobOut
from app.services.bucket_service import BucketService
from app.services.industry_service import IndustryService

router = APIRouter(prefix='/industry', tags=['industry'])


@router.post('/sync/{character_id}')
async def sync_industry(character_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    character = db.get(EveCharacter, character_id)
    if not character or str(character.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail='Character not found')
    count = await IndustryService(db).sync(character_id, payload=[])
    db.commit()
    return {'inserted_or_updated': count}


@router.get('/jobs', response_model=list[IndustryJobOut])
def list_jobs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    owned = [str(c.id) for c in db.scalars(select(EveCharacter).where(EveCharacter.user_id == user.id))]
    return list(db.scalars(select(IndustryJob).where(IndustryJob.character_fk.in_(owned))))


@router.get('/jobs/{job_id}', response_model=IndustryJobOut)
def get_job(job_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    job = db.get(IndustryJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    return job


@router.post('/jobs/{job_id}/assign/{bucket_id}')
def assign_job(job_id: str, bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    job = db.get(IndustryJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    bucket = BucketService(db).get(str(user.id), bucket_id)
    if not bucket:
        raise HTTPException(status_code=404, detail='Bucket not found')
    job.bucket_fk = bucket_id
    db.commit()
    return {'status': 'assigned'}
