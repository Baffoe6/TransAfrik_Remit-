import { apiClient } from "./client";
import type { Transfer, TransferDetail } from "../types";

export interface TransferQuote {
  send_amount_zar: string;
  fee_zar: string;
  exchange_rate: string;
  receive_amount_ghs: string;
  total_amount_zar: string;
  from_currency?: string;
  to_currency?: string;
}

export const transfersApi = {
  list: () => apiClient.get<Transfer[]>("/transfers"),
  get: (id: number) => apiClient.get<TransferDetail>(`/transfers/${id}`),
  calculate: (send_amount_zar: string, destination_country = "GH") =>
    apiClient.post<TransferQuote>("/transfers/calculate", { send_amount_zar, destination_country }),
  create: (data: { beneficiary_id: number; send_amount_zar: string; payment_method_code?: string }) =>
    apiClient.post<TransferDetail>("/transfers", data),
  timeline: (id: number) => apiClient.get<{ status: string; created_at: string; note?: string }[]>(`/transfers/${id}/timeline`),
  tracking: (id: number) => apiClient.get(`/transfers/${id}/tracking`),
};
