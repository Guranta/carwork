from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ORMBase


class ConversationCreateIn(BaseModel):
    role: str = "customer"
    title: str | None = None


class ConversationCreateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str | None = None
    role: str


class ConversationOut(ORMBase):
    id: int
    title: str | None = None
    role: str
    last_message_at: datetime
    created_at: datetime
    message_count: int = 0
    last_content: str | None = None


class MessageOut(ORMBase):
    id: int
    role: str
    content: str
    images: list | None = None
    tool_calls: list | None = None
    model: str | None = None
    created_at: datetime


class ConversationDetailOut(ORMBase):
    id: int
    title: str | None = None
    role: str
    last_message_at: datetime
    created_at: datetime
    messages: list[MessageOut] = []


class SendMessageIn(BaseModel):
    text: str = Field(default="", description="用户文本，可为空（仅图片时）")
    images: list[str] = Field(default_factory=list, description="车损图片 data URI 列表")


class SendMessageOut(BaseModel):
    """发送消息后返回：落库的用户消息 + assistant 回复"""
    model_config = ConfigDict(from_attributes=True)
    user_message: MessageOut
    assistant_message: MessageOut


class ConversationRenameIn(BaseModel):
    title: str
