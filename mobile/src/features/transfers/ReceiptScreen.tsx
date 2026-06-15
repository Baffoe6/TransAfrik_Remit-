import { Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { AmountDisplay, Button, FintechCard, LoadingState, Screen, StatusPill } from "../../components";
import { transfersApi } from "../../api";
import { formatDate, formatForeign, formatZAR } from "../../utils/format";
import { TRANSFER_STATUS_LABELS } from "../../utils/constants";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";

type Props = NativeStackScreenProps<RootStackParamList, "Receipt">;

export default function ReceiptScreen({ route }: Props) {
  const { id } = route.params;
  const theme = useAppTheme();

  const { data: transfer, isLoading } = useQuery({
    queryKey: ["transfer", id],
    queryFn: async () => (await transfersApi.get(id)).data,
  });

  if (isLoading || !transfer) return <LoadingState />;

  return (
    <Screen scroll>
      <View style={{ alignItems: "center", marginBottom: spacing.xl }}>
        <View style={{ width: 56, height: 56, borderRadius: 28, backgroundColor: theme.primary, alignItems: "center", justifyContent: "center", marginBottom: spacing.md }}>
          <Text style={{ color: theme.accent, fontWeight: "800", fontSize: 18 }}>TA</Text>
        </View>
        <Text style={[typography.h2, { color: theme.text }]}>Transfer receipt</Text>
        <Text style={[typography.caption, { color: theme.textSecondary }]}>TransAfrik Remit · IPAYGO (Pty) Ltd</Text>
      </View>

      <FintechCard variant="elevated">
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.lg }}>
          <Text style={[typography.bodyBold, { color: theme.text, fontSize: 18 }]}>{transfer.reference}</Text>
          <StatusPill label={TRANSFER_STATUS_LABELS[transfer.status] ?? transfer.status} variant="gold" />
        </View>

        <AmountDisplay amount={formatZAR(transfer.send_amount_zar)} label="Amount sent" size="sm" />
        <View style={{ height: 1, backgroundColor: theme.borderLight, marginVertical: spacing.md }} />
        <AmountDisplay amount={formatForeign(transfer.receive_amount_ghs, "GHS")} label="Recipient received" size="sm" />

        <View style={{ marginTop: spacing.lg, gap: spacing.sm }}>
          <Row label="Date" value={formatDate(transfer.created_at)} />
          <Row label="Recipient" value={transfer.beneficiary?.full_name ?? "—"} />
          <Row label="Fee" value={formatZAR(transfer.fee_zar)} />
          <Row label="Exchange rate" value={String(transfer.exchange_rate)} />
          <Row label="Total paid" value={formatZAR(transfer.total_amount_zar)} highlight />
          {transfer.payment_reference && <Row label="Payment ref" value={transfer.payment_reference.reference_number} />}
        </View>
      </FintechCard>

      <View style={{ flexDirection: "row", alignItems: "flex-start", gap: spacing.sm, padding: spacing.md }}>
        <Ionicons name="shield-checkmark-outline" size={18} color={theme.textTertiary} />
        <Text style={[typography.caption, { color: theme.textTertiary, flex: 1 }]}>
          Transfers processed via licensed remittance partners. TransAfrik Remit is a facilitation platform operated by IPAYGO (Pty) Ltd.
        </Text>
      </View>

      <Button title="Share receipt" onPress={() => {}} variant="primary" />
      <Button title="Download PDF" onPress={() => {}} variant="outline" />
    </Screen>
  );
}

function Row({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  const theme = useAppTheme();
  return (
    <View style={{ flexDirection: "row", justifyContent: "space-between", paddingVertical: 6 }}>
      <Text style={[typography.caption, { color: theme.textSecondary }]}>{label}</Text>
      <Text style={[highlight ? typography.bodyBold : typography.body, { color: highlight ? theme.primary : theme.text }]}>{value}</Text>
    </View>
  );
}
