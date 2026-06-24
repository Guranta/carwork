"""AI 编排层入口：技能调度 + 全链路日志 + 错误处理。

统一入口，业务域只通过 orchestrator.invoke(skill, **params) 调用 AI，
不直接接触供应商。所有调用落库 ai_call_log 便于成本/质量分析与复核闭环。
"""

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy.orm import Session

from app.ai.routing import get_router
from app.ai.skills import base as skill_base
from app.ai.skills.base import SkillContext
from app.core.logging import log


class Orchestrator:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.router = get_router()

    async def invoke(self, skill: str, *, ref_type: str | None = None, ref_id: int | None = None, **params: Any) -> dict[str, Any]:
        ctx = SkillContext(router=self.router)
        handler = skill_base.get_skill(skill, ctx)
        started = time.perf_counter()
        log.info("ai.invoke_start", skill=skill, ref_type=ref_type, ref_id=ref_id)
        try:
            result = await handler.run(**params)
        except Exception as exc:
            latency = int((time.perf_counter() - started) * 1000)
            self._log(
                skill, ref_type, ref_id,
                status="failed", latency_ms=latency, error=str(exc),
                request=params,
            )
            log.error("ai.invoke_failed", skill=skill, error=str(exc))
            raise

        latency = int((time.perf_counter() - started) * 1000)
        self._log(
            skill, ref_type, ref_id,
            status="success",
            latency_ms=latency,
            provider=result.get("provider"),
            model=result.get("model"),
            usage=result.get("usage"),
            confidence=result.get("confidence") or (result.get("assessment", {}) or {}).get("confidence"),
            request=params,
            response=result,
        )
        log.info("ai.invoke_done", skill=skill, latency_ms=latency, provider=result.get("provider"))
        return result

    def _log(
        self,
        skill: str,
        ref_type: str | None,
        ref_id: int | None,
        *,
        status: str,
        latency_ms: int,
        provider: str | None = None,
        model: str | None = None,
        usage: dict[str, int] | None = None,
        confidence: float | None = None,
        request: dict[str, Any] | None = None,
        response: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        from app.models import AICallLog

        entry = AICallLog(
            skill=skill,
            provider=provider or "n/a",
            model=model,
            capability=None,
            prompt_tokens=(usage or {}).get("prompt_tokens") if usage else None,
            completion_tokens=(usage or {}).get("completion_tokens") if usage else None,
            latency_ms=latency_ms,
            confidence=confidence,
            status=status,
            ref_type=ref_type,
            ref_id=ref_id,
            request=request,
            response=response,
            error=error,
        )
        try:
            self.db.add(entry)
            self.db.commit()
        except Exception as exc:  # noqa: BLE001
            self.db.rollback()
            log.warning("ai.log_persist_failed", error=str(exc))


    async def invoke_agent(
        self,
        *,
        role: str | None = None,
        messages: list[dict] | None = None,
        images: list[str] | None = None,
        ref_type: str | None = None,
        ref_id: int | None = None,
    ) -> dict[str, Any]:
        """对话 Agent 入口(走 function-calling)，复用 ai_call_log 记录。"""
        from app.ai.agent.loop import run_agent

        request = {"role": role, "messages": messages, "image_count": len(images or [])}
        started = time.perf_counter()
        try:
            result = await run_agent(
                db=self.db, router=self.router, role=role, messages=messages, images=images
            )
        except Exception as exc:
            latency = int((time.perf_counter() - started) * 1000)
            self._log(
                "agent", ref_type, ref_id,
                status="failed", latency_ms=latency, error=str(exc), request=request,
            )
            log.error("ai.invoke_failed", skill="agent", error=str(exc))
            raise

        latency = int((time.perf_counter() - started) * 1000)
        usage = result.get("usage") or {}
        self._log(
            "agent", ref_type, ref_id,
            status="success",
            latency_ms=latency,
            provider=self.router.pick_chat().name,
            model=result.get("model"),
            usage=usage,
            request=request,
            response={"answer": result.get("answer"), "tool_calls": result.get("tool_calls")},
        )
        log.info("ai.invoke_done", skill="agent", latency_ms=latency)
        return result


@contextmanager
def orchestrator_scope(db: Session) -> Generator[Orchestrator, None, None]:
    yield Orchestrator(db)
