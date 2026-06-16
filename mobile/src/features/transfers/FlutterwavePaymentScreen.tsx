import { useEffect, useState } from "react";
import { ActivityIndicator, Linking, Text, View } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useQuery } from "@tanstack/react-query";
import { Ionicons } from "@expo/vector-icons";
import { AlertBanner, Button, FintechCard, Screen } from "../../components";
import { paymentsApi } from "../../api/payments";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { COMPLIANCE } from "../../utils/compliance";

type Props = NativeStackScreenProps<RootStackParamList, "FlutterwavePayment">;

export default function FlutterwavePaymentScreen({ route, navigation }: Props) {
  const { transferId } = route.params;
  const theme = useAppTheme();
  const [error, setError] = useState("");
  const [polling, setPolling] = useState(false);

  const { data: session, isLoading, isError } = useQuery({
    queryKey: ["flutterwave-session", transferId],
    queryFn: async () => (await paymentsApi.flutterwaveSession(transferId)).data,
    retry: 1,
  });

  const { data: status, refetch } = useQuery({
    queryKey: ["payment-status", transferId],
    queryFn: async () => (await paymentsApi.paymentStatus(transferId)).data,
    enabled: polling,
    refetchInterval: polling ? 5000 : false,
  });

  useEffect(() => {
    if (status?.payment_status === "paid" || status?.status === "payment_received") {
      navigation.replace("TransferTracking", { id: transferId });
    }
  }, [status, transferId, navigation]);

  const openPayment = async () => {
    if (!session?.payment_url) return;
    setPolling(true);
    const ok = await Linking.canOpenURL(session.payment_url);
    if (ok) await Linking.openURL(session.payment_url);
    else setError("Unable to open payment page");
  };

  if (isLoading) {
    return (
      <Screen>
        <ActivityIndicator size="large" color={theme.primary} />
        <Text style={[typography.body, { color: theme.textSecondary, textAlign: "center", marginTop: spacing.md }]}>Preparing secure payment…</Text>
      </Screen>
    );
  }

  if (isError || !session) {
    return (
      <Screen scroll>
        <AlertBanner type="error" message="Could not start Flutterwave payment. Try another method or contact support." />
        <Button title="Go back" onPress={() => navigation.goBack()} variant="outline" />
      </Screen>
    );
  }

  return (
    <Screen scroll>
      <View style={{ alignItems: "center", marginBottom: spacing.xl }}>
        <View style={{ width: 64, height: 64, borderRadius: 32, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center" }}>
          <Ionicons name="card-outline" size={32} color={theme.primary} />
        </View>
        <Text style={[typography.h1, { color: theme.text, marginTop: spacing.md }]}>Secure card payment</Text>
        <Text style={[typography.body, { color: theme.textSecondary, textAlign: "center" }]}>Powered by Flutterwave — you will complete payment in a secure browser window.</Text>
      </View>

      {error ? <AlertBanner type="error" message={error} /> : null}

      <FintechCard variant="elevated">
        <Text style={[typography.label, { color: theme.textTertiary }]}>Session reference</Text>
        <Text style={[typography.bodyBold, { color: theme.text }]}>{session.session_ref}</Text>
        <Text style={[typography.caption, { color: theme.textSecondary, marginTop: spacing.sm }]}>Status: {session.status}</Text>
      </FintechCard>

      <Button title="Open secure payment page" onPress={openPayment} variant="gold" />
      <Button title="I've completed payment" onPress={() => { setPolling(true); refetch(); }} variant="primary" loading={polling} />
      <Button title="Cancel" onPress={() => navigation.goBack()} variant="outline" />

      <Text style={[typography.caption, { color: theme.textTertiary, marginTop: spacing.lg, textAlign: "center" }]}>
        {COMPLIANCE.platformDisclaimer} No payment secrets are stored on your device.
      </Text>
    </Screen>
  );
}
