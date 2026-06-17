import { useState } from "react";
import { Alert, Text, View } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { AmountDisplay, AlertBanner, Button, FintechCard, LoadingState, Screen, StatusPill, Timeline } from "../../components";
import { transfersApi } from "../../api";
import { formatDate, formatZAR, formatForeign } from "../../utils/format";
import {
  CANCELLATION_REASON_LABELS,
  TRANSFER_STATUS_LABELS,
  UNPAID_CANCELLABLE_STATUSES,
} from "../../utils/constants";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";

const STEPS = [
  "Transfer created",
  "Payment reference generated",
  "Payment received",
  "Compliance review",
  "Submitted to partner",
  "Processing",
  "Completed",
];

type Props = NativeStackScreenProps<RootStackParamList, "TransferTracking">;

export default function TransferTrackingScreen({ route, navigation }: Props) {
  const { id } = route.params;
  const theme = useAppTheme();
  const queryClient = useQueryClient();
  const [cancelling, setCancelling] = useState(false);
  const [cancelError, setCancelError] = useState("");

  const { data: transfer, isLoading } = useQuery({
    queryKey: ["transfer", id],
    queryFn: async () => (await transfersApi.get(id)).data,
    refetchInterval: 15000,
  });

  const { data: timeline = [] } = useQuery({
    queryKey: ["timeline", id],
    queryFn: () => transfersApi.timeline(id),
    refetchInterval: 15000,
  });

  const handleCancel = () => {
    Alert.alert(
      "Cancel transfer?",
      "Only unpaid transfers can be cancelled. If you have already made payment, please do not cancel and contact support.",
      [
        { text: "Keep transfer", style: "cancel" },
        {
          text: "Cancel transfer",
          style: "destructive",
          onPress: async () => {
            setCancelling(true);
            setCancelError("");
            try {
              await transfersApi.cancel(id);
              await queryClient.invalidateQueries({ queryKey: ["transfer", id] });
              await queryClient.invalidateQueries({ queryKey: ["timeline", id] });
            } catch (e) {
              setCancelError(e instanceof Error ? e.message : "Could not cancel transfer");
            } finally {
              setCancelling(false);
            }
          },
        },
      ],
    );
  };

  if (isLoading || !transfer) return <LoadingState message="Loading transfer..." />;

  const statusLabel = TRANSFER_STATUS_LABELS[transfer.status] ?? transfer.status;
  const variant =
    transfer.status === "completed"
      ? "success"
      : transfer.status === "failed" || transfer.status === "cancelled"
        ? "error"
        : "info";
  const isUnpaid = UNPAID_CANCELLABLE_STATUSES.has(transfer.status);
  const cancellationLabel = transfer.cancellation_reason
    ? CANCELLATION_REASON_LABELS[transfer.cancellation_reason] ?? transfer.cancellation_reason
  : null;

  const timelineSteps = (timeline.length ? timeline : STEPS.map((s) => ({ status: s, created_at: "", note: undefined }))).map((item, i) => ({
    title: TRANSFER_STATUS_LABELS[item.status] ?? item.status,
    subtitle: item.created_at ? formatDate(item.created_at) : undefined,
    note: item.note,
    completed: i < (timeline.length || 1),
    active: i === 0,
  }));

  return (
    <Screen scroll>
      <View style={{ alignItems: "center", marginBottom: spacing.lg }}>
        <View style={{ width: 72, height: 72, borderRadius: 36, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center", marginBottom: spacing.md }}>
          <Ionicons
            name={transfer.status === "completed" ? "checkmark-circle" : transfer.status === "cancelled" ? "close-circle" : "time"}
            size={40}
            color={theme.primary}
          />
        </View>
        <Text style={[typography.h2, { color: theme.text }]}>{transfer.reference}</Text>
        <StatusPill label={statusLabel} variant={variant as "success"} size="md" />
      </View>

      {cancelError ? <AlertBanner type="error" message={cancelError} /> : null}

      {transfer.status === "cancelled" && transfer.cancellation_reason === "expired_unpaid_24h" ? (
        <FintechCard variant="accent">
          <Text style={[typography.body, { color: theme.text }]}>
            Cancelled automatically because payment was not received within 24 hours.
          </Text>
        </FintechCard>
      ) : null}

      {cancellationLabel && transfer.status === "cancelled" ? (
        <Text style={[typography.caption, { color: theme.textSecondary, marginBottom: spacing.md, textAlign: "center" }]}>
          {cancellationLabel}
        </Text>
      ) : null}

      <FintechCard variant="elevated">
        <AmountDisplay label="Amount to pay" amount={formatZAR(transfer.total_amount_zar)} sublabel={`Includes transfer fee ${formatZAR(transfer.fee_zar)}`} size="sm" />
        <View style={{ height: 1, backgroundColor: theme.borderLight, marginVertical: spacing.md }} />
        <AmountDisplay label={`${transfer.beneficiary?.full_name ?? "Recipient"} receives`} amount={formatForeign(transfer.receive_amount_ghs, "GHS")} sublabel={`Rate ${transfer.exchange_rate}`} size="sm" />
      </FintechCard>

      <FintechCard variant="default">
        <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.md }]}>Delivery timeline</Text>
        <Timeline steps={timelineSteps} />
      </FintechCard>

      {isUnpaid ? (
        <FintechCard variant="default">
          <Text style={[typography.caption, { color: theme.textSecondary, marginBottom: spacing.md }]}>
            Only unpaid transfers can be cancelled. If you have already made payment, please do not cancel and contact support.
          </Text>
          <Button title="Cancel transfer" onPress={handleCancel} loading={cancelling} variant="outline" />
        </FintechCard>
      ) : null}

      {transfer.status !== "cancelled" ? (
        <>
          <Button title="View receipt" onPress={() => navigation.navigate("Receipt", { id })} variant="outline" />
          <Button title="Send again" onPress={() => navigation.navigate("SendFlow")} variant="ghost" />
        </>
      ) : (
        <Button title="Send again" onPress={() => navigation.navigate("SendFlow")} />
      )}
    </Screen>
  );
}
