
from app.ai.providers.base import OCRResult
from app.ai.providers.openai_compat import OpenAICompatibleProvider


class VisionOCRProvider:
    """基于多模态视觉大模型的 OCR（无需额外密钥，复用 LLM VL 模型）。

    适用于行驶证/驾驶证/保单/发票等单证。对结构化抽取要求高的场景，
    可切换到阿里云/腾讯云专用 OCR（见 aliyun.py）以获得更高准确率。
    """

    name = "vision-ocr"

    def __init__(self, llm: OpenAICompatibleProvider, vl_model: str) -> None:
        self.llm = llm
        self.vl_model = vl_model

    @property
    def available(self) -> bool:
        return self.llm.available

    async def recognize(self, image_bytes: bytes, *, ocr_type: str = "general") -> OCRResult:
        import base64

        b64 = base64.b64encode(image_bytes).decode("ascii")
        data_url = f"data:image/jpeg;base64,{b64}"

        instruction = {
            "general": "识别图片中的全部文字，按阅读顺序输出纯文本。",
            "id_card": "识别证件（身份证/行驶证/驾驶证）信息，输出纯文本，保留字段标签。",
            "invoice": "识别发票/票据信息，保留金额、日期、号码等关键字段。",
        }.get(ocr_type, "识别图片中的全部文字。")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ]
        result = await self.llm.chat(messages, model=self.vl_model, temperature=0.0, max_tokens=2000)
        return OCRResult(text=result.content, raw={"model": result.model, **result.usage})
