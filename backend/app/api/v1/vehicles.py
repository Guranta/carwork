from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import current_user
from app.db.session import get_db
from app.models import User
from app.platform.vehicles.service import VehicleService
from app.schemas.common import VehicleIn, VehicleOut

router = APIRouter(prefix="/vehicles", tags=["vehicle"])


@router.post("", response_model=VehicleOut)
def create_vehicle(payload: VehicleIn, db: Session = Depends(get_db), _: User = Depends(current_user)) -> VehicleOut:
    v = VehicleService(db).get_or_create(payload.vin, brand=payload.brand, model=payload.model, year=payload.year, color=payload.color, plate_no=payload.plate_no)
    return VehicleOut.model_validate(v)


@router.get("", response_model=list[VehicleOut])
def list_vehicles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
) -> list[VehicleOut]:
    rows, _ = VehicleService(db).list(page, page_size)
    return [VehicleOut.model_validate(r) for r in rows]
