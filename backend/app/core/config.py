from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_name: str = "carwork"
    app_debug: bool = True
    log_level: str = "INFO"
    secret_key: str = "dev-secret-change-me"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173"

    database_url: str = "postgresql+psycopg://carwork:carwork@localhost:5432/carwork"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "carwork"
    minio_secure: bool = False

    llm_default_provider: str = "deepseek"

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_chat_model: str = "deepseek-v4-flash"
    deepseek_reasoning_model: str = "deepseek-v4-pro"

    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dashscope_chat_model: str = "qwen-plus"
    dashscope_vl_model: str = "qwen-vl-max"

    glm_api_key: str = ""
    glm_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    glm_chat_model: str = "glm-4-flash"

    maas_api_key: str = ""
    maas_base_url: str = ""
    maas_chat_model: str = "minimax2.7"
    maas_vl_model: str = "qwen3-vl-plus"

    ocr_default_provider: str = "aliyun"
    aliyun_ocr_access_key: str = ""
    aliyun_ocr_secret_key: str = ""

    access_token_expire_minutes: int = 7 * 24 * 60

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
