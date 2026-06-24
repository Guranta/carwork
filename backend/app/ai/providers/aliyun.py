"""阿里云 OCR 适配占位。

阿里云 OCR（如 RecognizeDrivingLicense / RecognizeInvoice）使用 ACS3 签名认证。
接入时建议安装官方 SDK：
    pip install alibabacloud_ocr_api20210707

然后在 recognize() 内完成如下流程：
    from alibabacloud_ocr_api20210707.client import Client
    from alibabacloud_tea_openapi import models as open_api_models
    ...
    config = open_api_models.Config(access_key_id=AK, access_key_secret=SK)
    config.endpoint = "ocr-api.cn-hangzhou.aliyuncs.com"
    client = Client(config)
    resp = client.recognize_driving_license(...)
    return OCRResult(text=..., raw=resp.body.to_map())

当前版本默认使用 VisionOCRProvider（见 vision_ocr.py）完成 OCR，无需额外密钥。
"""


from app.ai.providers.base import OCRResult


class AliyunOCRProvider:
    name = "aliyun-ocr"

    def __init__(self, access_key: str, secret_key: str) -> None:
        self.access_key = access_key
        self.secret_key = secret_key

    @property
    def available(self) -> bool:
        return bool(self.access_key and self.secret_key)

    async def recognize(self, image_bytes: bytes, *, ocr_type: str = "general") -> OCRResult:
        raise NotImplementedError(
            "阿里云 OCR 待接入：请安装官方 SDK 并在此完成调用。"
            "MVP 阶段可继续使用 VisionOCRProvider。"
        )
