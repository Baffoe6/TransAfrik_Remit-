import { Share, Text, View } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Button, Caption, Card, H2, Screen } from "../../components";
import { formatZAR } from "../../utils/format";
import { typography } from "../../theme/typography";
import { spacing } from "../../theme/spacing";
import { RootStackParamList } from "../../navigation/MainNavigator";
import type { PaymentReference } from "../../api/payments";

type Props = NativeStackScreenProps<RootStackParamList, "PaymentSuccess">;

export default function PaymentSuccessScreen({ navigation, route }: Props) {
  const { transferId, reference } = route.params as { transferId: number; reference: PaymentReference };

  const shareVoucher = async () => {
    const msg = `TransAfrik Payment\nRef: ${reference.reference_number}\nVoucher: ${reference.voucher_number ?? "—"}\nAmount: ${formatZAR(reference.amount)}`;
    await Share.share({ message: msg });
  };

  return (
    <Screen scroll>
      <View style={{ alignItems: "center", marginBottom: spacing.xl }}>
        <Text style={{ fontSize: 64 }}>✅</Text>
        <H2>Payment Reference Ready</H2>
        <Caption>Pay at retail to complete your transfer</Caption>
      </View>

      <Card elevated>
        <Caption>Payment Reference</Caption>
        <Text style={[typography.h2, { color: "#1B5E3B" }]}>{reference.reference_number}</Text>
        {reference.voucher_number && <Text style={typography.body}>Voucher: {reference.voucher_number}</Text>}
        <Text style={typography.bodyBold}>Amount: {formatZAR(reference.amount)}</Text>
        {reference.expiry_date && <Caption>Expires: {reference.expiry_date}</Caption>}
        {reference.qr_data && (
          <View style={{ backgroundColor: "#F3F4F6", padding: spacing.lg, borderRadius: 12, alignItems: "center", marginTop: spacing.md }}>
            <Text style={typography.caption}>QR / Barcode</Text>
            <Text style={{ fontFamily: "monospace" }}>{reference.qr_data.slice(0, 40)}...</Text>
          </View>
        )}
        <Caption>Present this reference at Pay@, EasyPay, or your selected retailer</Caption>
      </Card>

      <Button title="Track Transfer" onPress={() => navigation.replace("TransferTracking", { id: transferId })} />
      <Button title="Share via WhatsApp" onPress={shareVoucher} variant="outline" />
      <Button title="View Receipt" onPress={() => navigation.navigate("Receipt", { id: transferId })} variant="secondary" />
      <Button title="Done" onPress={() => navigation.navigate("Tabs")} variant="ghost" />
    </Screen>
  );
}
