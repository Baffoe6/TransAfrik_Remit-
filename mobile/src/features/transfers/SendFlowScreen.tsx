import { useEffect, useState } from "react";
import { FlatList, Text, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import {
  AlertBanner,
  AmountDisplay,
  Button,
  FintechCard,
  Input,
  ListItem,
  Screen,
  StepIndicator,
} from "../../components";
import { beneficiariesApi, paymentsApi, transfersApi } from "../../api";
import { useSendFlowStore } from "../../store/sendFlowStore";
import { CORRIDORS } from "../../utils/constants";
import { formatForeign, formatZAR } from "../../utils/format";
import { radius, spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import type { Beneficiary } from "../../types";

type Props = NativeStackScreenProps<RootStackParamList, "SendFlow">;

const STEP_LABELS = ["Corridor", "Amount", "Recipient", "Payment", "Review"];

function SelectableRow({
  selected,
  onPress,
  children,
}: {
  selected: boolean;
  onPress: () => void;
  children: React.ReactNode;
}) {
  const theme = useAppTheme();
  return (
    <TouchableOpacity
      onPress={onPress}
      activeOpacity={0.75}
      style={{
        padding: spacing.md,
        borderWidth: selected ? 2 : 1,
        borderColor: selected ? theme.primary : theme.border,
        borderRadius: radius.lg,
        marginBottom: spacing.sm,
        backgroundColor: selected ? theme.primaryMuted : theme.surface,
        flexDirection: "row",
        alignItems: "center",
      }}
    >
      {children}
      {selected ? <Ionicons name="checkmark-circle" size={22} color={theme.primary} style={{ marginLeft: "auto" }} /> : null}
    </TouchableOpacity>
  );
}

export default function SendFlowScreen({ navigation }: Props) {
  const flow = useSendFlowStore();
  const theme = useAppTheme();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { data: beneficiaries = [] } = useQuery({
    queryKey: ["beneficiaries"],
    queryFn: async () => (await beneficiariesApi.list()).data,
  });

  const { data: methods = [] } = useQuery({
    queryKey: ["payment-methods"],
    queryFn: async () => (await paymentsApi.methods()).data,
    enabled: flow.step >= 4,
  });

  useEffect(() => () => useSendFlowStore.getState().reset(), []);

  const filteredBeneficiaries = beneficiaries.filter((b) => b.country === flow.destinationCountry || flow.destinationCountry === "GH");

  const fetchQuote = async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await transfersApi.calculate(flow.amount, flow.destinationCountry);
      flow.setQuote(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Quote failed");
    } finally {
      setLoading(false);
    }
  };

  const confirm = async () => {
    if (!flow.beneficiary || !flow.paymentMethod) return;
    setLoading(true);
    setError("");
    try {
      const { data } = await transfersApi.create({
        beneficiary_id: flow.beneficiary.id,
        send_amount_zar: flow.amount,
        payment_method_code: flow.paymentMethod.code,
      });
      const { data: ref } = await paymentsApi.generate(data.id, flow.paymentMethod.code);
      flow.setTransferId(data.id);
      navigation.replace("PaymentSuccess", { transferId: data.id, reference: ref });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Transfer failed");
    } finally {
      setLoading(false);
    }
  };

  const next = async () => {
    if (flow.step === 2 && !flow.quote) {
      await fetchQuote();
      if (!useSendFlowStore.getState().quote) return;
    }
    if (flow.step === 3 && !flow.beneficiary) {
      setError("Select a recipient");
      return;
    }
    if (flow.step === 4 && !flow.paymentMethod) {
      setError("Select a payment method");
      return;
    }
    setError("");
    if (flow.step < 5) flow.setStep(flow.step + 1);
    else confirm();
  };

  return (
    <Screen scroll>
      <StepIndicator step={flow.step} total={5} />
      <Text style={[typography.label, { color: theme.textTertiary, marginBottom: 4 }]}>Step {flow.step} of 5</Text>
      <Text style={[typography.h1, { color: theme.text, marginBottom: spacing.lg }]}>{STEP_LABELS[flow.step - 1]}</Text>
      {error ? <AlertBanner type="error" message={error} /> : null}

      {flow.step === 1 && (
        <>
          <Text style={[typography.body, { color: theme.textSecondary, marginBottom: spacing.md }]}>Where are you sending money?</Text>
          {CORRIDORS.map((c) => (
            <SelectableRow key={c.code} selected={flow.corridorCode === c.code} onPress={() => flow.setDestination(c.country, c.code, c.currency)}>
              <Text style={{ fontSize: 32, marginRight: spacing.md }}>{c.flag}</Text>
              <View style={{ flex: 1 }}>
                <Text style={typography.bodyBold}>{c.name}</Text>
                <Text style={[typography.caption, { color: theme.textSecondary }]}>{c.currency} · {c.eta}</Text>
              </View>
            </SelectableRow>
          ))}
        </>
      )}

      {flow.step === 2 && (
        <>
          <FintechCard variant="elevated">
            <Input label="You send (ZAR)" value={flow.amount} onChangeText={flow.setAmount} keyboardType="decimal-pad" />
            <Button title="Get live quote" onPress={fetchQuote} variant="outline" loading={loading} />
          </FintechCard>
          {flow.quote && (
            <FintechCard variant="hero" padding="lg">
              <AmountDisplay label="You send" amount={formatZAR(flow.quote.send_amount_zar)} light />
              <View style={{ height: 1, backgroundColor: "rgba(255,255,255,0.2)", marginVertical: spacing.md }} />
              <AmountDisplay label="They receive" amount={formatForeign(flow.quote.receive_amount_ghs, flow.currency)} sublabel={`Fee ${formatZAR(flow.quote.fee_zar)} · Rate ${flow.quote.exchange_rate}`} size="sm" light />
            </FintechCard>
          )}
        </>
      )}

      {flow.step === 3 && (
        <>
          <FlatList
            data={filteredBeneficiaries}
            keyExtractor={(b) => String(b.id)}
            scrollEnabled={false}
            renderItem={({ item }: { item: Beneficiary }) => (
              <SelectableRow selected={flow.beneficiary?.id === item.id} onPress={() => flow.setBeneficiary(item)}>
                <View style={{ flex: 1 }}>
                  <Text style={typography.bodyBold}>{item.full_name}</Text>
                  <Text style={[typography.caption, { color: theme.textSecondary }]}>{item.beneficiary_type.replace("_", " ")} · {item.mobile_wallet_number ?? item.bank_account_number ?? "—"}</Text>
                </View>
              </SelectableRow>
            )}
            ListEmptyComponent={<Text style={{ color: theme.textSecondary, marginBottom: spacing.md }}>No recipients for this corridor</Text>}
          />
          <Button title="Add new recipient" onPress={() => navigation.navigate("BeneficiaryForm", {})} variant="outline" />
        </>
      )}

      {flow.step === 4 && (
        <>
          {methods.map((m) => (
            <SelectableRow key={m.id} selected={flow.paymentMethod?.id === m.id} onPress={() => flow.setPaymentMethod(m)}>
              <View style={{ width: 44, height: 44, borderRadius: radius.md, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center", marginRight: spacing.md }}>
                <Ionicons name="card" size={22} color={theme.primary} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={typography.bodyBold}>{m.name}</Text>
                <Text style={[typography.caption, { color: theme.textSecondary }]}>{m.description ?? m.provider}</Text>
              </View>
            </SelectableRow>
          ))}
        </>
      )}

      {flow.step === 5 && flow.quote && flow.beneficiary && flow.paymentMethod && (
        <FintechCard variant="elevated">
          <Text style={[typography.label, { color: theme.textTertiary, marginBottom: spacing.md }]}>Transfer summary</Text>
          <ListItem title={flow.beneficiary.full_name} subtitle="Recipient" avatarName={flow.beneficiary.full_name} showChevron={false} style={{ paddingHorizontal: 0, backgroundColor: "transparent" }} />
          <View style={{ gap: spacing.sm, marginTop: spacing.md }}>
            <Row label="You send" value={formatZAR(flow.quote.send_amount_zar)} />
            <Row label="Fee" value={formatZAR(flow.quote.fee_zar)} />
            <Row label="Rate" value={String(flow.quote.exchange_rate)} />
            <Row label="They receive" value={formatForeign(flow.quote.receive_amount_ghs, flow.currency)} highlight />
            <Row label="Payment" value={flow.paymentMethod.name} />
          </View>
          <Text style={[typography.caption, { color: theme.textTertiary, marginTop: spacing.md }]}>Est. same-day delivery · Processed via licensed partners</Text>
        </FintechCard>
      )}

      <View style={{ flexDirection: "row", gap: spacing.sm, marginTop: spacing.lg }}>
        {flow.step > 1 && <Button title="Back" onPress={() => flow.setStep(flow.step - 1)} variant="outline" style={{ flex: 1 }} />}
        <Button title={flow.step === 5 ? "Confirm & pay" : "Continue"} onPress={next} loading={loading} style={{ flex: 2 }} disabled={flow.step === 1 && !flow.corridorCode} />
      </View>
    </Screen>
  );
}

function Row({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  const theme = useAppTheme();
  return (
    <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
      <Text style={[typography.caption, { color: theme.textSecondary }]}>{label}</Text>
      <Text style={[highlight ? typography.bodyBold : typography.body, { color: highlight ? theme.primary : theme.text }]}>{value}</Text>
    </View>
  );
}
