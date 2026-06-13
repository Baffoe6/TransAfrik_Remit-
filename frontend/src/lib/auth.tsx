"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "./api";
import { getDeviceId, getDeviceLabel } from "./device";

export interface User {
  id: number;
  mobile_number: string | null;
  email: string | null;
  first_name: string | null;
  last_name: string | null;
  role: string;
  status: string;
  email_verified: boolean;
  phone_verified: boolean;
}

interface TokenResponse {
  access_token: string | null;
  refresh_token: string | null;
  mfa_required?: boolean;
  step_up_required?: boolean;
  step_up_mobile?: string;
  risk_score?: number;
  risk_level?: string;
}

interface OtpSendResponse {
  sent: boolean;
  channel: string;
  message: string;
  dev_code?: string;
}

interface LoginResult {
  user: User | null;
  mfaRequired: boolean;
  stepUpRequired: boolean;
  stepUpMobile?: string;
  riskScore?: number;
  riskLevel?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (identifier: string, password: string, mfaCode?: string) => Promise<LoginResult>;
  loginWithOtp: (mobile: string, code: string) => Promise<LoginResult>;
  completeStepUp: (mobile: string, code: string) => Promise<LoginResult>;
  sendOtp: (mobile: string, channel: "sms" | "whatsapp", purpose: "login" | "verify_phone" | "step_up") => Promise<OtpSendResponse>;
  verifyPhoneOtp: (code: string) => Promise<void>;
  register: (data: RegisterData) => Promise<User>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

interface RegisterData {
  mobile_number: string;
  password: string;
  first_name: string;
  last_name: string;
  email?: string;
  invite_code?: string;
}

const AuthContext = createContext<AuthContextType | null>(null);

function devicePayload() {
  return { device_id: getDeviceId(), device_label: getDeviceLabel() };
}

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

  const storeTokens = async (tokens: TokenResponse): Promise<User> => {
    localStorage.setItem("access_token", tokens.access_token!);
    localStorage.setItem("refresh_token", tokens.refresh_token!);
    const me = await api<User>("/auth/me");
    setUser(me);
    return me;
  };

  const login = async (identifier: string, password: string, mfaCode?: string): Promise<LoginResult> => {
    const tokens = await api<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ identifier, password, mfa_code: mfaCode, ...devicePayload() }),
    });
    if (tokens.mfa_required) {
      return { user: null, mfaRequired: true, stepUpRequired: false };
    }
    if (tokens.step_up_required) {
      return {
        user: null,
        mfaRequired: false,
        stepUpRequired: true,
        stepUpMobile: tokens.step_up_mobile ?? undefined,
        riskScore: tokens.risk_score,
        riskLevel: tokens.risk_level,
      };
    }
    const me = await storeTokens(tokens);
    return { user: me, mfaRequired: false, stepUpRequired: false, riskScore: tokens.risk_score };
  };

  const sendOtp = async (mobile: string, channel: "sms" | "whatsapp", purpose: "login" | "verify_phone" | "step_up") => {
    return api<OtpSendResponse>("/auth/otp/send", {
      method: "POST",
      body: JSON.stringify({ mobile_number: mobile, channel, purpose }),
    });
  };

  const loginWithOtp = async (mobile: string, code: string): Promise<LoginResult> => {
    const tokens = await api<TokenResponse>("/auth/login/otp", {
      method: "POST",
      body: JSON.stringify({ mobile_number: mobile, code, trust_device: true, ...devicePayload() }),
    });
    const me = await storeTokens(tokens);
    return { user: me, mfaRequired: false, stepUpRequired: false };
  };

  const completeStepUp = async (mobile: string, code: string): Promise<LoginResult> => {
    const tokens = await api<TokenResponse>("/auth/login/step-up", {
      method: "POST",
      body: JSON.stringify({ mobile_number: mobile, code, trust_device: true, ...devicePayload() }),
    });
    const me = await storeTokens(tokens);
    return { user: me, mfaRequired: false, stepUpRequired: false };
  };

  const verifyPhoneOtp = async (code: string) => {
    await api("/auth/otp/verify-phone", {
      method: "POST",
      body: JSON.stringify({ code }),
    });
    await refreshUser();
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
    <AuthContext.Provider value={{
      user, loading, login, loginWithOtp, completeStepUp, sendOtp, verifyPhoneOtp, register, logout, refreshUser,
    }}>
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
