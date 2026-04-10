from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.eve_character import EveCharacter
from app.schemas.sync_job import SyncJobOut
from app.services.sync_scheduler_service import SyncSchedulerService

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/character/{character_id}", response_model=SyncJobOut)
async def sync_character(character_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    character = db.get(EveCharacter, character_id)
    if not character or str(character.user_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Character not found")
    return await SyncSchedulerService(db).sync_character(str(user.id), character_id)


@router.post("/all", response_model=SyncJobOut)
async def sync_all(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return await SyncSchedulerService(db).sync_all(str(user.id))


@router.get("/jobs", response_model=list[SyncJobOut])
def list_jobs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return SyncSchedulerService(db).list_jobs(str(user.id))


@router.get("/jobs/{job_id}", response_model=SyncJobOut)
def get_job(job_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    job = SyncSchedulerService(db).get_job(str(user.id), job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
