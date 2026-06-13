import { Badge } from "@/components/ui/badge";
import { TRANSFER_STATUSES } from "@/types";

export function StatusBadge({ status }: { status: string }) {
  const config = TRANSFER_STATUSES[status] || { label: status, color: "bg-gray-100 text-gray-800" };
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${config.color}`}>
      {config.label}
    </span>
  );
}

export function KycStatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    not_submitted: "bg-gray-100 text-gray-700",
    pending: "bg-amber-100 text-amber-800",
    approved: "bg-green-100 text-green-800",
    rejected: "bg-red-100 text-red-800",
  };
  const label = status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  return <Badge className={colors[status] || ""}>{label}</Badge>;
}
