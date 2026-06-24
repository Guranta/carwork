from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class Document(Base, IDMixin, TimestampMixin):
    __tablename__ = "document"

    type: Mapped[str] = mapped_column(String(32), index=True)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(128))
    size: Mapped[int | None] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(16), default="uploaded", index=True)
    extracted: Mapped[dict | None] = mapped_column(JSONB, default=dict)
    confidence: Mapped[float | None] = mapped_column()
    raw_text: Mapped[str | None] = mapped_column(Text)
    org_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("organization.id"))
    case_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("claim_case.id"))
    uploaded_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"))
