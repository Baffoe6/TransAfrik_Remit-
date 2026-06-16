import { apiClient } from "./client";

export interface PaymentMethod {
  id: number;
  name: string;
  code: string;
  provider: string;
  description: string | null;
  requires_proof_upload: boolean;
  is_instant: boolean;
  is_active: boolean;
}

export interface PaymentReference {
  id: number;
  transfer_id: number;
  provider: string;
  reference_number: string;
  voucher_number: string | null;
  barcode_data: string | null;
  qr_data: string | null;
  amount: string;
  currency: string;
  expiry_date: string | null;
  status: string;
  banking_instructions: Record<string, unknown> | null;
  provider_metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface FlutterwaveSession {
  payment_url: string;
  session_ref: string;
  provider: string;
  status: string;
  expires_at?: string;
}

export interface PaymentStatus {
  transfer_id: number;
  status: string;
  payment_status: string;
  reference_number?: string;
}

export const paymentsApi = {
  methods: () => apiClient.get<PaymentMethod[]>("/payments/methods"),
  generate: (transferId: number, payment_method_code: string) =>
    apiClient.post<PaymentReference>(`/payments/transfers/${transferId}/generate`, { payment_method_code }),
  getReference: (transferId: number) =>
    apiClient.get<PaymentReference | null>(`/payments/transfers/${transferId}/reference`),
  voucherPdfUrl: (transferId: number) => `${apiClient.defaults.baseURL}/payments/transfers/${transferId}/voucher.pdf`,
  flutterwaveSession: (transferId: number) =>
    apiClient.post<FlutterwaveSession>(`/payments/transfers/${transferId}/flutterwave/session`),
  paymentStatus: (transferId: number) =>
    apiClient.get<PaymentStatus>(`/payments/transfers/${transferId}/payment-status`),
};
