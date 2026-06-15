import AsyncStorage from "@react-native-async-storage/async-storage";
import { apiClient } from "./client";

export interface AppNotification {
  id: string;
  type: "transfer" | "kyc" | "promo" | "security" | "rate";
  title: string;
  body: string;
  read: boolean;
  created_at: string;
}

const INBOX_KEY = "notification_inbox";

async function loadLocalInbox(): Promise<AppNotification[]> {
  const raw = await AsyncStorage.getItem(INBOX_KEY);
  return raw ? JSON.parse(raw) : [];
}

// Local inbox + seed demo notifications until backend API ships
export const notificationsApi = {
  list: async (): Promise<AppNotification[]> => {
    const items = await loadLocalInbox();
    if (items.length) return items;
    const seeded: AppNotification[] = [
      { id: "seed_1", type: "rate", title: "Rate alert", body: "ZA→Ghana rate improved — send now to lock in", read: false, created_at: new Date().toISOString() },
      { id: "seed_2", type: "promo", title: "Refer & earn R50", body: "Invite a friend and both get R50 off your next transfer", read: false, created_at: new Date(Date.now() - 86400000).toISOString() },
    ];
    await AsyncStorage.setItem(INBOX_KEY, JSON.stringify(seeded));
    return seeded;
  },
  markRead: async (id: string) => {
    const items = await loadLocalInbox();
    const next = items.map((i) => (i.id === id ? { ...i, read: true } : i));
    await AsyncStorage.setItem(INBOX_KEY, JSON.stringify(next));
  },
  markAllRead: async () => {
    const items = await loadLocalInbox();
    const next = items.map((i) => ({ ...i, read: true }));
    await AsyncStorage.setItem(INBOX_KEY, JSON.stringify(next));
  },
};

export const corridorsApi = {
  list: async () => null as null,
};
