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
  pending_payment: "Awaiting Payment",
  payment_received: "Payment Received",
  compliance_review: "Compliance Review",
  submitted_to_partner: "Submitted to Partner",
  processing: "Processing",
  completed: "Completed",
  cancelled: "Cancelled",
  failed: "Failed",
  rejected: "Rejected",
};

export const FAQ_ITEMS = [
  { q: "How long do transfers take?", a: "Most mobile money transfers arrive same day. Bank and cash pickup may take 1–2 business days." },
  { q: "What payment methods are supported?", a: "Pay@, EasyPay, EFT, and card payments via our partners." },
  { q: "Is my money safe?", a: "TransAfrik uses licensed partners and FICA-compliant KYC. We never hold your funds directly." },
  { q: "How do I complete KYC?", a: "Upload your ID or passport, proof of address, and a selfie from the KYC section in your profile." },
];
