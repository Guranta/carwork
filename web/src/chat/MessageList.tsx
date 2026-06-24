import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage, Role } from "./types";
import { TOOL_LABELS } from "./utils";

const QUICK_QUESTIONS: Record<Role, { icon: string; q: string }[]> = {
  customer: [
    { icon: "📸", q: "我的车前保险杠剐蹭了，帮我看看修一下多少钱、保险能报多少" },
    { icon: "📍", q: "我在上海徐家汇，车坏了，附近有什么合作修理厂？" },
    { icon: "📋", q: "京A12345 的保单还在生效吗？都有什么险种？" },
  ],
  agent: [
    { icon: "💰", q: "沪B88888 客户出险，车损喷漆，走保险 vs 自费怎么沟通？" },
    { icon: "🗂️", q: "帮我梳理一起理赔案件需要哪些材料" },
  ],
  service: [
    { icon: "🚨", q: "客户报案流程是什么？需要引导客户提供哪些信息？" },
    { icon: "📦", q: "理赔案件 CL20260625XXXX 现在到哪个阶段了？" },
  ],
};

function summarize(name: string, result: unknown): string {
  const r = result as Record<string, unknown> | undefined;
  if (!r) return "";
  if (typeof r === "object" && r && "error" in r) return String(r.error);
  switch (name) {
    case "query_policy":
      return (r as any).found
        ? `${(r as any).insurance_company} · 车损险:${(r as any).has_damage_coverage ? "有" : "无"} · 免赔¥${(r as any).deductible}`
        : "未找到保单";
    case "query_claim_status":
      return (r as any).found ? `阶段:${(r as any).stage} / 状态:${(r as any).status}` : "未找到案件";
    case "search_repair_shop":
      return `找到 ${((r as any).shops || []).length} 家合作店`;
    case "estimate_cost":
      return `自费合计 ¥${(r as any).total_self_pay ?? "?"}`;
    case "assess_damage": {
      const a = ((r as any).assessment || {}) as any;
      return `识别损伤 ${(a.damages || []).length} 处`;
    }
    default:
      return "";
  }
}

function MessageItem({ m, onImage }: { m: ChatMessage; onImage: (url: string) => void }) {
  return (
    <div className={`msg-row ${m.role} ${m.error ? "error" : ""}`}>
      <div className="msg-avatar">{m.role === "user" ? "我" : "🤖"}</div>
      <div className="msg-bubble">
        {m.images && m.images.length > 0 && (
          <div className="msg-images">
            {m.images.map((src, i) => (
              <img key={i} src={src} alt={`上传图片${i + 1}`} onClick={() => onImage(src)} />
            ))}
          </div>
        )}
        {m.pending ? (
          <div className="typing">
            <span />
            <span />
            <span />
          </div>
        ) : m.role === "assistant" ? (
          <>
            {m.toolCalls && m.toolCalls.length > 0 && (
              <div className="tool-group">
                {m.toolCalls.map((tc, i) => (
                  <div className="tool-chip" key={i}>
                    <span className="dot" />
                    <span className="name">{TOOL_LABELS[tc.name] || tc.name}</span>
                    <span className="summary">{summarize(tc.name, tc.result)}</span>
                  </div>
                ))}
              </div>
            )}
            <div className="md-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
            </div>
            {m.modelName && <div className="model-tag">{m.modelName}</div>}
          </>
        ) : (
          <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>
        )}
      </div>
    </div>
  );
}

export default function MessageList({
  messages,
  role,
  onQuick,
}: {
  messages: ChatMessage[];
  role: Role;
  onQuick: (text: string) => void;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [lightbox, setLightbox] = useState<string | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="chat-messages">
        <div className="welcome">
          <div className="big">🚗</div>
          <h3>车险理赔 · 智能助手</h3>
          <div>拍照上传车损，帮你识别损伤、估算费用、查保单报销、推荐附近修理厂</div>
          <div className="quick">
            {QUICK_QUESTIONS[role].map((q, i) => (
              <button key={i} onClick={() => onQuick(q.q)}>
                {q.icon} {q.q}
              </button>
            ))}
          </div>
        </div>
        {lightbox && (
          <div className="img-overlay" onClick={() => setLightbox(null)}>
            <img src={lightbox} alt="预览" />
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="chat-messages">
      {messages.map((m) => (
        <MessageItem key={m.id} m={m} onImage={setLightbox} />
      ))}
      <div ref={bottomRef} />
      {lightbox && (
        <div className="img-overlay" onClick={() => setLightbox(null)}>
          <img src={lightbox} alt="预览" />
        </div>
      )}
    </div>
  );
}
