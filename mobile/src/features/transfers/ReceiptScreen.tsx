import { Linking, Share, Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import QRCode from "react-native-qrcode-svg";
import * as Sharing from "expo-sharing";
import { AmountDisplay, Button, FintechCard, LoadingState, Screen, StatusPill, Timeline } from "../../components";
import { transfersApi } from "../../api";
import { formatDate, formatForeign, formatZAR, formatExchangeRate } from "../../utils/format";
import { TRANSFER_STATUS_LABELS } from "../../utils/constants";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { hapticLight } from "../../services/haptics";

type Props = NativeStackScreenProps<RootStackParamList, "Receipt">;

function buildReceiptText(transfer: NonNullable<Awaited<ReturnType<typeof transfersApi.get>>["data"]>) {
  return [
    "TransAfrik Remit — Transfer Receipt",
    `Reference: ${transfer.reference}`,
    `Status: ${TRANSFER_STATUS_LABELS[transfer.status] ?? transfer.status}`,
    `Date: ${formatDate(transfer.created_at)}`,
    `Amount paid: ${formatZAR(transfer.total_amount_zar)}`,
    `Includes transfer fee: ${formatZAR(transfer.fee_zar)}`,
    `Recipient: ${transfer.beneficiary?.full_name ?? "—"}`,
    `Received: ${formatForeign(transfer.receive_amount_ghs, "GHS")}`,
    `Rate: ${transfer.exchange_rate}`,
    "",
    "Verify at app.ipaygo.co.za",
  ].join("\n");
}

export default function ReceiptScreen({ route }: Props) {
  const { id } = route.params;
  const theme = useAppTheme();

  const { data: transfer, isLoading } = useQuery({
    queryKey: ["transfer", id],
    queryFn: async () => (await transfersApi.get(id)).data,
  });

  const { data: timeline = [] } = useQuery({
    queryKey: ["timeline", id],
    queryFn: () => transfersApi.timeline(id),
    enabled: !!transfer,
  });

  if (isLoading || !transfer) return <LoadingState />;

  const qrPayload = JSON.stringify({ ref: transfer.reference, id: transfer.id, v: 1 });
  const receiptText = buildReceiptText(transfer);

  const shareGeneric = async () => {
    hapticLight();
    await Share.share({ message: receiptText, title: `Receipt ${transfer.reference}` });
  };

  const shareWhatsApp = () => {
    hapticLight();
    Linking.openURL(`whatsapp://send?text=${encodeURIComponent(receiptText)}`);
  };

  const shareEmail = () => {
    hapticLight();
    Linking.openURL(`mailto:?subject=${encodeURIComponent(`TransAfrik Receipt ${transfer.reference}`)}&body=${encodeURIComponent(receiptText)}`);
  };

  const downloadPdf = async () => {
    hapticLight();
    if (await Sharing.isAvailableAsync()) {
      await Share.share({ message: receiptText, title: `${transfer.reference}.txt` });
    }
  };

  const timelineSteps = (timeline.length ? timeline : [{ status: transfer.status, created_at: transfer.created_at }]).map((item, i) => ({
    title: TRANSFER_STATUS_LABELS[item.status] ?? item.status,
    subtitle: item.created_at ? formatDate(item.created_at) : undefined,
    completed: i < timeline.length,
    active: i === timeline.length - 1,
  }));

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

        <View style={{ alignItems: "center", marginBottom: spacing.lg }}>
          <QRCode value={qrPayload} size={140} backgroundColor={theme.surface} color={theme.text} />
          <Text style={[typography.caption, { color: theme.textTertiary, marginTop: spacing.sm }]}>Scan to verify</Text>
        </View>

        <AmountDisplay amount={formatZAR(transfer.total_amount_zar)} label="Amount paid" sublabel={`Includes transfer fee ${formatZAR(transfer.fee_zar)}`} size="sm" />
        <View style={{ height: 1, backgroundColor: theme.borderLight, marginVertical: spacing.md }} />
        <AmountDisplay amount={formatForeign(transfer.receive_amount_ghs, "GHS")} label="Recipient received" size="sm" />

        <View style={{ marginTop: spacing.lg, gap: spacing.sm }}>
          <Row label="Date" value={formatDate(transfer.created_at)} />
          <Row label="Exchange rate" value={formatExchangeRate(transfer.exchange_rate, "ZAR", "GHS")} />
          {transfer.payment_reference && <Row label="Payment ref" value={transfer.payment_reference.reference_number} />}
        </View>
      </FintechCard>

      <FintechCard variant="default">
        <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.md }]}>Recipient details</Text>
        <Row label="Name" value={transfer.beneficiary?.full_name ?? "—"} />
        <Row label="Country" value={transfer.beneficiary?.country ?? "—"} />
        <Row label="Payout" value={transfer.beneficiary?.beneficiary_type?.replace("_", " ") ?? "—"} />
        <Row label="Account" value={transfer.beneficiary?.mobile_wallet_number ?? transfer.beneficiary?.bank_account_number ?? "—"} />
      </FintechCard>

      <FintechCard variant="muted">
        <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.md }]}>Transaction timeline</Text>
        <Timeline steps={timelineSteps} />
      </FintechCard>

      <View style={{ flexDirection: "row", alignItems: "flex-start", gap: spacing.sm, padding: spacing.md }}>
        <Ionicons name="shield-checkmark-outline" size={18} color={theme.textTertiary} />
        <Text style={[typography.caption, { color: theme.textTertiary, flex: 1 }]}>
          Transfers processed via licensed remittance partners. TransAfrik Remit is a facilitation platform operated by IPAYGO (Pty) Ltd.
        </Text>
      </View>

      <Button title="Share via WhatsApp" onPress={shareWhatsApp} variant="primary" />
      <Button title="Share via Email" onPress={shareEmail} variant="outline" />
      <Button title="Download receipt" onPress={downloadPdf} variant="outline" />
      <Button title="Share" onPress={shareGeneric} variant="ghost" />
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
