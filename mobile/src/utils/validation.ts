export function isValidPin(pin: string): boolean {
  return /^\d{4,6}$/.test(pin);
}

/** Production password — backend requires min 8 characters */
export function isValidPassword(password: string): boolean {
  return password.length >= 8 && password.length <= 128;
}

export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
}

export function isValidMobile(phone: string): boolean {
  const n = phone.replace(/\D/g, "");
  return n.length >= 10 && n.length <= 15;
}

/** Ghana mobile money numbers — 9 digits after country code */
export function isValidGhanaMobile(phone: string): boolean {
  const n = phone.replace(/\D/g, "");
  if (n.startsWith("233")) return n.length === 12;
  if (n.startsWith("0")) return n.length === 10;
  return n.length >= 9 && n.length <= 12;
}

export function isValidAmount(amount: string): boolean {
  const n = parseFloat(amount);
  return !Number.isNaN(n) && n > 0;
}

export function isValidDateOfBirth(dob: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dob)) return false;
  const d = new Date(dob);
  const age = (Date.now() - d.getTime()) / (365.25 * 86400000);
  return age >= 18 && age <= 120;
}
