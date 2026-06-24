import { useCallback, useRef, useState } from "react";
import { getApiBase, genId, getToken } from "./utils";
import type { ChatMessage, Role } from "./types";

interface SendOpts {
  text: string;
  images: string[];
}

export function useChat(role: Role) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const send = useCallback(
    async ({ text, images }: SendOpts) => {
      const trimmed = text.trim();
      if (loading || (!trimmed && images.length === 0)) return;

      const userMsg: ChatMessage = {
        id: genId(),
        role: "user",
        content: trimmed,
        images: images.length ? images : undefined,
        ts: Date.now(),
      };
      // 发给后端的 history：之前消息 + 本轮；只保留 role/content
      const history = [...messages, userMsg].map((m) => ({
        role: m.role,
        content: m.content || (m.role === "user" ? "我上传了车辆损伤照片，请帮我识别并评估" : m.content),
      }));

      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);

      const placeholderId = genId();
      setMessages((prev) => [
        ...prev,
        { id: placeholderId, role: "assistant", content: "", pending: true, ts: Date.now() },
      ]);

      const ctrl = new AbortController();
      abortRef.current = ctrl;
      try {
        const resp = await fetch(`${getApiBase()}/agent/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
          },
          body: JSON.stringify({ messages: history, role, images }),
          signal: ctrl.signal,
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        setMessages((prev) =>
          prev.map((m) =>
            m.id === placeholderId
              ? {
                  ...m,
                  pending: false,
                  content: data.answer || "(无回复)",
                  toolCalls: data.tool_calls || [],
                  modelName: data.model,
                  ts: Date.now(),
                }
              : m,
          ),
        );
      } catch (e) {
        const aborted = e instanceof DOMException && e.name === "AbortError";
        setMessages((prev) =>
          prev.map((m) =>
            m.id === placeholderId
              ? {
                  ...m,
                  pending: false,
                  error: !aborted,
                  content: aborted ? "已取消" : "请求失败，请检查网络后重试",
                  ts: Date.now(),
                }
              : m,
          ),
        );
      } finally {
        setLoading(false);
        abortRef.current = null;
      }
    },
    [loading, messages, role],
  );

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setMessages([]);
  }, []);

  return { messages, loading, send, reset };
}
