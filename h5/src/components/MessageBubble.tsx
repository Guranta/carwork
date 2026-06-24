import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Message } from "../types";
import { formatTime } from "../utils";

export default function MessageBubble({ message }: { message: Message }) {
  const mine = message.role === "user";
  return (
    <article className={`message ${mine ? "mine" : "assistant"} ${message.pending ? "pending" : ""} ${message.error ? "error" : ""}`}>
      <div className="avatar">{mine ? "我" : "AI"}</div>
      <div className="bubble-wrap">
        {message.images?.length ? (
          <div className="sent-images">
            {message.images.map((src, index) => <img key={index} src={src} alt={`图片 ${index + 1}`} />)}
          </div>
        ) : null}
        <div className="bubble">
          {message.pending ? <span className="typing">正在分析...</span> : <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>}
        </div>
        {message.tool_calls?.length ? (
          <details className="tools">
            <summary>调用了 {message.tool_calls.length} 个工具</summary>
            {message.tool_calls.map((tool, index) => <code key={index}>{tool.name}</code>)}
          </details>
        ) : null}
        <div className="meta">{message.model ? `${message.model} · ` : ""}{formatTime(message.created_at)}</div>
      </div>
    </article>
  );
}
