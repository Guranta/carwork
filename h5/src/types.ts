export interface TokenOut {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  name: string;
  phone?: string | null;
  role: string;
  is_active: boolean;
}

export interface ToolCall {
  name: string;
  args: Record<string, unknown>;
  result?: unknown;
}

export interface Message {
  id: number | string;
  role: "user" | "assistant";
  content: string;
  images?: string[] | null;
  tool_calls?: ToolCall[] | null;
  model?: string | null;
  created_at: string;
  pending?: boolean;
  error?: boolean;
}

export interface Conversation {
  id: number;
  title?: string | null;
  role: string;
  last_message_at: string;
  created_at: string;
  message_count: number;
  last_content?: string | null;
}

export interface ConversationDetail {
  id: number;
  title?: string | null;
  role: string;
  last_message_at: string;
  created_at: string;
  messages: Message[];
}

export interface SendMessagePayload {
  text: string;
  images: string[];
}

export interface SendMessageResult {
  user_message: Message;
  assistant_message: Message;
}
