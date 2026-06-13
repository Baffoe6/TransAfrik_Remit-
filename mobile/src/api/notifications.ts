import { apiClient } from "./client";

export interface AppNotification {
  id: string;
  type: "transfer" | "kyc" | "promo" | "security";
  title: string;
  body: string;
  read: boolean;
  created_at: string;
}

// TODO: Wire to backend push/in-app notification API when available
export const notificationsApi = {
  list: async (): Promise<AppNotification[]> => {
    try {
      // Placeholder — no customer notification endpoint yet
      return [];
    } catch {
      return [];
    }
  },
  markRead: async (_id: string) => {
    // TODO: POST /notifications/{id}/read
  },
};

export const corridorsApi = {
  // TODO: GET /corridors when public endpoint is available
  list: async () => null as null,
};
