from typing import Any

from app.ai.agent.prompts import OUTPUT_STYLE
from app.ai.skills.base import Skill, register_skill


@register_skill
class ChatSkill(Skill):
    """通用问答/导修客服技能。可选接入 RAG 知识库（手册、条款、故障库）。"""

    name = "chat"
    capability = "chat"

    async def run(
        self,
        *,
        query: str,
        history: list[dict[str, str]] | None = None,
        context_docs: list[str] | None = None,
        system_prompt: str | None = None,
        prefer_provider: str | None = None,
    ) -> dict[str, Any]:
        provider = self.ctx.router.pick_chat(prefer_provider)
        system = system_prompt or (
            "你是车后市场与保险理赔助手，回答车辆故障、维修方案、配件匹配、理赔政策等问题。\n\n"
            + OUTPUT_STYLE
        )
        if context_docs:
            system += "\n\n参考资料:\n" + "\n---\n".join(context_docs[:5])

        messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": query})

        result = await provider.chat(messages, temperature=0.3, max_tokens=1500)
        return {
            "provider": provider.name,
            "model": result.model,
            "answer": result.content,
            "usage": result.usage,
        }
