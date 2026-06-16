import { Linking, Share, Text, View } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import QRCode from "react-native-qrcode-svg";
import { AmountDisplay, Button, FintechCard, Screen } from "../../components";
import { formatZAR } from "../../utils/format";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { COMPLIANCE } from "../../utils/compliance";
import type { PaymentReference } from "../../api/payments";

type Props = NativeStackScreenProps<RootStackParamList, "PaymentSuccess">;

const RETAIL_PARTNERS = ["Pay@", "EasyPay", "Shoprite", "Pick n Pay", "Boxer"];

export default function PaymentSuccessScreen({ navigation, route }: Props) {
  const { transferId, reference } = route.params;
  const theme = useAppTheme();

  const shareVoucher = async () => {
    const msg = [
      "TransAfrik Remit — Payment Instructions",
      `Reference: ${reference.reference_number}`,
      reference.voucher_number ? `Voucher: ${reference.voucher_number}` : null,
      `Amount: ${formatZAR(reference.amount)}`,
      reference.expiry_date ? `Pay before: ${reference.expiry_date}` : null,
      "",
      "Pay at Pay@, EasyPay or participating retailers.",
    ].filter(Boolean).join("\n");
    await Share.share({ message: msg });
  };

  const shareWhatsApp = () => {
    const text = encodeURIComponent(`TransAfrik payment ref: ${reference.reference_number} — ${formatZAR(reference.amount)}`);
    Linking.openURL(`whatsapp://send?text=${text}`);
  };

  return (
    <Screen scroll>
      <View style={{ alignItems: "center", marginBottom: spacing.xl }}>
        <View style={{ width: 56, height: 56, borderRadius: 28, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center" }}>
          <Ionicons name="receipt-outline" size={28} color={theme.primary} />
        </View>
        <Text style={[typography.h1, { color: theme.text, marginTop: spacing.md }]}>Payment instructions</Text>
        <Text style={[typography.body, { color: theme.textSecondary, textAlign: "center" }]}>Complete payment to start processing your transfer</Text>
      </View>

      <FintechCard variant="elevated">
        <Text style={[typography.label, { color: theme.textTertiary }]}>Payment reference</Text>
        <Text style={[typography.h2, { color: theme.primary }]}>{reference.reference_number}</Text>
        {reference.voucher_number ? <Text style={[typography.body, { color: theme.text, marginTop: 4 }]}>Voucher: {reference.voucher_number}</Text> : null}
        <AmountDisplay label="Amount to pay" amount={formatZAR(reference.amount)} size="sm" />
        {reference.expiry_date ? <Text style={[typography.caption, { color: theme.warning, marginTop: spacing.sm }]}>Expires: {reference.expiry_date}</Text> : null}

        {(reference.qr_data || reference.barcode_data) && (
          <View style={{ alignItems: "center", marginTop: spacing.lg }}>
            <QRCode value={reference.qr_data ?? reference.barcode_data ?? reference.reference_number} size={140} />
            <Text style={[typography.caption, { color: theme.textTertiary, marginTop: spacing.sm }]}>Scan at retailer</Text>
          </View>
        )}

        <Text style={[typography.caption, { color: theme.textSecondary, marginTop: spacing.md }]}>
          Pay at: {RETAIL_PARTNERS.join(" · ")}
        </Text>
      </FintechCard>

      <Text style={[typography.caption, { color: theme.textTertiary, marginBottom: spacing.md, textAlign: "center" }]}>
        {COMPLIANCE.complianceReview}
      </Text>

      <Button title="Track transfer" onPress={() => navigation.replace("TransferTracking", { id: transferId })} variant="gold" />
      <Button title="Share via WhatsApp" onPress={shareWhatsApp} variant="primary" />
      <Button title="Share instructions" onPress={shareVoucher} variant="outline" />
      <Button title="View receipt" onPress={() => navigation.navigate("Receipt", { id: transferId })} variant="outline" />
      <Button title="Done" onPress={() => navigation.navigate("Tabs")} variant="ghost" />
    </Screen>
  );
}
