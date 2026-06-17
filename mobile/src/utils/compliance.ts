/** Production-accurate compliance copy — no misleading licensing claims */

export const COMPLIANCE = {
  platformDisclaimer:
    "TransAfrik Remit is a customer facilitation platform operated by IPAYGO (Pty) Ltd. Transfers are processed through approved payment and remittance partners.",
  partnerPayout: "Payouts are delivered via our partner-powered network.",
  kycRequired: "Identity verification is required before you can send money.",
  complianceReview: "Compliance review may apply to transfers and payouts.",
  pilotAccess: "Sign up with your mobile number — no invite required.",
  popiaConsent:
    "I consent to IPAYGO (Pty) Ltd processing my personal information in accordance with POPIA for remittance services.",
  amlDeclaration:
    "I declare that funds sent are from legitimate sources and I am not acting on behalf of a third party without disclosure.",
  termsAcceptance: "I accept the Terms of Service and Privacy Policy.",
} as const;

export const KYC_DOC_TYPES = [
  { type: "id_passport", label: "Passport or National ID", icon: "card-outline" as const, hint: "Clear photo of your ID document" },
  { type: "proof_of_address", label: "Proof of Address", icon: "home-outline" as const, hint: "Utility bill or bank statement (within 3 months)" },
  { type: "selfie", label: "Selfie Verification", icon: "person-circle-outline" as const, hint: "Hold your ID next to your face" },
] as const;

export const SUPPORT_CATEGORIES = [
  { value: "transfer_delay", label: "Transfer delay" },
  { value: "payment_issue", label: "Payment issue" },
  { value: "kyc_issue", label: "KYC issue" },
  { value: "beneficiary_issue", label: "Beneficiary issue" },
  { value: "refund_request", label: "Refund request" },
  { value: "general", label: "General enquiry" },
] as const;

export const FLUTTERWAVE_METHOD_CODES = new Set([
  "flutterwave",
  "fw_card",
  "fw_eft",
  "fw_capitec",
  "fw_1voucher",
  "fw_ussd",
  "fw_account",
]);

export function isFlutterwaveMethod(code: string): boolean {
  return code.startsWith("fw_") || FLUTTERWAVE_METHOD_CODES.has(code.toLowerCase());
}

export const FLUTTERWAVE_METHOD_ICONS: Record<string, keyof typeof import("@expo/vector-icons").Ionicons.glyphMap> = {
  fw_card: "card",
  fw_eft: "business",
  fw_capitec: "phone-portrait",
  fw_1voucher: "ticket",
  fw_ussd: "keypad",
  fw_account: "wallet",
  flutterwave: "card",
};
