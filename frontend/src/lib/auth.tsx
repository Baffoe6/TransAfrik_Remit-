"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "./api";

export interface User {
  id: number;
  email: string;
  phone: string | null;
  role: string;
  email_verified: boolean;
  phone_verified: boolean;
}

interface TokenResponse {
  access_token: string | null;
  refresh_token: string | null;
  mfa_required?: boolean;
}

interface LoginResult {
  user: User | null;
  mfaRequired: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string, mfaCode?: string) => Promise<LoginResult>;
  register: (data: RegisterData) => Promise<User>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  phone?: string;
  first_name: string;
  last_name: string;
  invite_code?: string;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await api<User>("/auth/me");
      setUser(me);
    } catch {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (email: string, password: string, mfaCode?: string): Promise<LoginResult> => {
    const tokens = await api<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password, mfa_code: mfaCode }),
    });
    if (tokens.mfa_required) {
      return { user: null, mfaRequired: true };
    }
    localStorage.setItem("access_token", tokens.access_token!);
    localStorage.setItem("refresh_token", tokens.refresh_token!);
    const me = await api<User>("/auth/me");
    setUser(me);
    return { user: me, mfaRequired: false };
  };

  const register = async (data: RegisterData) => {
    const tokens = await api<{ access_token: string; refresh_token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    const me = await api<User>("/auth/me");
    setUser(me);
    return me;
  };

  const logout = async () => {
    const refresh = localStorage.getItem("refresh_token");
    if (refresh) {
      try {
        await api("/auth/logout", { method: "POST", body: JSON.stringify({ refresh_token: refresh }) });
      } catch {
        /* ignore */
      }
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function isStaff(role: string) {
  return role === "admin" || role === "compliance_officer" || role === "founder";
}

export function isAgent(role: string) {
  return role === "agent";
}

export function getHomeForRole(role: string) {
  if (role === "agent") return "/agent";
  if (isStaff(role)) return role === "founder" ? "/admin/founder" : "/admin";
  return "/dashboard";
}
