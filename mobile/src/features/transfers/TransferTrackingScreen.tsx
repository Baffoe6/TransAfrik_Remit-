import { Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Badge, Body, Button, Caption, Card, H2, LoadingState, Screen } from "../../components";
import { transfersApi } from "../../api";
import { formatDate, formatZAR, formatForeign } from "../../utils/format";
import { TRANSFER_STATUS_LABELS } from "../../utils/constants";
import { spacing } from "../../theme/spacing";
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

  return (
    <Screen scroll>
      <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.lg }}>
        <H2>{transfer.reference}</H2>
        <Badge label={statusLabel} variant={variant as "success"} />
      </View>

      <Card>
        <Caption>Recipient</Caption>
        <Body>{transfer.beneficiary?.full_name ?? "—"}</Body>
        <Caption>Send amount</Caption>
        <Text style={typography.h3}>{formatZAR(transfer.send_amount_zar)}</Text>
        <Caption>Recipient gets {formatForeign(transfer.receive_amount_ghs, "GHS")}</Caption>
      </Card>

      <Card elevated>
        <H2>Timeline</H2>
        {(timeline.length ? timeline : STEPS.map((s, i) => ({ status: s, created_at: "", note: undefined }))).map((item, i) => (
          <View key={i} style={{ flexDirection: "row", gap: spacing.md, marginBottom: spacing.md }}>
            <View style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: i === 0 ? "#1B5E3B" : "#D1D5DB", marginTop: 4 }} />
            <View style={{ flex: 1 }}>
              <Text style={typography.bodyBold}>{TRANSFER_STATUS_LABELS[item.status] ?? item.status}</Text>
              {item.created_at ? <Caption>{formatDate(item.created_at)}</Caption> : null}
              {item.note ? <Caption>{item.note}</Caption> : null}
            </View>
          </View>
        ))}
      </Card>

      <Button title="View Receipt" onPress={() => navigation.navigate("Receipt", { id })} variant="outline" />
    </Screen>
  );
}