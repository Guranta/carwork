from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IDMixin, TimestampMixin

try:
    from pgvector.sqlalchemy import Vector
except Exception:  # pragma: no cover - pgvector optional in some envs
    Vector = None  # type: ignore[assignment]


EMBED_DIM = 1024


class KnowledgeBase(Base, IDMixin, TimestampMixin):
    __tablename__ = "knowledge_base"

    name: Mapped[str] = mapped_column(String(128), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    doc_count: Mapped[int] = mapped_column(default=0)


class KnowledgeChunk(Base, IDMixin, TimestampMixin):
    __tablename__ = "knowledge_chunk"

    kb_id: Mapped[int] = mapped_column(ForeignKey("knowledge_base.id"), index=True)
    source: Mapped[str | None] = mapped_column(String(255))
    chunk_index: Mapped[int] = mapped_column(default=0)
    text: Mapped[str] = mapped_column(Text)
    meta: Mapped[dict | None] = mapped_column(JSONB, default=dict)

    if Vector is not None:
        embedding: Mapped[list[float]] = mapped_column(Vector(EMBED_DIM))
