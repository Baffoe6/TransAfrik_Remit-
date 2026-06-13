export function normalizePhone(input: string): string {
  const digits = input.replace(/\D/g, "");
  if (digits.startsWith("27")) return `+${digits}`;
  if (digits.startsWith("0")) return `+27${digits.slice(1)}`;
  if (input.startsWith("+")) return input.replace(/\s/g, "");
  return `+${digits}`;
}

export function formatPhoneDisplay(phone: string | null | undefined): string {
  if (!phone) return "—";
  const n = normalizePhone(phone);
  if (n.startsWith("+27") && n.length >= 12) {
    return `${n.slice(0, 3)} ${n.slice(3, 5)} ${n.slice(5, 8)} ${n.slice(8)}`;
  }
  return n;
}

export function maskPhone(phone: string | null | undefined): string {
  if (!phone || phone.length < 6) return "****";
  return `${phone.slice(0, 4)}****${phone.slice(-2)}`;
}
