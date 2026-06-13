import { create } from "zustand";
import { authApi } from "../api/auth";
import { secureStorage } from "../services/secureStorage";
import type { User } from "../types";

interface AuthState {
  user: User | null;
  loading: boolean;
  initialized: boolean;
  login: (identifier: string, password: string) => Promise<{ stepUp?: boolean; stepUpMobile?: string }>;
  loginOtp: (mobile: string, code: string) => Promise<void>;
  register: (data: {
    mobile_number: string;
    password: string;
    first_name: string;
    last_name: string;
    email?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  bootstrap: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,
  initialized: false,

  bootstrap: async () => {
    const token = await secureStorage.getAccessToken();
    // Show UI immediately after local token read — don't block on network.
    set({ initialized: true });
    if (!token) return;
    try {
      const { data } = await authApi.me();
      set({ user: data });
    } catch {
      await secureStorage.clearTokens();
      set({ user: null });
    }
  },

  login: async (identifier, password) => {
    set({ loading: true });
    try {
      const { data } = await authApi.login(identifier, password);
      if (data.step_up_required) {
        return { stepUp: true, stepUpMobile: data.step_up_mobile ?? undefined };
      }
      if (data.mfa_required) throw new Error("MFA required — use web admin portal");
      await secureStorage.setTokens(data.access_token!, data.refresh_token!);
      const { data: user } = await authApi.me();
      set({ user });
      return {};
    } finally {
      set({ loading: false });
    }
  },

  loginOtp: async (mobile, code) => {
    set({ loading: true });
    try {
      const { data } = await authApi.loginOtp(mobile, code);
      await secureStorage.setTokens(data.access_token!, data.refresh_token!);
      const { data: user } = await authApi.me();
      set({ user });
    } finally {
      set({ loading: false });
    }
  },

  register: async (payload) => {
    set({ loading: true });
    try {
      const { data } = await authApi.register(payload);
      await secureStorage.setTokens(data.access_token!, data.refresh_token!);
      const { data: user } = await authApi.me();
      set({ user });
    } finally {
      set({ loading: false });
    }
  },

  logout: async () => {
    const refresh = await secureStorage.getRefreshToken();
    if (refresh) {
      try {
        await authApi.logout(refresh);
      } catch {
        /* ignore */
      }
    }
    await secureStorage.clearTokens();
    set({ user: null });
  },

  refreshUser: async () => {
    const { data } = await authApi.me();
    set({ user: data });
  },
}));
