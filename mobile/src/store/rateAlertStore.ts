import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";

export interface RateAlert {
  id: string;
  corridorCode: string;
  currency: string;
  targetRate: string;
  enabled: boolean;
  createdAt: string;
}

interface RateAlertState {
  alerts: RateAlert[];
  loaded: boolean;
  load: () => Promise<void>;
  addAlert: (corridorCode: string, currency: string, targetRate: string) => Promise<void>;
  toggleAlert: (id: string) => Promise<void>;
  removeAlert: (id: string) => Promise<void>;
}

const KEY = "rate_alerts";

export const useRateAlertStore = create<RateAlertState>((set, get) => ({
  alerts: [],
  loaded: false,
  load: async () => {
    const raw = await AsyncStorage.getItem(KEY);
    set({ alerts: raw ? JSON.parse(raw) : [], loaded: true });
  },
  addAlert: async (corridorCode, currency, targetRate) => {
    const entry: RateAlert = {
      id: `alert_${Date.now()}`,
      corridorCode,
      currency,
      targetRate,
      enabled: true,
      createdAt: new Date().toISOString(),
    };
    const next = [entry, ...get().alerts].slice(0, 5);
    await AsyncStorage.setItem(KEY, JSON.stringify(next));
    set({ alerts: next });
  },
  toggleAlert: async (id) => {
    const next = get().alerts.map((a) => (a.id === id ? { ...a, enabled: !a.enabled } : a));
    await AsyncStorage.setItem(KEY, JSON.stringify(next));
    set({ alerts: next });
  },
  removeAlert: async (id) => {
    const next = get().alerts.filter((a) => a.id !== id);
    await AsyncStorage.setItem(KEY, JSON.stringify(next));
    set({ alerts: next });
  },
}));
