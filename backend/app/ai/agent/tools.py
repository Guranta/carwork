"""Agent 工具实现。

每个工具是一个 async 函数：接收 ToolContext + 关键字参数，返回 dict。
loop 会把 dict 序列化为 JSON 回填给 LLM 的 tool 消息。
工具职责单一、可独立测试；调用顺序由 LLM 编排。
"""

import math
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.ai.routing import AIRouter
from app.data import load_price_catalog
from app.models import ClaimCase, Policy, RepairShop


@dataclass
class ToolContext:
    db: Session
    router: AIRouter
    # 最近一条用户消息携带的图片(data URI)。assess_damage 从这里取，LLM 不接触。
    pending_images: list[str] = field(default_factory=list)


async def query_policy(
    ctx: ToolContext,
    *,
    policy_no: str | None = None,
    plate_no: str | None = None,
    vin: str | None = None,
) -> dict[str, Any]:
    """按保单号/车牌/车架号查询保单条款(险种、免赔额、赔付比例、保额)。"""
    q = ctx.db.query(Policy).filter(Policy.active.is_(True))
    if policy_no:
        q = q.filter(Policy.policy_no == policy_no)
    elif plate_no:
        q = q.filter(Policy.plate_no == plate_no)
    elif vin:
        q = q.filter(Policy.vin == vin)
    else:
        return {"error": "请至少提供 policy_no / plate_no / vin 之一"}
    p = q.first()
    if p is None:
        return {"found": False, "hint": "未找到在保保单，请确认信息或引导用户补充"}
    coverages = p.coverage_types or []
    return {
        "found": True,
        "policy_no": p.policy_no,
        "insured_name": p.insured_name,
        "plate_no": p.plate_no,
        "insurance_company": p.insurance_company,
        "coverage_types": coverages,
        "has_damage_coverage": "车辆损失险" in coverages,
        "has_compulsory": "交强险" in coverages,
        "deductible": float(p.deductible),
        "payout_ratio": float(p.payout_ratio),
        "sum_insured": float(p.sum_insured) if p.sum_insured is not None else None,
        "effective_from": p.effective_from,
        "effective_to": p.effective_to,
    }


async def query_claim_status(ctx: ToolContext, *, case_no: str) -> dict[str, Any]:
    """按案件编号查询理赔案件当前阶段与进度。"""
    if not case_no:
        return {"error": "请提供 case_no"}
    c = ctx.db.query(ClaimCase).filter(ClaimCase.case_no == case_no).first()
    if c is None:
        return {"found": False, "hint": "未找到该案件"}
    return {
        "found": True,
        "case_no": c.case_no,
        "status": c.status,
        "stage": c.stage,
        "estimated_amount": float(c.estimated_amount) if c.estimated_amount is not None else None,
        "settled_amount": float(c.settled_amount) if c.settled_amount is not None else None,
        "incident_location": c.incident_location,
        "description": c.description,
    }


async def search_repair_shop(
    ctx: ToolContext,
    *,
    lat: float,
    lng: float,
    top_n: int = 3,
    city: str | None = None,
) -> dict[str, Any]:
    """按经纬度查找最近的合作修理厂(按直线距离排序)。"""
    q = ctx.db.query(RepairShop).filter(RepairShop.is_partner.is_(True))
    if city:
        q = q.filter(RepairShop.city == city)
    rows = [s for s in q.all() if s.lat is not None and s.lng is not None]
    if not rows:
        return {"shops": [], "hint": "该区域暂无合作修理厂"}
    scored = [(_haversine_km(lat, lng, float(s.lat), float(s.lng)), s) for s in rows]
    scored.sort(key=lambda x: x[0])
    top = scored[: max(1, min(int(top_n or 3), 10))]
    return {
        "shops": [
            {
                "name": s.name,
                "address": s.address,
                "phone": s.phone,
                "city": s.city,
                "distance_km": round(d, 2),
                "labor_rate": float(s.labor_rate) if s.labor_rate is not None else None,
                "rating": float(s.rating) if s.rating is not None else None,
                "brands": s.brands or [],
            }
            for d, s in top
        ]
    }


