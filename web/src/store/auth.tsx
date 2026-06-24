import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getJSON, postJSON } from "../api/client";

export interface AuthUser {
  id: number;
  name: string;
  phone: string | null;
  role: string;
  is_active: boolean;
}

interface AuthCtx {
  user: AuthUser | null;
  loading: boolean;
  login: (account: string, password: string) => Promise<void>;
  logout: () => void;
}

const Ctx = createContext<AuthCtx>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("carwork_token");
    if (!token) {
      setLoading(false);
      return;
    }
    getJSON<AuthUser>("/auth/me")
      .then(setUser)
      .catch(() => localStorage.removeItem("carwork_token"))
      .finally(() => setLoading(false));
  }, []);

  const login = async (account: string, password: string) => {
    const { access_token } = await postJSON<{ access_token: string }>("/auth/login", {
      account,
      password,
    });
    localStorage.setItem("carwork_token", access_token);
    const me = await getJSON<AuthUser>("/auth/me");
    setUser(me);
  };

  const logout = () => {
    localStorage.removeItem("carwork_token");
    setUser(null);
  };

  return <Ctx.Provider value={{ user, loading, login, logout }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  return useContext(Ctx);
}
