export interface Profile {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  date_of_birth: string | null;
  id_number: string | null;
  address_line1: string | null;
  address_line2: string | null;
  city: string | null;
  province: string | null;
  postal_code: string | null;
  country: string;
  kyc_status: string;
  kyc_rejection_reason: string | null;
  created_at: string;
}

export type BeneficiaryType = "mobile_money" | "bank_account" | "cash_pickup";

export interface Beneficiary {
  id: number;
  user_id: number;
  beneficiary_type: BeneficiaryType;
  full_name: string;
  account_name: string | null;
  country: string;
  mobile_money_provider: string | null;
  mobile_wallet_number: string | null;
  bank_name: string | null;
  bank_account_number: string | null;
  bank_branch: string | null;
  pickup_location: string | null;
  pickup_city: string | null;
  relationship_to_sender: string;
  status: string;
  rejection_reason: string | null;
  is_active: boolean;
  created_at: string;
}

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

export interface PaymentReferenceBrief {
  reference_number: string;
  voucher_number: string | null;
  barcode_data: string | null;
  qr_data: string | null;
  expiry_date: string | null;
  status: string;
  banking_instructions: Record<string, string> | null;
}

export interface Transfer {
  id: number;
  reference: string;
  user_id: number;
  beneficiary_id: number;
  payment_method_id: number | null;
  status: string;
  send_amount_zar: string;
  fee_zar: string;
  exchange_rate: string;
  receive_amount_ghs: string;
  total_amount_zar: string;
  aml_flags: AmlFlag[] | null;
  risk_score: number;
  compliance_approved: boolean;
  rejection_reason: string | null;
  batch_export_id: string | null;
  provider_reference: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  payment_reference?: PaymentReferenceBrief | null;
  timeline?: TimelineEvent[];
}

export interface TimelineEvent {
  status: string;
  label: string;
  timestamp: string | null;
  notes: string | null;
}

export interface AmlFlag {
  type: string;
  message: string;
}

export interface CalculatorResult {
  send_amount_zar: string;
  fee_zar: string;
  exchange_rate: string;
  receive_amount_ghs: string;
  total_amount_zar: string;
  from_currency: string;
  to_currency: string;
}

export interface KycDocument {
  id: number;
  document_type: string;
  original_filename: string;
  status: string;
  rejection_reason: string | null;
  created_at: string;
}

export interface DashboardStats {
  total_customers: number;
  pending_kyc: number;
  pending_transfers: number;
  completed_transfers: number;
  monthly_volume_zar: string;
}

export interface AnalyticsDashboard {
  daily_volume_zar: string;
  monthly_volume_zar: string;
  daily_revenue_zar: string;
  monthly_revenue_zar: string;
  transfers_by_country: { country: string; count: number; volume_zar: string }[];
  transfers_by_payment_method: { method: string; count: number; volume_zar: string }[];
  transfers_by_status: Record<string, number>;
  completed_today: number;
}

export interface ProviderConfigItem {
  id: number;
  provider_code: string;
  provider_type: string;
  display_name: string;
  is_enabled: boolean;
  is_sandbox: boolean;
  api_base_url: string | null;
  has_webhook_secret: boolean;
  config: Record<string, unknown> | null;
}

export interface SecurityAuditEntry {
  id: number;
  user_id: number | null;
  event_type: string;
  ip_address: string | null;
  details: string | null;
  created_at: string;
}

export interface UserSessionItem {
  id: number;
  user_id: number;
  ip_address: string | null;
  created_at: string;
  expires_at: string;
}

export interface EddCase {
  id: number;
  user_id: number;
  transfer_id: number | null;
  status: string;
  risk_score: number;
  reason: string;
  aml_flags: AmlFlag[] | null;
  created_at: string;
}

export interface RateHistoryEntry {
  id: number;
  from_currency: string;
  to_currency: string;
  rate: string;
  effective_from: string;
  effective_to: string | null;
  change_reason: string | null;
  created_at: string;
}

export interface MukuruBatch {
  id: number;
  batch_id: string;
  status: string;
  transfer_count: number;
  total_amount_zar: string;
  total_amount_ghs: string;
  file_format: string;
  created_at: string;
  approved_at: string | null;
  submitted_at: string | null;
  reconciled_at: string | null;
}

export interface MukuruReconciliation {
  batches_by_status: Record<string, number>;
  total_batches: number;
  pending_approval: number;
  submitted: number;
  reconciled: number;
  settlement_variance_zar: string;
  recent_settlements: { id: number; reference: string; amount_zar: string; status: string; variance_zar: string; settlement_date: string }[];
}

export interface TreasuryDashboard {
  funds_collected_today_zar: string;
  funds_pending_processing_zar: string;
  funds_paid_out_zar: string;
  outstanding_liabilities_zar: string;
  revenue_today_zar: string;
  revenue_month_zar: string;
  awaiting_payment_zar: string;
  completed_transfer_count: number;
}

