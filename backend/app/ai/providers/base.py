from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class LLMResult:
    content: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)

    @property
    def prompt_tokens(self) -> int:
        return int(self.usage.get("prompt_tokens", 0))

    @property
    def completion_tokens(self) -> int:
        return int(self.usage.get("completion_tokens", 0))


@dataclass
class OCRResult:
    text: str
    raw: dict[str, Any] = field(default_factory=dict)


class LLMProvider(Protocol):
    name: str

    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        response_format: dict | None = None,
        tools: list[dict] | None = None,
        timeout: float = 60.0,
    ) -> LLMResult: ...

    async def chat_json(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int | None = None,
    ) -> tuple[LLMResult, dict[str, Any]]: ...


class OCRProvider(Protocol):
    name: str

    async def recognize(self, image_bytes: bytes, *, ocr_type: str = "general") -> OCRResult: ...
