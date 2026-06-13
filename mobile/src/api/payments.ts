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

export const paymentsApi = {
  methods: () => apiClient.get<PaymentMethod[]>("/payments/methods"),
  generate: (transferId: number, payment_method_code: string) =>
    apiClient.post<PaymentReference>(`/payments/transfers/${transferId}/generate`, { payment_method_code }),
  getReference: (transferId: number) =>
    apiClient.get<PaymentReference | null>(`/payments/transfers/${transferId}/reference`),
};
