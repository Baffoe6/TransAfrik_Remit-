import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import type { AppNotification } from "../api/notifications";

interface InboxState {
  items: AppNotification[];
  loaded: boolean;
  load: () => Promise<void>;
  push: (n: Omit<AppNotification, "id" | "read" | "created_at">) => Promise<void>;
  markRead: (id: string) => Promise<void>;
  markAllRead: () => Promise<void>;
  unreadCount: () => number;
}

const KEY = "notification_inbox";

export const useNotificationInboxStore = create<InboxState>((set, get) => ({
  items: [],
  loaded: false,
  load: async () => {
    const raw = await AsyncStorage.getItem(KEY);
    set({ items: raw ? JSON.parse(raw) : [], loaded: true });
  },
  push: async (n) => {
    const entry: AppNotification = {
      ...n,
      id: `notif_${Date.now()}`,
      read: false,
      created_at: new Date().toISOString(),
    };
    const next = [entry, ...get().items].slice(0, 50);
    await AsyncStorage.setItem(KEY, JSON.stringify(next));
    set({ items: next });
  },
  markRead: async (id) => {
    const next = get().items.map((i) => (i.id === id ? { ...i, read: true } : i));
    await AsyncStorage.setItem(KEY, JSON.stringify(next));
    set({ items: next });
  },
  markAllRead: async () => {
    const next = get().items.map((i) => ({ ...i, read: true }));
    await AsyncStorage.setItem(KEY, JSON.stringify(next));
    set({ items: next });
  },
  unreadCount: () => get().items.filter((i) => !i.read).length,
}));
