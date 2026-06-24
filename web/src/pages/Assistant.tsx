import { useRef, useState } from "react";
import { PageContainer } from "@ant-design/pro-components";
import { Avatar, Input, Button, Space, Spin, Typography } from "antd";
import { RobotOutlined, UserOutlined, SendOutlined } from "@ant-design/icons";
import { postJSON } from "../api/client";

interface Msg {
  role: "user" | "assistant";
  content: string;
}

export default function Assistant() {
  const [messages, setMessages] = useState<Msg[]>([
    { role: "assistant", content: "你好，我是车后市场与保险理赔助手。可询问车辆故障、维修方案、配件匹配、理赔政策等。" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setLoading(true);
    try {
      const { answer } = await postJSON<{ answer: string }>("/aftermarket/assistant", {
        query: text,
        history,
      });
      setMessages((prev) => [...prev, { role: "assistant", content: answer }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "（调用失败，请检查后端是否配置 LLM Key）" }]);
    } finally {
      setLoading(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  };

  return (
    <PageContainer header={{ title: "智能助手", breadcrumb: {} }}>
      <div
        style={{
          maxWidth: 760,
          margin: "0 auto",
          background: "#fff",
          borderRadius: 8,
          padding: 16,
          minHeight: 520,
          display: "flex",
          flexDirection: "column",
          border: "1px solid #f0f0f0",
        }}
      >
        <div style={{ flex: 1, overflow: "auto" }}>
          {messages.map((m, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                flexDirection: m.role === "user" ? "row-reverse" : "row",
                gap: 8,
                marginBottom: 16,
              }}
            >
              <Avatar icon={m.role === "user" ? <UserOutlined /> : <RobotOutlined />} style={{ backgroundColor: m.role === "user" ? "#1677ff" : "#52c41a" }} />
              <div
                style={{
                  background: m.role === "user" ? "#e6f4ff" : "#f6ffed",
                  padding: "8px 12px",
                  borderRadius: 8,
                  maxWidth: 560,
                  whiteSpace: "pre-wrap",
                }}
              >
                <Typography.Text>{m.content}</Typography.Text>
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: "flex", gap: 8 }}>
              <Avatar icon={<RobotOutlined />} style={{ backgroundColor: "#52c41a" }} />
              <Spin size="small" style={{ marginTop: 10 }} />
            </div>
          )}
          <div ref={bottomRef} />
        </div>
        <Space.Compact style={{ marginTop: 12 }}>
          <Input
            placeholder="输入问题…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onPressEnter={send}
          />
          <Button type="primary" icon={<SendOutlined />} onClick={send} loading={loading}>
            发送
          </Button>
        </Space.Compact>
      </div>
    </PageContainer>
  );
}
