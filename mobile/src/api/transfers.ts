import { apiClient } from "./client";
import type { Transfer, TransferDetail } from "../types";

export const transfersApi = {
  list: () => apiClient.get<Transfer[]>("/transfers"),
  get: (id: number) => apiClient.get<TransferDetail>(`/transfers/${id}`),
  calculate: (send_amount_zar: string) =>
    apiClient.post("/transfers/calculate", { send_amount_zar }),
  create: (data: Record<string, unknown>) => apiClient.post<TransferDetail>("/transfers", data),
  timeline: (id: number) => apiClient.get(`/transfers/${id}/timeline`),
  tracking: (id: number) => apiClient.get(`/transfers/${id}/tracking`),
};
