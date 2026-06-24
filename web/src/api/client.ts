import axios, { type AxiosError, type AxiosInstance } from "axios";
import { App, message } from "antd";

const TOKEN_KEY = "carwork_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export const api: AxiosInstance = axios.create({
  baseURL: "/api/v1",
  timeout: 60000,
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (resp) => resp,
  (error: AxiosError<{ detail?: string }>) => {
    const status = error.response?.status;
    const detail = error.response?.data?.detail || error.message;
    if (status === 401) {
      clearToken();
      if (location.pathname !== "/login") {
        message.error("登录已过期，请重新登录");
        location.href = "/login";
      }
    } else if (status && status >= 400) {
      message.error(typeof detail === "string" ? detail : "请求失败");
    }
    return Promise.reject(error);
  }
);

export async function getJSON<T = unknown>(url: string, params?: object): Promise<T> {
  const { data } = await api.get<T>(url, { params });
  return data;
}

export async function postJSON<T = unknown>(url: string, body?: unknown): Promise<T> {
  const { data } = await api.post<T>(url, body);
  return data;
}

export { App };
