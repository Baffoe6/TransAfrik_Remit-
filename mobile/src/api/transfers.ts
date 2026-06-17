import { apiClient } from "./client";
import type { Transfer, TransferDetail } from "../types";

export interface TransferQuote {
  amount_to_pay_zar?: string;
  fee_zar: string;
  exchange_rate: string;
  receive_amount_ghs: string;
  receive_amount?: string;
  total_amount_zar: string;
  from_currency?: string;
  to_currency?: string;
  corridor_code?: string;
  customer_rate?: string;
  delivery_method?: string;
  estimated_delivery?: string;
}

export const transfersApi = {
  list: () => apiClient.get<Transfer[]>("/transfers"),
  get: (id: number) => apiClient.get<TransferDetail>(`/transfers/${id}`),
  calculate: (amount_to_pay_zar: string, destination_country = "GH") =>
    apiClient.post<TransferQuote>("/transfers/calculate", { amount_to_pay_zar, destination_country }),
  create: (data: { beneficiary_id: number; amount_to_pay_zar: string; payment_method_code?: string }) =>
    apiClient.post<TransferDetail>("/transfers", data),
  timeline: async (id: number) => {
    const { data } = await apiClient.get<{ timeline?: { status: string; created_at: string; note?: string }[] } | { status: string; created_at: string; note?: string }[]>(`/transfers/${id}/timeline`);
    if (Array.isArray(data)) return data;
    return data.timeline ?? [];
  },
  uploadPaymentProof: (id: number, form: FormData) =>
    apiClient.post(`/transfers/${id}/payment-proof`, form, { headers: { "Content-Type": "multipart/form-data" } }),
  cancel: (id: number) => apiClient.post<TransferDetail>(`/transfers/${id}/cancel`),
  tracking: (id: number) => apiClient.get(`/transfers/${id}/tracking`),
};
