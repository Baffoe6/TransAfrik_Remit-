import { apiClient } from "./client";

export interface SupportTicket {
  id: number;
  subject: string;
  message: string;
  status: string;
  priority: string;
  created_at: string;
  updated_at: string;
}

export const supportApi = {
  listTickets: () => apiClient.get<SupportTicket[]>("/support/tickets"),
  createTicket: (data: { subject: string; message: string; priority?: string; transfer_id?: number }) =>
    apiClient.post<SupportTicket>("/support/tickets", data),
};
