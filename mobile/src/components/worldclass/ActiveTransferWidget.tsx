import { Text, TouchableOpacity, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { FintechCard, StatusPill, Timeline } from "../fintech";
import { useAppTheme, radius, spacing } from "../../theme";
import { typography } from "../../theme/typography";
import { formatZAR, formatRelativeDate } from "../../utils/format";
import { TRANSFER_STATUS_LABELS } from "../../utils/constants";
import type { Transfer } from "../../types";

interface ActiveTransferWidgetProps {
  transfer: Transfer | null;
  onPress?: () => void;
}

const PROGRESS_MAP: Record<string, number> = {
  pending_payment: 20,
  payment_received: 40,
  compliance_review: 55,
  submitted_to_partner: 70,
  processing: 85,
  completed: 100,
  failed: 0,
};

export function ActiveTransferWidget({ transfer, onPress }: ActiveTransferWidgetProps) {
  const theme = useAppTheme();
  if (!transfer) return null;

  const progress = PROGRESS_MAP[transfer.status] ?? 30;
  const isActive = !["completed", "failed", "cancelled", "rejected"].includes(transfer.status);

  if (!isActive) return null;

  const steps = [
    { title: "Created", completed: true },
    { title: TRANSFER_STATUS_LABELS[transfer.status] ?? transfer.status, active: true },
    { title: "Delivered", completed: false },
  ];

  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.85}>
      <FintechCard variant="accent">
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.sm }}>
            <View style={{ width: 36, height: 36, borderRadius: 18, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center" }}>
              <Ionicons name="pulse" size={18} color={theme.primary} />
            </View>
            <Text style={[typography.bodyBold, { color: theme.text }]}>Active transfer</Text>
          </View>
          <StatusPill label={TRANSFER_STATUS_LABELS[transfer.status] ?? transfer.status} variant="info" />
        </View>
        <Text style={[typography.h3, { color: theme.text }]}>{formatZAR(transfer.total_amount_zar)}</Text>
        <Text style={[typography.caption, { color: theme.textSecondary }]}>{transfer.reference} · {formatRelativeDate(transfer.created_at)}</Text>
        <View style={{ height: 6, backgroundColor: theme.border, borderRadius: 3, marginVertical: spacing.md, overflow: "hidden" }}>
          <View style={{ width: `${progress}%`, height: 6, backgroundColor: theme.primary, borderRadius: 3 }} />
        </View>
        <Timeline steps={steps.map((s, i) => ({ title: s.title, completed: s.completed, active: s.active && i === 1 }))} />
        <Text style={[typography.caption, { color: theme.primary, fontWeight: "600", marginTop: spacing.sm }]}>Tap to track →</Text>
      </FintechCard>
    </TouchableOpacity>
  );
}
