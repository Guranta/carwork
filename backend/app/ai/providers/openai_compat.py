import json
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.ai.providers.base import LLMResult


class OpenAICompatibleProvider:
    """通用 OpenAI 兼容协议供应商（DeepSeek / 通义 DashScope / GLM / 豆包 等）。

    同时支持纯文本 chat 与多模态（视觉）消息：messages 中 content 项可为
    {"type": "text", "text": ...} 或 {"type": "image_url", "image_url": {"url": ...}}。
    """

    def __init__(
        self,
        name: str,
        api_key: str,
        base_url: str,
        default_model: str,
        timeout: float = 60.0,
    ) -> None:
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
    async def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        response_format: dict | None = None,
        tools: list[dict] | None = None,
        timeout: float | None = None,
    ) -> LLMResult:
        payload: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format is not None:
            payload["response_format"] = response_format
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=timeout or self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        message = choice["message"]
        content = message.get("content") or ""
        tool_calls = message.get("tool_calls") or []
        usage = data.get("usage", {})
        return LLMResult(
            content=content,
            model=payload["model"],
            usage=usage,
            raw=data,
            tool_calls=tool_calls,
        )

    async def chat_json(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int | None = None,
    ) -> tuple[LLMResult, dict[str, Any]]:
        messages = list(messages)
        if messages and messages[-1]["role"] == "user":
            last = messages[-1]
            content = last.get("content")
            json_hint = "\n\n请严格仅输出合法 JSON，不要包含 ``` 或额外说明。"
            if isinstance(content, str):
                new_content = content + json_hint
            elif isinstance(content, list):
                # 多模态（text + image_url）：把 JSON 指令作为一个 text 项追加，必须保留图片
                new_content = content + [{"type": "text", "text": json_hint}]
            else:
                new_content = json_hint
            messages[-1] = {**last, "content": new_content}
        result = await self.chat(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        parsed = _safe_json(result.content)
        return result, parsed


def _safe_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
    return {}
