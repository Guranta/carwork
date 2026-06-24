import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.orchestrator import Orchestrator
from app.core.deps import current_user
from app.db.session import get_db
from app.models import ServiceOrder, User
from app.platform.vehicles.service import VehicleService
from app.schemas.common import ServiceOrderIn, ServiceOrderOut

router = APIRouter(prefix="/aftermarket", tags=["aftermarket"])


def _new_order_no() -> str:
    return f"SO{time.strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


class PartsMatchIn(BaseModel):
    query: str
    vin: str | None = None


@router.post("/orders", response_model=ServiceOrderOut)
def create_order(payload: ServiceOrderIn, db: Session = Depends(get_db), user: User = Depends(current_user)) -> ServiceOrderOut:
    vehicle_id = None
    if payload.vin:
        vehicle_id = VehicleService(db).get_or_create(payload.vin).id
    order = ServiceOrder(
        order_no=_new_order_no(),
        vehicle_id=vehicle_id,
        fault_desc=payload.fault_desc,
        items=payload.items,
        status="created",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return ServiceOrderOut.model_validate(order)


@router.get("/orders", response_model=list[ServiceOrderOut])
def list_orders(db: Session = Depends(get_db), _: User = Depends(current_user)) -> list[ServiceOrderOut]:
    rows = db.query(ServiceOrder).order_by(ServiceOrder.id.desc()).limit(50).all()
    return [ServiceOrderOut.model_validate(r) for r in rows]


@router.get("/orders/{order_id}", response_model=ServiceOrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)) -> ServiceOrderOut:
    order = db.get(ServiceOrder, order_id)
    if order is None:
        raise HTTPException(404, "工单不存在")
    return ServiceOrderOut.model_validate(order)


@router.post("/parts/match")
async def match_parts(payload: PartsMatchIn, db: Session = Depends(get_db), _: User = Depends(current_user)) -> dict:
    """配件匹配：VIN -> OE 件号 -> 替换件号推荐（MVP 走 LLM，后续接配件知识库 RAG）。"""
    context = [f"VIN: {payload.vin}"] if payload.vin else []
    result = await Orchestrator(db).invoke(
        "chat",
        ref_type="parts_match",
        query=payload.query,
        context_docs=context,
        system_prompt=(
            "你是汽车配件专家。根据描述匹配配件，给出原厂 OE 件号方向与可替换品牌件建议。"
            "输出 JSON: {\"parts\":[{\"name\":名称,\"oe_hint\":件号方向,\"alternatives\":[品牌件]}],\"notes\":\"\"}."
        ),
    )
    return {"answer": result["answer"], "provider": result["provider"]}


@router.post("/assistant")
async def assistant_chat(payload: dict, db: Session = Depends(get_db), _: User = Depends(current_user)) -> dict:
    """导修/技师辅助问答。"""
    query = payload.get("query", "")
    history = payload.get("history")
    result = await Orchestrator(db).invoke("chat", ref_type="assistant", query=query, history=history)
    return {"answer": result["answer"], "provider": result["provider"], "model": result.get("model")}
