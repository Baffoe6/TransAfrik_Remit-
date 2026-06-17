export function formatZAR(amount: string | number | null | undefined): string {
  const n = parseFloat(String(amount ?? "0"));
  if (Number.isNaN(n)) return "R0.00";
  return `R${n.toLocaleString("en-ZA", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function formatForeign(amount: string | number | null | undefined, currency: string): string {
  const n = parseFloat(String(amount ?? "0"));
  if (Number.isNaN(n)) return `0.00 ${currency}`;
  return `${n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${currency}`;
}

export function formatExchangeRate(rate: string | number, fromCurrency: string, toCurrency: string): string {
  const n = parseFloat(String(rate));
  if (Number.isNaN(n)) return `1 ${fromCurrency} = — ${toCurrency}`;
  return `1 ${fromCurrency} = ${n.toFixed(4)} ${toCurrency}`;
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-ZA", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatRelativeDate(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const days = Math.floor(diff / 86400000);
  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days} days ago`;
  return formatDate(iso);
}

export function greetingName(firstName?: string | null): string {
  const hour = new Date().getHours();
  const period = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
  return firstName ? `${period}, ${firstName}` : period;
}
