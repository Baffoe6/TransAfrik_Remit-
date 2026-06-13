export function isValidPin(pin: string): boolean {
  return /^\d{4,6}$/.test(pin);
}

export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());
}

export function isValidMobile(phone: string): boolean {
  const n = phone.replace(/\D/g, "");
  return n.length >= 10 && n.length <= 15;
}

export function isValidAmount(amount: string): boolean {
  const n = parseFloat(amount);
  return !Number.isNaN(n) && n > 0;
}
