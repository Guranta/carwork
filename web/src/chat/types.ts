export type Role = "customer" | "agent" | "service";

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
  result: unknown;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  images?: string[]; // user: 已上传图片 data URI(预览)
  toolCalls?: ToolCall[]; // assistant: 工具调用过程
  modelName?: string;
  ts: number;
  pending?: boolean; // assistant 等待中占位
  error?: boolean;
}

export const ROLE_LABELS: Record<Role, string> = {
  customer: "车主",
  agent: "代理人",
  service: "售后客服",
};
