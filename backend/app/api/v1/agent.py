from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai.orchestrator import Orchestrator
from app.core.deps import current_user, optional_user
from app.db.session import get_db
from app.models import Conversation, Message, User
from app.schemas.conversation import (
    ConversationCreateIn,
    ConversationCreateOut,
    ConversationDetailOut,
    ConversationOut,
    ConversationRenameIn,
    MessageOut,
    SendMessageIn,
    SendMessageOut,
)

router = APIRouter(prefix="/agent", tags=["agent"])


# --------------------------------------------------------------------------- #
# 无状态对话（保留：匿名可用，前端传全量 history）
# --------------------------------------------------------------------------- #
class AgentChatIn(BaseModel):
    # [{role: "user"|"assistant", content: str}] 最近的对话；最后一条通常是本轮用户输入
    messages: list[dict]
    # 角色轻调: customer(车主) / agent(代理人) / service(售后客服)
    role: str = "customer"
    # 本轮新上传的车辆损伤图片(data URI)，由前端本地转 base64 生成，后端直接转发给 VL 模型
    images: list[str] | None = None


class AgentChatOut(BaseModel):
    answer: str
    tool_calls: list[dict] = []
    model: str | None = None


@router.post("/chat", response_model=AgentChatOut)
async def agent_chat(
    payload: AgentChatIn,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_user),
) -> AgentChatOut:
    """对话 Agent：多轮对话 + function calling + 可带车损图片。C 端无需登录即可使用。"""
    result = await Orchestrator(db).invoke_agent(
        role=payload.role,
        messages=payload.messages,
        images=payload.images,
        ref_type="agent_chat",
        ref_id=user.id if user else None,
    )
    return AgentChatOut(
        answer=result["answer"],
        tool_calls=result.get("tool_calls", []),
        model=result.get("model"),
    )


# --------------------------------------------------------------------------- #
# 持久化对话（需登录，历史落库可回看）
# --------------------------------------------------------------------------- #
def _get_owned_conversation(db: Session, conv_id: int, user: User) -> Conversation:
    conv = db.get(Conversation, conv_id)
    if conv is None or conv.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "会话不存在")
    return conv


def _conv_to_out(conv: Conversation) -> ConversationOut:
    msgs = conv.messages or []
    return ConversationOut(
        id=conv.id,
        title=conv.title,
        role=conv.role,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        message_count=len(msgs),
        last_content=msgs[-1].content if msgs else None,
    )


@router.post("/conversations", response_model=ConversationCreateOut)
def create_conversation(
    payload: ConversationCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> ConversationCreateOut:
    """新建一个会话。"""
    conv = Conversation(user_id=user.id, role=payload.role or "customer", title=payload.title)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return ConversationCreateOut(id=conv.id, title=conv.title, role=conv.role)


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[ConversationOut]:
    """当前用户的会话列表（按最近活跃倒序）。"""
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.last_message_at.desc())
        .limit(100)
        .all()
    )
    return [_conv_to_out(c) for c in convs]


@router.get("/conversations/{conv_id}", response_model=ConversationDetailOut)
def get_conversation(
    conv_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> ConversationDetailOut:
    """会话详情 + 全部消息。"""
    conv = _get_owned_conversation(db, conv_id, user)
    return ConversationDetailOut(
        id=conv.id,
        title=conv.title,
        role=conv.role,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        messages=[MessageOut.model_validate(m) for m in (conv.messages or [])],
    )


@router.patch("/conversations/{conv_id}", response_model=ConversationOut)
def rename_conversation(
    conv_id: int,
    payload: ConversationRenameIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> ConversationOut:
    conv = _get_owned_conversation(db, conv_id, user)
    conv.title = payload.title.strip()[:128] or None
    db.commit()
    db.refresh(conv)
    return _conv_to_out(conv)


@router.delete("/conversations/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conv_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> None:
    conv = _get_owned_conversation(db, conv_id, user)
    db.delete(conv)
    db.commit()


@router.post("/conversations/{conv_id}/messages", response_model=SendMessageOut)
async def send_message(
    conv_id: int,
    payload: SendMessageIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> SendMessageOut:
    """发送一条消息：落库用户消息 → 拼历史调 Agent → 落库 assistant 回复 → 返回。"""
    conv = _get_owned_conversation(db, conv_id, user)

    text = payload.text.strip()
    images = payload.images or []
    if not text and not images:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "消息内容不能为空")

    now = datetime.now(UTC)

    # 1) 落库用户消息
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=text or "（上传了车辆损伤照片）",
        images=images if images else None,
    )
    db.add(user_msg)
    conv.last_message_at = now
    # 首条消息自动生成标题
    if not conv.title and text:
        conv.title = text[:32]
    db.commit()
    db.refresh(user_msg)
    db.refresh(conv)

    # 2) 从 DB 拼历史（含本轮用户消息），喂给 Agent
    history = [
        {"role": m.role, "content": m.content}
        for m in (conv.messages or [])
        if m.role in ("user", "assistant") and m.content
    ]

    # 3) 调用 Agent（本轮图片直接传，供 assess_damage 工具使用）
    result = await Orchestrator(db).invoke_agent(
        role=conv.role,
        messages=history,
        images=images,
        ref_type="agent_conversation",
        ref_id=conv.id,
    )

    # 4) 落库 assistant 回复
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=result.get("answer") or "(无回复)",
        tool_calls=result.get("tool_calls") or None,
        model=result.get("model"),
    )
    db.add(assistant_msg)
    conv.last_message_at = datetime.now(UTC)
    db.commit()
    db.refresh(assistant_msg)

    return SendMessageOut(
        user_message=MessageOut.model_validate(user_msg),
        assistant_message=MessageOut.model_validate(assistant_msg),
    )
