import { useState } from "react";
import MessageList from "./MessageList";
import Composer from "./Composer";
import { useChat } from "./useChat";
import type { Role } from "./types";
import { ROLE_LABELS } from "./types";
import "./chat.css";

const ROLES: Role[] = ["customer", "agent", "service"];

export default function ChatApp() {
  const [role, setRole] = useState<Role>("customer");
  const { messages, loading, send, reset } = useChat(role);

  return (
    <div className="chat-app">
      <header className="chat-header">
        <div className="title">
          车险理赔助手
          <span className="subtitle"> · {ROLE_LABELS[role]}模式</span>
        </div>
        <div className="role-switch">
          {ROLES.map((r) => (
            <button
              key={r}
              className={r === role ? "active" : ""}
              onClick={() => setRole(r)}
            >
              {ROLE_LABELS[r]}
            </button>
          ))}
        </div>
        <button className="icon-btn" onClick={reset} title="新对话" aria-label="新对话">
          ↻
        </button>
      </header>

      <MessageList messages={messages} role={role} onQuick={(t) => send({ text: t, images: [] })} />

      <Composer onSend={(text, images) => send({ text, images })} disabled={loading} />
    </div>
  );
}
