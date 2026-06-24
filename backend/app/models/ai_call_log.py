from sqlalchemy import Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IDMixin, TimestampMixin


class AICallLog(Base, IDMixin, TimestampMixin):
    __tablename__ = "ai_call_log"

    skill: Mapped[str] = mapped_column(String(64), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    model: Mapped[str | None] = mapped_column(String(128))
    capability: Mapped[str | None] = mapped_column(String(32))

    prompt_tokens: Mapped[int | None] = mapped_column()
    completion_tokens: Mapped[int | None] = mapped_column()
    cost: Mapped[float | None] = mapped_column()
    latency_ms: Mapped[int | None] = mapped_column()
    confidence: Mapped[float | None] = mapped_column(Float)

    status: Mapped[str] = mapped_column(String(16), default="success", index=True)
    ref_type: Mapped[str | None] = mapped_column(String(32))
    ref_id: Mapped[int | None] = mapped_column()

    request: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    response: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    error: Mapped[str | None] = mapped_column(Text)
