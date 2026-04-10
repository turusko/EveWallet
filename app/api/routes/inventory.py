from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.phase3 import InventoryLotOut, InventoryMovementOut
from app.services.bucket_service import BucketService
from app.services.inventory_service import InventoryService

router = APIRouter(prefix='/inventory', tags=['inventory'])


@router.get('/lots', response_model=list[InventoryLotOut])
def list_lots(bucket_id: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return InventoryService(db).list_lots(bucket_id)


@router.get('/movements', response_model=list[InventoryMovementOut])
def list_movements(bucket_id: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return InventoryService(db).list_movements(bucket_id)


@router.get('/buckets/{bucket_id}')
def bucket_inventory(bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    bucket = BucketService(db).get(str(user.id), bucket_id)
    if not bucket:
        raise HTTPException(status_code=404, detail='Bucket not found')
    lots = InventoryService(db).list_lots(bucket_id)
    return {'bucket_id': bucket_id, 'item_count': len(lots), 'inventory_value': sum((l.quantity_remaining * l.unit_cost for l in lots), Decimal('0'))}


@router.post('/rebuild/{bucket_id}')
def rebuild(bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    bucket = BucketService(db).get(str(user.id), bucket_id)
    if not bucket:
        raise HTTPException(status_code=404, detail='Bucket not found')
    return {'status': 'noop', 'bucket_id': bucket_id}


@router.post('/reconcile-assets/{bucket_id}')
def reconcile_assets(bucket_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    bucket = BucketService(db).get(str(user.id), bucket_id)
    if not bucket:
        raise HTTPException(status_code=404, detail='Bucket not found')
    return InventoryService(db).reconcile_assets(bucket_id)
