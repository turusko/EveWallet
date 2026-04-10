from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.bucket import AssignmentRequest, BucketCreate, BucketOut, BucketUpdate
from app.services.bucket_service import BucketService

router = APIRouter(prefix="/buckets", tags=["buckets"])


@router.post("", response_model=BucketOut)
def create_bucket(payload: BucketCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return BucketService(db).create(str(user.id), payload)


@router.get("", response_model=list[BucketOut])
def list_buckets(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return BucketService(db).list(str(user.id))


@router.get("/{bucket_id}", response_model=BucketOut)
def get_bucket(bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    bucket = BucketService(db).get(str(user.id), bucket_id)
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")
    return bucket


@router.patch("/{bucket_id}", response_model=BucketOut)
def update_bucket(bucket_id: str, payload: BucketUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return BucketService(db).update(str(user.id), bucket_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{bucket_id}/archive", response_model=BucketOut)
def archive_bucket(bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return BucketService(db).archive(str(user.id), bucket_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{bucket_id}/assign")
def assign_bucket(bucket_id: str, payload: AssignmentRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        count = BucketService(db).assign(str(user.id), bucket_id, payload.items, note=payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"assigned": count}


@router.post("/{bucket_id}/unassign")
def unassign_bucket(bucket_id: str, payload: AssignmentRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        count = BucketService(db).unassign(str(user.id), bucket_id, payload.items)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"unassigned": count}
