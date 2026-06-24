from typing import Any

from app.ai.skills.base import Skill, register_skill

DOC_SCHEMAS: dict[str, dict[str, Any]] = {
    "driving_license": {
        "type": "object",
        "properties": {
            "plate_no": {"type": "string", "description": "号牌号码"},
            "vehicle_type": {"type": "string", "description": "车辆类型"},
            "owner": {"type": "string", "description": "所有人"},
            "address": {"type": "string"},
            "brand_model": {"type": "string", "description": "品牌型号"},
            "vin": {"type": "string", "description": "车辆识别代号"},
            "engine_no": {"type": "string", "description": "发动机号"},
            "register_date": {"type": "string"},
            "issue_date": {"type": "string"},
        },
        "required": ["plate_no", "vin"],
    },
    "driver_license": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "id_card": {"type": "string"},
            "license_no": {"type": "string", "description": "证号"},
            "vehicle_types": {"type": "string", "description": "准驾车型"},
            "valid_from": {"type": "string"},
            "valid_to": {"type": "string"},
        },
    },
    "invoice": {
        "type": "object",
        "properties": {
            "invoice_no": {"type": "string"},
            "invoice_date": {"type": "string"},
            "seller": {"type": "string"},
            "buyer": {"type": "string"},
            "amount": {"type": "number", "description": "金额"},
            "tax_amount": {"type": "number"},
            "total": {"type": "number"},
        },
    },
    "general": {
        "type": "object",
        "properties": {
            "fields": {"type": "object", "description": "识别到的键值对"},
        },
    },
}


@register_skill
class OCRExtractSkill(Skill):
    name = "ocr_extract"
    capability = "chat"

    async def run(
        self,
        *,
        ocr_text: str,
        doc_type: str = "general",
        prefer_provider: str | None = None,
    ) -> dict[str, Any]:
        schema = DOC_SCHEMAS.get(doc_type, DOC_SCHEMAS["general"])
        provider = self.ctx.router.pick_chat(prefer_provider)
        system = (
            "你是单证信息抽取助手。根据 OCR 文本抽取结构化字段，"
            "严格输出符合 Schema 的 JSON。缺失字段用空字符串，不要臆造。"
        )
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    f"单证类型: {doc_type}\n"
                    f"目标 Schema: {schema}\n\n"
                    f"OCR 文本:\n{ocr_text}\n\n请输出 JSON。"
                ),
            },
        ]
        result, parsed = await provider.chat_json(messages, temperature=0.0, max_tokens=1200)
        confidence = _confidence(parsed, schema)
        return {
            "provider": provider.name,
            "model": result.model,
            "extracted": parsed,
            "confidence": confidence,
            "usage": result.usage,
        }


def _confidence(parsed: dict[str, Any], schema: dict[str, Any]) -> float:
    props = schema.get("properties", {})
    if not props:
        return 0.5
    filled = sum(1 for v in parsed.values() if v not in (None, "", [], {}))
    return round(min(1.0, filled / max(1, len(props))), 2)
