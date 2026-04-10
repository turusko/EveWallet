from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
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
        raise HTTPException(status_code=404, detail="Bucket not found")
    return ReportService(db).bucket_summary(bucket_id)


@router.get("/buckets", response_model=list[BucketSummary])
def all_bucket_summaries(db: Session = Depends(get_db), user=Depends(get_current_user)):
    buckets = BucketService(db).list(str(user.id))
    svc = ReportService(db)
    return [svc.bucket_summary(str(b.id)) for b in buckets]


@router.get("/buckets/{bucket_id}/export.csv")
def bucket_export(bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    bucket = BucketService(db).get(str(user.id), bucket_id)
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")
    csv_text = ReportService(db).export_bucket_csv(bucket_id)
    return Response(content=csv_text, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=bucket-{bucket_id}.csv"})


@router.get("/buckets/export.csv")
def all_buckets_export(db: Session = Depends(get_db), user=Depends(get_current_user)):
    csv_text = ReportService(db).export_all_buckets_csv(str(user.id))
    return Response(content=csv_text, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=buckets.csv"})