async def estimate_cost(ctx: ToolContext, *, damages: list[dict]) -> dict[str, Any]:
    """按损伤清单(部位+维修方式)估算自费维修价(工时+配件)。用于报"自费价"。"""
    if not damages:
        return {"error": "请提供 damages 损伤清单"}
    catalog = load_price_catalog().get("items", [])
    items: list[dict[str, Any]] = []
    total = 0.0
    for d in damages:
        part = (d.get("part") or "").strip()
        repair = (d.get("repair") or "").strip()
        m = _match_price(catalog, part, repair)
        if m:
            subtotal = int(m["labor"]) + int(m["parts"])
            total += subtotal
            items.append(
                {
                    "part": part or m["part"],
                    "repair": m["repair"],
                    "labor": m["labor"],
                    "parts": m["parts"],
                    "subtotal": subtotal,
                }
            )
        else:
            items.append(
                {"part": part, "repair": repair, "found": False, "hint": "价格表未覆盖，建议门店实报"}
            )
    return {"items": items, "total_self_pay": int(total), "currency": "CNY"}


async def assess_damage(ctx: ToolContext, *, focus: str | None = None) -> dict[str, Any]:
    """识别用户上传的车辆损伤照片: 部位/损伤类型/程度/建议维修方式。依赖最近上传的图片。"""
    images = ctx.pending_images
    if not images:
        return {"error": "用户尚未上传车辆损伤照片，请引导用户拍照上传"}
    provider = ctx.router.pick_vision()
    focus_hint = f"重点关注: {focus}\n" if focus else ""
    system = (
        "你是资深车险定损员。基于车辆损伤照片识别损伤。"
        "严格输出 JSON: {\"damages\":[{\"part\":\"部位\",\"type\":\"划痕/凹陷/破损/裂痕等\","
        "\"severity\":\"轻微/中度/重度\",\"repair\":\"喷漆/钣金/更换\"}],"
        "\"summary\":\"概括\",\"confidence\":0-1}。"
        "repair 字段必须取值: 喷漆、钣金、更换 三者之一。"
    )
    content: list[dict[str, Any]] = [
        {"type": "text", "text": f"{focus_hint}请逐图分析损伤并输出 JSON。"}
    ]
    content += [{"type": "image_url", "image_url": {"url": u}} for u in images]
    messages = [{"role": "system", "content": system}, {"role": "user", "content": content}]
    result, parsed = await provider.chat_json(messages, temperature=0.1, max_tokens=1500)
    parsed.setdefault("confidence", 0.6)
    return {"assessment": parsed, "model": provider.default_model}


# ---- 工具注册表 ----
TOOLS: dict[str, Any] = {
    "query_policy": query_policy,
    "query_claim_status": query_claim_status,
    "search_repair_shop": search_repair_shop,
    "estimate_cost": estimate_cost,
    "assess_damage": assess_damage,
}


async def call_tool(name: str, ctx: ToolContext, args: dict) -> dict[str, Any]:
    fn = TOOLS.get(name)
    if fn is None:
        return {"error": f"未知工具 {name}"}
    try:
        return await fn(ctx, **(args or {}))
    except TypeError as exc:
        return {"error": f"参数错误: {exc}"}


# ---- helpers ----
def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _match_price(catalog: list[dict], part: str, repair: str) -> dict | None:
    """部位+维修方式 模糊匹配价格表。"""
    # 1) 部位 + 维修方式 都命中
    for it in catalog:
        if part and part in it["part"] and repair and (repair in it["repair"] or it["repair"] in repair):
            return it
    # 2) 仅部位命中(取第一条)
    for it in catalog:
        if part and part in it["part"]:
            return it
    # 3) 仅维修方式命中
    for it in catalog:
        if repair and (repair in it["repair"] or it["repair"] in repair):
            return it
    return None
