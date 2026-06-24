import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getConversation, renameConversation, sendMessage } from "../api";
import Composer from "../components/Composer";
import MessageBubble from "../components/MessageBubble";
import type { ConversationDetail, Message } from "../types";
import { genId } from "../utils";

const QUICK = [
  "我车牌沪B88888，能赔本车损吗？",
  "我上传车损照片，请帮我识别并估价",
  "帮我找上海附近合作修理厂",
  "理赔需要准备哪些材料？",
];

export default function Chat() {
  const { id } = useParams();
  const navigate = useNavigate();
  const convId = Number(id);
  const [detail, setDetail] = useState<ConversationDetail | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const title = useMemo(() => detail?.title || "新理赔咨询", [detail]);

  useEffect(() => {
    if (!Number.isFinite(convId)) return;
    getConversation(convId)
      .then((data) => { setDetail(data); setMessages(data.messages); })
      .catch(() => navigate("/", { replace: true }))
      .finally(() => setLoading(false));
  }, [convId, navigate]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  const send = async (text: string, images: string[]) => {
    if (sending) return;
    setSending(true);
    const now = new Date().toISOString();
    const pendingId = genId();
    setMessages((prev) => [
      ...prev,
      { id: genId(), role: "user", content: text || "（上传了车辆损伤照片）", images, created_at: now },
      { id: pendingId, role: "assistant", content: "", created_at: now, pending: true },
    ]);
    try {
      const result = await sendMessage(convId, { text, images });
      setMessages((prev) => [...prev.filter((m) => m.id !== pendingId), result.assistant_message]);
      if (!detail?.title && text) {
        const nextTitle = text.slice(0, 32);
        setDetail((prev) => prev ? { ...prev, title: nextTitle } : prev);
        void renameConversation(convId, nextTitle).catch(() => {});
      }
    } catch {
      setMessages((prev) => prev.map((m) => m.id === pendingId ? { ...m, pending: false, error: true, content: "请求失败，请检查网络或稍后再试。" } : m));
    } finally {
      setSending(false);
    }
  };

  return (
    <main className="chat-page">
      <header className="chat-topbar">
        <Link to="/" className="back-link">‹</Link>
        <div>
          <h1>{title}</h1>
          <p>车主模式 · 可查保单/进度/修理厂/识损估价</p>
        </div>
      </header>

      <section className="messages">
        {loading ? <div className="state-card">加载历史...</div> : messages.length === 0 ? (
          <div className="welcome-card">
            <span>AI CLAIM AGENT</span>
            <h2>把理赔问题说清楚，剩下交给我。</h2>
            <p>支持上传车损照片，也可以直接提供保单号、车牌号、案件号或当前位置。</p>
            <div className="quick-grid">
              {QUICK.map((item) => <button key={item} onClick={() => void send(item, [])}>{item}</button>)}
            </div>
          </div>
        ) : messages.map((message) => <MessageBubble key={message.id} message={message} />)}
        <div ref={bottomRef} />
      </section>

      <Composer disabled={sending || loading} onSend={send} />
    </main>
  );
}
