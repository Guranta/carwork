from dataclasses import dataclass
from typing import Any, ClassVar

from app.ai.routing import AIRouter


@dataclass
class SkillContext:
    router: AIRouter
    trace: dict[str, Any] | None = None


class Skill:
    name: ClassVar[str] = "base"
    capability: ClassVar[str] = "chat"

    def __init__(self, ctx: SkillContext) -> None:
        self.ctx = ctx

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


_REGISTRY: dict[str, type[Skill]] = {}


def register_skill(cls: type[Skill]) -> type[Skill]:
    _REGISTRY[cls.name] = cls
    return cls


def get_skill(name: str, ctx: SkillContext) -> Skill:
    if name not in _REGISTRY:
        raise KeyError(f"未知技能: {name}，已注册: {list(_REGISTRY)}")
    return _REGISTRY[name](ctx)


def list_skills() -> list[str]:
    return list(_REGISTRY)
