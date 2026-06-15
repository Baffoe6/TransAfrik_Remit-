export const CORRIDORS = [
  { code: "ZA-GH", country: "GH", name: "Ghana", flag: "🇬🇭", currency: "GHS", eta: "Same day" },
  { code: "ZA-ZW", country: "ZW", name: "Zimbabwe", flag: "🇿🇼", currency: "USD", eta: "1–2 days" },
  { code: "ZA-ZM", country: "ZM", name: "Zambia", flag: "🇿🇲", currency: "ZMW", eta: "Same day" },
  { code: "ZA-KE", country: "KE", name: "Kenya", flag: "🇰🇪", currency: "KES", eta: "Same day" },
  { code: "ZA-NG", country: "NG", name: "Nigeria", flag: "🇳🇬", currency: "NGN", eta: "1–2 days" },
  { code: "ZA-UG", country: "UG", name: "Uganda", flag: "🇺🇬", currency: "UGX", eta: "Same day" },
] as const;

export const GHANA_MM_PROVIDERS = [
  { id: "mtn", label: "MTN Mobile Money" },
  { id: "telecel", label: "Telecel Cash" },
  { id: "airteltigo", label: "AirtelTigo Money" },
] as const;

export const RELATIONSHIPS = ["Family", "Friend", "Spouse", "Parent", "Child", "Business", "Other"];

export const TRANSFER_STATUS_LABELS: Record<string, string> = {
  draft: "Draft",
  pending_payment: "Pending",
  payment_received: "Payment Received",
  compliance_review: "Processing",
  submitted_to_partner: "Processing",
  processing: "Processing",
  completed: "Completed",
  cancelled: "Cancelled",
  failed: "Failed",
  rejected: "Rejected",
  refunded: "Refunded",
};

export const ACTIVITY_STATUS_FILTERS = [
  { value: "all", label: "All" },
  { value: "pending_payment", label: "Pending" },
  { value: "processing", label: "Processing" },
  { value: "completed", label: "Completed" },
  { value: "failed", label: "Failed" },
  { value: "refunded", label: "Refunded" },
] as const;

export const ACTIVITY_TIME_FILTERS = [
  { value: "all", label: "All time" },
  { value: "today", label: "Today" },
  { value: "week", label: "This week" },
  { value: "month", label: "This month" },
] as const;

export const BENEFICIARY_CATEGORIES = [
  { value: "all", label: "All", icon: "people" as const },
  { value: "mobile_money", label: "Mobile Money", icon: "phone-portrait" as const },
  { value: "bank_account", label: "Bank Account", icon: "business" as const },
  { value: "cash_pickup", label: "Cash Pickup", icon: "cash" as const },
] as const;

export const KYC_WORKFLOW_STATES = [
  { value: "draft", label: "Draft", variant: "neutral" as const },
  { value: "submitted", label: "Submitted", variant: "info" as const },
  { value: "reviewing", label: "Reviewing", variant: "warning" as const },
  { value: "approved", label: "Approved", variant: "success" as const },
  { value: "rejected", label: "Rejected", variant: "error" as const },
] as const;

export const NETWORK_LOGOS: Record<string, { label: string; color: string; icon: string }> = {
  mtn: { label: "MTN", color: "#FFCC00", icon: "cellular" },
  telecel: { label: "Telecel", color: "#E60000", icon: "cellular" },
  airteltigo: { label: "AirtelTigo", color: "#ED1C24", icon: "cellular" },
  vodacom: { label: "Vodacom", color: "#E60000", icon: "cellular" },
  mukuru: { label: "Mukuru", color: "#1B5E3B", icon: "shield-checkmark" },
};

export const USER_TIERS = [
  { id: "standard", label: "Standard", limit: "R25,000/mo" },
  { id: "verified", label: "Verified", limit: "R50,000/mo" },
  { id: "premium", label: "Premium", limit: "R100,000/mo" },
] as const;

export const PAYOUT_PARTNERS = [
  { id: "mukuru", name: "Mukuru", corridors: ["GH", "ZW", "ZM"] },
  { id: "flutterwave", name: "Flutterwave", corridors: ["NG", "KE", "UG"] },
  { id: "onafriq", name: "Onafriq", corridors: ["GH", "KE", "UG"] },
] as const;

export const FAQ_ITEMS = [
  { q: "How long do transfers take?", a: "Most mobile money transfers arrive same day. Bank and cash pickup may take 1–2 business days." },
  { q: "What payment methods are supported?", a: "Pay@, EasyPay, EFT, and card payments via our partners." },
  { q: "Is my money safe?", a: "TransAfrik uses licensed partners and FICA-compliant KYC. We never hold your funds directly." },
  { q: "How do I complete KYC?", a: "Upload your ID or passport, proof of address, and a selfie from the KYC section in your profile." },
];
