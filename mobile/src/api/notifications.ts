import { apiClient } from "./client";

export interface AppNotification {
  id: number;
  notification_type: string;
  event_code: string;
  title: string;
  message: string;
  transfer_id: number | null;
  transfer_reference: string | null;
  read_status: "unread" | "read";
  created_at: string;
  read_at?: string | null;
}

export interface NotificationListResponse {
  items: AppNotification[];
  unread_count: number;
}

export const notificationsApi = {
  list: async (): Promise<NotificationListResponse> => {
    const { data } = await apiClient.get<NotificationListResponse>("/notifications");
    return data;
  },
  unreadCount: async (): Promise<number> => {
    const { data } = await apiClient.get<NotificationListResponse>("/notifications", { params: { limit: 1 } });
    return data.unread_count;
  },
  markRead: async (id: number) => {
    await apiClient.post(`/notifications/${id}/read`);
  },
  markAllRead: async () => {
    await apiClient.post("/notifications/read-all");
  },
  registerPushToken: async (pushToken: string, enabled = true) => {
    await apiClient.post("/notifications/push-token", {
      push_token: pushToken,
      push_notifications_enabled: enabled,
    });
  },
};

export const corridorsApi = {
  list: async () => null as null,
};
