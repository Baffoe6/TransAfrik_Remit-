import { Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Badge, Body, Button, Caption, Card, H2, LoadingState, Screen } from "../../components";
import { transfersApi } from "../../api";
import { formatDate, formatForeign, formatZAR } from "../../utils/format";
import { TRANSFER_STATUS_LABELS } from "../../utils/constants";
import { typography } from "../../theme/typography";
import { spacing } from "../../theme/spacing";
import { RootStackParamList } from "../../navigation/MainNavigator";

type Props = NativeStackScreenProps<RootStackParamList, "Receipt">;

export default function ReceiptScreen({ route }: Props) {
  const { id } = route.params;
  const { data: transfer, isLoading } = useQuery({
    queryKey: ["transfer", id],
    queryFn: async () => (await transfersApi.get(id)).data,
  });

  if (isLoading || !transfer) return <LoadingState />;

  return (
    <Screen scroll>
      <View style={{ alignItems: "center", marginBottom: spacing.lg }}>
        <Text style={{ fontSize: 32, fontWeight: "800", color: "#1B5E3B" }}>TransAfrik Remit</Text>
        <Caption>Official Transfer Receipt</Caption>
      </View>

      <Card elevated>
        <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: spacing.md }}>
          <H2>{transfer.reference}</H2>
          <Badge label={TRANSFER_STATUS_LABELS[transfer.status] ?? transfer.status} variant="gold" />
        </View>
        <Row label="Date" value={formatDate(transfer.created_at)} />
        <Row label="Sender" value="You" />
        <Row label="Recipient" value={transfer.beneficiary?.full_name ?? "—"} />
        <Row label="Send Amount" value={formatZAR(transfer.send_amount_zar)} />
        <Row label="Fee" value={formatZAR(transfer.fee_zar)} />
        <Row label="FX Rate" value={String(transfer.exchange_rate)} />
        <Row label="Recipient Gets" value={formatForeign(transfer.receive_amount_ghs, "GHS")} />
        <Row label="Total Paid" value={formatZAR(transfer.total_amount_zar)} />
        {transfer.payment_reference && (
          <Row label="Payment Ref" value={transfer.payment_reference.reference_number} />
        )}
      </Card>

      <Caption>Operated by IPAYGO (Pty) Ltd. Transfers processed via licensed partners.</Caption>
      <Button title="Share Receipt" onPress={() => {}} variant="outline" />
      <Button title="Download PDF" onPress={() => {}} variant="ghost" />
    </Screen>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={{ flexDirection: "row", justifyContent: "space-between", paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: "#F3F4F6" }}>
      <Caption>{label}</Caption>
      <Text style={typography.bodyBold}>{value}</Text>
    </View>
  );
}
