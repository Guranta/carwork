import { api } from "./client";
import type { Conversation, ConversationDetail, SendMessagePayload, SendMessageResult, TokenOut, User } from "../types";

export const login = (account: string, password: string) =>
  api.post<unknown, TokenOut>("/auth/login", { account, password });

export const register = (name: string, phone: string, password: string) =>
  api.post<unknown, TokenOut>("/auth/register", { name, phone, password });

export const getMe = () => api.get<unknown, User>("/auth/me");

export const listConversations = () => api.get<unknown, Conversation[]>("/agent/conversations");

export const createConversation = () =>
  api.post<unknown, { id: number; title: string | null; role: string }>("/agent/conversations", { role: "customer" });

export const getConversation = (id: number) =>
  api.get<unknown, ConversationDetail>(`/agent/conversations/${id}`);

export const sendMessage = (id: number, payload: SendMessagePayload) =>
  api.post<unknown, SendMessageResult>(`/agent/conversations/${id}/messages`, payload);

export const renameConversation = (id: number, title: string) =>
  api.patch<unknown, Conversation>(`/agent/conversations/${id}`, { title });

export const deleteConversation = (id: number) => api.delete<unknown, void>(`/agent/conversations/${id}`);
