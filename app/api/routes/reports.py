from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.eve_character import EveCharacter
from app.schemas.report import BucketSummary
from app.services.bucket_service import BucketService
from app.services.report_service import ReportService
from app.services.report_service_phase3 import ReportServicePhase3

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


@router.get("/buckets/{bucket_id}/inventory")
def bucket_inventory_report(bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    bucket = BucketService(db).get(str(user.id), bucket_id)
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")
    p3 = ReportServicePhase3(db).bucket_profit(bucket_id)
    return {"bucket_id": bucket_id, "inventory_value_on_hand": p3.inventory_value_on_hand, "warnings": p3.warnings}


@router.get("/buckets/{bucket_id}/profit")
def bucket_profit_report(bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    bucket = BucketService(db).get(str(user.id), bucket_id)
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")
    return ReportServicePhase3(db).bucket_profit(bucket_id)


@router.get('/dashboard')
def dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    buckets = BucketService(db).list(str(user.id))
    svc = ReportServicePhase3(db)
    reports = [svc.bucket_profit(str(b.id)) for b in buckets]
    return {
        'linked_characters': len({str(c.id) for c in db.scalars(select(EveCharacter).where(EveCharacter.user_id == user.id))}),
        'active_buckets': len([b for b in buckets if b.status == 'active']),
        'top_profitable_buckets': sorted([{'bucket_id': r.bucket_id, 'profit': r.realised_net_profit} for r in reports], key=lambda x: x['profit'], reverse=True)[:5],
        'buckets_with_warnings': [r.bucket_id for r in reports if r.warnings],
        'inventory_total_by_bucket': [{'bucket_id': r.bucket_id, 'inventory': r.inventory_value_on_hand} for r in reports],
    }
