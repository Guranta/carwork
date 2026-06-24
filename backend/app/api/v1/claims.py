import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.orchestrator import Orchestrator
from app.core.deps import current_user
from app.db.session import get_db
from app.models import ClaimCase, ServiceOrder, User
from app.platform.vehicles.service import VehicleService
from app.schemas.common import ClaimCaseIn, ClaimCaseOut, DamageAssessmentIn

router = APIRouter(prefix="/claims", tags=["claim"])


def _new_case_no() -> str:
    return f"CL{time.strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


def _new_order_no() -> str:
    return f"SO{time.strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


@router.post("", response_model=ClaimCaseOut)
def create_case(payload: ClaimCaseIn, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ClaimCaseOut:
    vehicle = VehicleService(db).get_or_create(payload.vin)
    case = ClaimCase(
        case_no=_new_case_no(),
        insurance_policy_no=payload.insurance_policy_no,
        insurance_company=payload.insurance_company,
        vehicle_id=vehicle.id,
        claimant_user_id=user.id,
        incident_at=payload.incident_at,
        incident_location=payload.incident_location,
        description=payload.description,
        status="reported",
        stage="report",
    )
    db.add(case)
    db.flush()

    order = ServiceOrder(
        order_no=_new_order_no(),
        vehicle_id=vehicle.id,
        claim_case_id=case.id,
        fault_desc=payload.description,
        status="created",
    )
    db.add(order)
    db.commit()
    db.refresh(case)

    out = ClaimCaseOut.model_validate(case)
    out.service_order_no = order.order_no
    return out


@router.get("", response_model=list[ClaimCaseOut])
def list_cases(db: Session = Depends(get_db), _: User = Depends(current_user)) -> list[ClaimCaseOut]:
    rows = db.query(ClaimCase).order_by(ClaimCase.id.desc()).limit(50).all()
    return [ClaimCaseOut.model_validate(r) for r in rows]


@router.get("/{case_id}", response_model=ClaimCaseOut)
def get_case(case_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)) -> ClaimCaseOut:
    case = db.get(ClaimCase, case_id)
    if case is None:
        raise HTTPException(404, "案件不存在")
    return ClaimCaseOut.model_validate(case)


@router.post("/{case_id}/assess-damage")
async def assess_damage(
    case_id: int,
    payload: DamageAssessmentIn,
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
) -> dict:
    case = db.get(ClaimCase, case_id)
    if case is None:
        raise HTTPException(404, "案件不存在")
    result = await Orchestrator(db).invoke(
        "damage_assessment",
        ref_type="claim_case",
        ref_id=case.id,
        image_urls=payload.image_urls,
        vehicle_info={"brand": case.extra.get("brand")} if case.extra else None,
    )
    assessment = result["assessment"]
    case.loss_assessment = assessment
    case.estimated_amount = assessment.get("total_estimate")
    case.stage = "assessment"
    db.commit()
    return {"case_id": case.id, "assessment": assessment}
