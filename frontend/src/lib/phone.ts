export function normalizePhoneNumber(raw: string, defaultCountryCode = "27"): string {
  const cleaned = raw.trim().replace(/[^\d+]/g, "");
  let digits = cleaned;
  if (digits.startsWith("00")) digits = digits.slice(2);
  if (digits.startsWith("+")) digits = digits.slice(1);
  else if (digits.startsWith("0")) digits = defaultCountryCode + digits.slice(1);

  const codes = ["27", "233", "263", "254", "256", "260", "234"];
  for (const code of codes.sort((a, b) => b.length - a.length)) {
    if (digits.startsWith(code) && digits.length >= code.length + 7) {
      return `+${digits}`;
    }
  }
  if (digits.length >= 9) return `+${defaultCountryCode}${digits}`;
  throw new Error("Invalid mobile number");
}

export function formatPhoneNumber(e164: string): string {
  if (!e164) return "";
  const normalized = e164.startsWith("+") ? e164 : `+${e164}`;
  const codes = ["27", "233", "263", "254", "256", "260", "234"];
  for (const code of codes.sort((a, b) => b.length - a.length)) {
    if (normalized.slice(1).startsWith(code)) {
      const rest = normalized.slice(1 + code.length);
      return rest.length <= 3 ? `+${code} ${rest}` : `+${code} ${rest.slice(0, 3)} ${rest.slice(3)}`;
    }
  }
  return normalized;
}

export function isEmailIdentifier(value: string): boolean {
  return value.includes("@");
}
