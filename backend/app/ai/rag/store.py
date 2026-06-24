"""轻量 RAG：文本切块 -> 向量嵌入 -> pgvector 相似检索。

嵌入默认走 DashScope text-embedding-v3（OpenAI 兼容 embeddings 端点）。
知识库用于：保险条款、维修手册、配件目录、故障案例 等。
"""

from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.knowledge import EMBED_DIM, KnowledgeBase, KnowledgeChunk


class RAGStore:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not settings.dashscope_api_key:
            raise RuntimeError("未配置 DASHSCOPE_API_KEY，无法生成嵌入向量")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{settings.dashscope_base_url}/embeddings",
                headers={"Authorization": f"Bearer {settings.dashscope_api_key}"},
                json={"model": "text-embedding-v3", "input": texts, "dimensions": EMBED_DIM},
            )
            resp.raise_for_status()
            data = resp.json()
        return [d["embedding"] for d in sorted(data["data"], key=lambda x: x["index"])]

    def ensure_kb(self, name: str, description: str | None = None) -> KnowledgeBase:
        kb = self.db.execute(select(KnowledgeBase).where(KnowledgeBase.name == name)).scalar_one_or_none()
        if kb is None:
            kb = KnowledgeBase(name=name, description=description)
            self.db.add(kb)
            self.db.flush()
        return kb

    async def upsert(self, kb_name: str, texts: list[str], source: str | None = None) -> int:
        kb = self.ensure_kb(kb_name)
        embeddings = await self.embed(texts)
        for i, (text, vec) in enumerate(zip(texts, embeddings, strict=True)):
            self.db.add(
                KnowledgeChunk(kb_id=kb.id, source=source, chunk_index=i, text=text, embedding=vec)
            )
        kb.doc_count = (kb.doc_count or 0) + len(texts)
        self.db.commit()
        return len(texts)

    async def search(self, kb_name: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        kb = self.db.execute(select(KnowledgeBase).where(KnowledgeBase.name == kb_name)).scalar_one_or_none()
        if kb is None:
            return []
        q_vec = (await self.embed([query]))[0]
        stmt = (
            select(KnowledgeChunk, KnowledgeChunk.embedding.cosine_distance(q_vec).label("dist"))
            .where(KnowledgeChunk.kb_id == kb.id)
            .order_by("dist")
            .limit(top_k)
        )
        rows = self.db.execute(stmt).all()
        return [{"text": chunk.text, "source": chunk.source, "score": round(1 - dist, 4)} for chunk, dist in rows]
