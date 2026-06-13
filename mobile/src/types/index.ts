export interface User {
  id: number;
  mobile_number: string | null;
  email: string | null;
  first_name: string | null;
  last_name: string | null;
  role: string;
  status: string;
  email_verified: boolean;
  phone_verified: boolean;
}

export interface TokenResponse {
  access_token: string | null;
  refresh_token: string | null;
  mfa_required?: boolean;
  step_up_required?: boolean;
  step_up_mobile?: string | null;
  risk_score?: number;
  risk_level?: string;
}

export interface Profile {
  id: number;
  user_id: number;
  first_name: string;
  last_name: string;
  date_of_birth: string | null;
  id_number: string | null;
  address_line1: string | null;
  city: string | null;
  province: string | null;
  postal_code: string | null;
  country: string;
  kyc_status: string;
  kyc_rejection_reason: string | null;
}

export type BeneficiaryType = "mobile_money" | "bank_account" | "cash_pickup";

export interface Beneficiary {
  id: number;
  user_id: number;
  beneficiary_type: BeneficiaryType;
  full_name: string;
  country: string;
  mobile_money_provider: string | null;
  mobile_wallet_number: string | null;
  bank_name: string | null;
  bank_account_number: string | null;
  relationship_to_sender: string;
  status: string;
  is_active: boolean;
  created_at: string;
}

export interface Transfer {
  id: number;
  reference: string;
  beneficiary_id: number;
  status: string;
  send_amount_zar: string;
  fee_zar: string;
  exchange_rate: string;
  receive_amount_ghs: string;
  total_amount_zar: string;
  created_at: string;
  completed_at: string | null;
}

export interface TransferDetail extends Transfer {
  beneficiary?: Beneficiary;
  payment_reference?: {
    reference_number: string;
    voucher_number: string | null;
    barcode_data: string | null;
    qr_data: string | null;
  };
  timeline?: { status: string; created_at: string; note?: string }[];
}

export interface KycDocument {
  id: number;
  document_type: string;
  file_name: string;
  status: string;
  uploaded_at: string;
}

export interface DashboardSummary {
  mobile_identity: {
    mobile_number: string | null;
    formatted_mobile: string | null;
    verified: boolean;
    verification_status: string;
  };
  profile_completion: { percent: number; missing: string[] };
  kyc: { status: string; raw_status: string; documents_uploaded: number };
  beneficiaries: { count: number };
  transfers: { count: number; recent: Transfer[] };
  referral_program: { referrals_made: number };
}

export interface WalletProfile {
  total_sent_zar: string;
  total_transfers: number;
  last_transfer_at: string | null;
}

export interface ReferralDashboard {
  referral_code: string;
  referrals_made: number;
  total_earnings_zar: string;
  pending_rewards_zar: string;
}

export interface Corridor {
  code: string;
  source_country: string;
  destination_country: string;
  is_active: boolean;
}

export const MOBILE_MONEY_PROVIDERS = ["MTN Ghana", "Telecel Ghana", "AirtelTigo Ghana"];

export const PARTNER_PROVIDERS = ["flutterwave", "mukuru", "onafriq", "veengu"] as const;
