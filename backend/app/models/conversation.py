from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.account import User


class Conversation(Base, IDMixin, TimestampMixin):
    __tablename__ = "conversation"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(16), default="customer")
    last_message_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship("User")
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.id",
    )


class Message(Base, IDMixin, TimestampMixin):
    __tablename__ = "message"

    conversation_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("conversation.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # user / assistant
    content: Mapped[str] = mapped_column(Text, default="")
    images: Mapped[list | None] = mapped_column(JSONB, default=list)  # 用户消息: data URI 列表
    tool_calls: Mapped[list | None] = mapped_column(JSONB, default=list)  # assistant: 工具过程
    model: Mapped[str | None] = mapped_column(String(128))

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
