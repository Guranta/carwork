"""DeepSeek function-calling 主循环。

流程：system+history → 发 DeepSeek(带 tools) → 若返回 tool_calls 则逐个执行并把结果回填 → 再发，
直到模型给出无 tool_calls 的最终回答，或达到最大轮数。
"""

import json
import time
from typing import Any

from sqlalchemy.orm import Session

from app.ai.agent.prompts import build_system_prompt
from app.ai.agent.schemas import AGENT_TOOLS
from app.ai.agent.tools import ToolContext, call_tool
from app.ai.routing import AIRouter
from app.core.logging import log

MAX_STEPS = 8


async def run_agent(
    *,
    db: Session,
    router: AIRouter,
    role: str | None = None,
    messages: list[dict] | None = None,
    images: list[str] | None = None,
) -> dict[str, Any]:
    provider = router.pick_chat()
    tool_ctx = ToolContext(db=db, router=router, pending_images=list(images or []))

    convo: list[dict[str, Any]] = [{"role": "system", "content": build_system_prompt(role)}]
    for m in messages or []:
        r, c = m.get("role"), m.get("content")
        if r in ("user", "assistant") and c:
            convo.append({"role": r, "content": c})

    trace: list[dict[str, Any]] = []
    started = time.perf_counter()
    for step in range(MAX_STEPS):
        result = await provider.chat(convo, tools=AGENT_TOOLS, temperature=0.4, max_tokens=1500)
        if not result.tool_calls:
            log.info("agent.done", steps=step, tool_calls=len(trace), latency_ms=int((time.perf_counter() - started) * 1000))
            return {
                "answer": result.content or "",
                "tool_calls": trace,
                "model": result.model,
                "usage": result.usage,
            }

        # assistant 消息含 tool_calls，需原样(含 tool_calls)回传给模型
        convo.append(result.raw["choices"][0]["message"])
        for tc in result.tool_calls:
            fn = tc.get("function") or {}
            name = fn.get("name", "")
            raw_args = fn.get("arguments", "{}")
            try:
                args = json.loads(raw_args) if raw_args else {}
            except json.JSONDecodeError:
                args = {"_raw": raw_args}
            record = {"name": name, "args": args}
            trace.append(record)
            out = await call_tool(name, tool_ctx, args)
            record["result"] = out
            convo.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.get("id", ""),
                    "content": json.dumps(out, ensure_ascii=False),
                }
            )

    log.warning("agent.max_steps", tool_calls=len(trace))
    return {
        "answer": "抱歉，处理步骤过多未能完成，请稍后重试或转人工。",
        "tool_calls": trace,
        "model": provider.default_model,
        "usage": {},
    }
