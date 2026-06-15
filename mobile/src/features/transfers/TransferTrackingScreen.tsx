import { Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { AmountDisplay, Button, FintechCard, LoadingState, Screen, StatusPill, Timeline } from "../../components";
import { transfersApi } from "../../api";
import { formatDate, formatZAR, formatForeign } from "../../utils/format";
import { TRANSFER_STATUS_LABELS } from "../../utils/constants";
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

  const { data: transfer, isLoading } = useQuery({
    queryKey: ["transfer", id],
    queryFn: async () => (await transfersApi.get(id)).data,
    refetchInterval: 15000,
  });

  const { data: timeline = [] } = useQuery({
    queryKey: ["timeline", id],
    queryFn: async () => (await transfersApi.timeline(id)).data,
    refetchInterval: 15000,
  });

  if (isLoading || !transfer) return <LoadingState message="Loading transfer..." />;

  const statusLabel = TRANSFER_STATUS_LABELS[transfer.status] ?? transfer.status;
  const variant = transfer.status === "completed" ? "success" : transfer.status === "failed" ? "error" : "info";

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
          <Ionicons name={transfer.status === "completed" ? "checkmark-circle" : "time"} size={40} color={theme.primary} />
        </View>
        <Text style={[typography.h2, { color: theme.text }]}>{transfer.reference}</Text>
        <StatusPill label={statusLabel} variant={variant as "success"} size="md" />
      </View>

      <FintechCard variant="elevated">
        <AmountDisplay label="You sent" amount={formatZAR(transfer.send_amount_zar)} size="sm" />
        <View style={{ height: 1, backgroundColor: theme.borderLight, marginVertical: spacing.md }} />
        <AmountDisplay label={`${transfer.beneficiary?.full_name ?? "Recipient"} receives`} amount={formatForeign(transfer.receive_amount_ghs, "GHS")} sublabel={`Fee ${formatZAR(transfer.fee_zar)} · Rate ${transfer.exchange_rate}`} size="sm" />
      </FintechCard>

      <FintechCard variant="default">
        <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.md }]}>Delivery timeline</Text>
        <Timeline steps={timelineSteps} />
      </FintechCard>

      <Button title="View receipt" onPress={() => navigation.navigate("Receipt", { id })} variant="outline" />
      <Button title="Send again" onPress={() => navigation.navigate("SendFlow")} variant="ghost" />
    </Screen>
  );
}
