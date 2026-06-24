from typing import Any

from app.ai.skills.base import Skill, register_skill


@register_skill
class DamageAssessmentSkill(Skill):
    """视觉定损：识别车辆损伤部位/类型/程度，给出维修方案与估价。

    估价部分应接入工时标准 + 配件价格库做校准（见 rag/ 与 domains/aftermarket）。
    MVP 阶段先由模型基于通用知识给出参考价，并在结果中标注 confidence，
    低置信度结果由编排层转为人工复核。
    """

    name = "damage_assessment"
    capability = "vision"

    async def run(
        self,
        *,
        image_urls: list[str],
        vehicle_info: dict[str, Any] | None = None,
        prefer_provider: str | None = None,
    ) -> dict[str, Any]:
        if not image_urls:
            raise ValueError("至少提供一张损伤照片")
        provider = self.ctx.router.pick_vision(prefer_provider)
        model = provider.default_model

        vehicle_hint = f"车辆信息: {vehicle_info}\n" if vehicle_info else ""
        system = (
            "你是资深车险定损员。基于车辆损伤照片完成损伤识别与估价。"
            "严格输出 JSON：{\"damages\":[{\"part\":\"部位\",\"type\":\"划痕/凹陷/破损/更换\","
            "\"severity\":\"轻微/中度/重度\",\"repair\":\"钣金/喷漆/更换\",\"estimate\":金额}],"
            "\"summary\":\"概括\",\"total_estimate\":金额,\"confidence\":0-1}。金额为人民币元。"
        )
        content: list[dict[str, Any]] = [
            {"type": "text", "text": f"{vehicle_hint}请逐图分析损伤并输出 JSON。"},
            *[
                {"type": "image_url", "image_url": {"url": u}}
                for u in image_urls
            ],
        ]
        messages = [{"role": "system", "content": system}, {"role": "user", "content": content}]
        result, parsed = await provider.chat_json(messages, temperature=0.1, max_tokens=1500)
        parsed.setdefault("confidence", 0.6)
        return {
            "provider": provider.name,
            "model": model,
            "assessment": parsed,
            "usage": result.usage,
        }
