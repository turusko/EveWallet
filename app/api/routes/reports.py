from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.report import BucketSummary
from app.services.bucket_service import BucketService
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/buckets/{bucket_id}/summary", response_model=BucketSummary)
def bucket_summary(bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    bucket = BucketService(db).get(str(user.id), bucket_id)
    if not bucket:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Bucket not found")
    return ReportService(db).bucket_summary(bucket_id)


@router.get("/buckets", response_model=list[BucketSummary])
def all_bucket_summaries(db: Session = Depends(get_db), user=Depends(get_current_user)):
    buckets = BucketService(db).list(str(user.id))
    svc = ReportService(db)
    return [svc.bucket_summary(str(b.id)) for b in buckets]
