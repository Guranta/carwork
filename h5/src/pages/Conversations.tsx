import { type MouseEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createConversation, deleteConversation, listConversations } from "../api";
import { clearToken } from "../api/client";
import type { Conversation } from "../types";
import { clipTitle, formatTime } from "../utils";

export default function Conversations() {
  const navigate = useNavigate();
  const [items, setItems] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      setItems(await listConversations());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  const start = async () => {
    const created = await createConversation();
    navigate(`/chat/${created.id}`);
  };

  const logout = () => {
    clearToken();
    navigate("/login", { replace: true });
  };

  const remove = async (event: MouseEvent, id: number) => {
    event.stopPropagation();
    if (!confirm("删除这段对话？")) return;
    await deleteConversation(id);
    await load();
  };

  return (
    <main className="convo-page">
      <header className="topbar">
        <div>
          <span className="eyebrow">AGENT HISTORY</span>
          <h1>理赔助手</h1>
        </div>
        <button className="ghost-btn" onClick={logout}>退出</button>
      </header>

      <button className="new-chat" onClick={start}>
        <span>+</span>
        开始一次新咨询
      </button>

      <section className="list-panel">
        {loading ? (
          <div className="state-card">加载中...</div>
        ) : items.length === 0 ? (
          <div className="empty-card">
            <strong>还没有对话</strong>
            <p>可以问：我的车损能赔吗？附近修理厂有哪些？案件进度到哪了？</p>
          </div>
        ) : (
          items.map((item) => (
            <button key={item.id} className="convo-item" onClick={() => navigate(`/chat/${item.id}`)}>
              <div>
                <strong>{clipTitle(item.title || item.last_content)}</strong>
                <p>{item.last_content || "空白对话"}</p>
              </div>
              <aside>
                <span>{formatTime(item.last_message_at)}</span>
                <small>{item.message_count} 条</small>
                <button className="delete-btn" onClick={(event) => remove(event, item.id)}>删除</button>
              </aside>
            </button>
          ))
        )}
      </section>
    </main>
  );
}
