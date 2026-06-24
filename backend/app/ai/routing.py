"""多供应商路由：按能力(chat / vision / ocr)选择供应商，支持降级熔断。

设计目标：
- 同一能力多家供应商，按优先级调用，失败自动降级到下一个；
- 所有供应商由配置驱动构建，无 key 的供应商自动跳过；
- 技能层只声明需要的能力，不关心具体供应商。
"""

from dataclasses import dataclass
from typing import Any

from app.ai.providers.openai_compat import OpenAICompatibleProvider
from app.ai.providers.vision_ocr import VisionOCRProvider
from app.core.config import settings
from app.core.logging import log


@dataclass
class ProviderBundle:
    chat: list[OpenAICompatibleProvider]
    vision: list[OpenAICompatibleProvider]
    ocr: list[Any]


def build_providers() -> ProviderBundle:
    chat: list[OpenAICompatibleProvider] = []
    vision: list[OpenAICompatibleProvider] = []
    ocr: list[Any] = []

    maas = OpenAICompatibleProvider(
        name="maas",
        api_key=settings.maas_api_key,
        base_url=settings.maas_base_url,
        default_model=settings.maas_chat_model,
    )
    maas_vision = OpenAICompatibleProvider(
        name="maas",
        api_key=settings.maas_api_key,
        base_url=settings.maas_base_url,
        default_model=settings.maas_vl_model,
    )
    if maas_vision.available:
        vision.append(maas_vision)
        ocr.append(VisionOCRProvider(maas_vision, settings.maas_vl_model))

    deepseek = OpenAICompatibleProvider(
        name="deepseek",
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        default_model=settings.deepseek_chat_model,
    )
    dashscope = OpenAICompatibleProvider(
        name="dashscope",
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
        default_model=settings.dashscope_chat_model,
    )
    glm = OpenAICompatibleProvider(
        name="glm",
        api_key=settings.glm_api_key,
        base_url=settings.glm_base_url,
        default_model=settings.glm_chat_model,
    )
    for p in (deepseek, dashscope, glm):
        if p.available:
            chat.append(p)
    # maas 作为 chat 兜底(主用途是视觉 qwen3-vl-plus)
    if maas.available:
        chat.append(maas)

    dashscope_vision = OpenAICompatibleProvider(
        name="dashscope",
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
        default_model=settings.dashscope_vl_model,
    )
    if dashscope_vision.available:
        vision.append(dashscope_vision)
        ocr.append(VisionOCRProvider(dashscope_vision, settings.dashscope_vl_model))

    bundle = ProviderBundle(chat=chat, vision=vision, ocr=ocr)
    _log_providers(bundle)
    return bundle


def _log_providers(bundle: ProviderBundle) -> None:
    if not bundle.chat:
        log.warning("ai.no_chat_provider", hint="请在 .env 配置 DEEPSEEK_API_KEY / DASHSCOPE_API_KEY / GLM_API_KEY")
    log.info(
        "ai.providers_ready",
        chat=[p.name for p in bundle.chat],
        vision=[p.name for p in bundle.vision],
        ocr=[type(p).__name__ for p in bundle.ocr],
    )


class AIRouter:
    def __init__(self, bundle: ProviderBundle) -> None:
        self.bundle = bundle

    def pick_chat(self, prefer: str | None = None) -> OpenAICompatibleProvider:
        return self._pick(self.bundle.chat, prefer)

    def pick_vision(self, prefer: str | None = None) -> OpenAICompatibleProvider:
        return self._pick(self.bundle.vision, prefer)

    def pick_ocr(self) -> Any:
        if not self.bundle.ocr:
            raise RuntimeError("无可用 OCR 供应商，请配置 VL 模型密钥")
        return self.bundle.ocr[0]

    @staticmethod
    def _pick(providers: list[OpenAICompatibleProvider], prefer: str | None) -> OpenAICompatibleProvider:
        if not providers:
            raise RuntimeError("无可用 LLM 供应商，请在 .env 配置至少一个 API Key")
        if prefer:
            for p in providers:
                if p.name == prefer:
                    return p
        return providers[0]


_bundle: ProviderBundle | None = None


def get_bundle() -> ProviderBundle:
    global _bundle
    if _bundle is None:
        _bundle = build_providers()
    return _bundle


def get_router() -> AIRouter:
    return AIRouter(get_bundle())