export interface SettlementDashboard {
  pay_at_collections: { provider: string; transaction_count: number; collected_zar: string };
  easy_pay_collections: { provider: string; transaction_count: number; collected_zar: string };
  eft_collections: { provider: string; transaction_count: number; collected_zar: string };
  mukuru_payouts_zar: string;
  total_variance_zar: string;
  payment_settlements: { id: number; provider: string; settlement_date: string; expected_zar: string; collected_zar: string; variance_zar: string; status: string; transaction_count: number }[];
  mukuru_settlements: { id: number; reference: string; amount_zar: string; variance_zar: string; status: string }[];
}

export interface OperationsAuditEntry {
  id: number;
  category: string;
  action: string;
  entity_type: string;
  entity_id: number | null;
  user_id: number | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface FeeRuleV2 {
  id: number;
  name: string;
  min_amount_zar: string;
  max_amount_zar: string | null;
  fee_type: string;
  fee_value: string;
  destination_country: string | null;
  payment_method_id: number | null;
  provider_id: number | null;
  priority: number;
  is_active: boolean;
}

export interface PaymentDashboardStats {
  pending_payments: number;
  pending_verifications: number;
  expired_references: number;
  paid_today: number;
  daily_volume_zar: string;
  monthly_volume_zar: string;
}

export interface ComplianceQueueItem {
  transfer_id: number;
  reference: string;
  customer_email: string;
  customer_name: string;
  send_amount_zar: string;
  risk_score: number;
  aml_flags: AmlFlag[] | null;
  status: string;
  created_at: string;
}

export interface CustomerListItem {
  id: number;
  email: string;
  phone: string | null;
  first_name: string | null;
  last_name: string | null;
  kyc_status: string | null;
  created_at: string;
  transfer_count: number;
}

export interface AuditLog {
  id: number;
  user_id: number | null;
  action: string;
  entity_type: string;
  entity_id: number | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export const TRANSFER_STATUSES: Record<string, { label: string; color: string }> = {
  draft: { label: "Draft", color: "bg-gray-100 text-gray-700" },
  awaiting_payment: { label: "Awaiting Payment", color: "bg-orange-100 text-orange-800" },
  payment_pending_verification: { label: "Pending Verification", color: "bg-amber-100 text-amber-800" },
  payment_verified: { label: "Payment Verified", color: "bg-blue-100 text-blue-800" },
  compliance_review: { label: "Compliance Review", color: "bg-purple-100 text-purple-800" },
  ready_for_processing: { label: "Ready for Processing", color: "bg-indigo-100 text-indigo-800" },
  submitted_to_mukuru: { label: "Submitted to Mukuru", color: "bg-indigo-100 text-indigo-800" },
  processing: { label: "Processing", color: "bg-blue-100 text-blue-800" },
  completed: { label: "Completed", color: "bg-green-100 text-green-800" },
  failed: { label: "Failed", color: "bg-red-100 text-red-800" },
  refunded: { label: "Refunded", color: "bg-gray-100 text-gray-800" },
  expired: { label: "Expired", color: "bg-gray-100 text-gray-600" },
};

export const MOBILE_MONEY_PROVIDERS = [
  "MTN Ghana",
  "Telecel Ghana",
  "AirtelTigo Ghana",
];

export const BENEFICIARY_TYPES: { value: BeneficiaryType; label: string }[] = [
  { value: "mobile_money", label: "Mobile Money" },
  { value: "bank_account", label: "Bank Account" },
  { value: "cash_pickup", label: "Cash Pickup" },
];

export const DISCLAIMER =
  "TransAfrik Remit is a customer-facing remittance facilitation platform operated by IPAYGO (Pty) Ltd. Transfers are processed through approved third-party payment and remittance partners.";

export interface DashboardSummary {
  profile_completion: { percent: number; missing: string[] };
  kyc: {
    status: string;
    raw_status: string;
    documents_uploaded: number;
    rejection_reason: string | null;
  };
  beneficiaries: {
    count: number;
    items: {
      id: number;
      full_name: string;
      country: string;
      mobile_wallet_number: string | null;
      mobile_money_provider: string | null;
      relationship_to_sender: string;
      status: string;
    }[];
  };
  transfers: {
    count: number;
    recent: {
      id: number;
      reference: string;
      status: string;
      send_amount_zar: string;
      receive_amount_ghs: string;
      created_at: string | null;
    }[];
  };
  transaction_history: {
    id: number;
    reference: string;
    status: string;
    send_amount_zar: string;
    receive_amount_ghs: string;
    fee_zar: string;
    exchange_rate: string;
    created_at: string | null;
    completed_at: string | null;
  }[];
  referral_program: { referrals_made: number };
}
