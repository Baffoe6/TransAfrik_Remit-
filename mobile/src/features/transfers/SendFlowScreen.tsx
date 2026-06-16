import { useEffect, useMemo, useState } from "react";
import { FlatList, Text, TextInput, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import {
  AlertBanner,
  Button,
  FintechCard,
  ListItem,
  Screen,
  StepIndicator,
} from "../../components";
import { LiveCalculator } from "../../components/worldclass";
import { beneficiariesApi, paymentsApi, transfersApi } from "../../api";
import { useSendFlowStore } from "../../store/sendFlowStore";
import { useTemplateStore } from "../../store/templateStore";
import { useLiveQuote } from "../../hooks/useLiveQuote";
import { CORRIDORS, PAYOUT_PARTNERS } from "../../utils/constants";
import { formatForeign, formatZAR } from "../../utils/format";
import { radius, spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import type { Beneficiary } from "../../types";
import { useTransferEligibility } from "../../hooks/useTransferEligibility";
import { FLUTTERWAVE_METHOD_CODES, COMPLIANCE } from "../../utils/compliance";
import { hapticSuccess } from "../../services/haptics";

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
  const saveTemplate = useTemplateStore((s) => s.saveTemplate);
  const theme = useAppTheme();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [templateName, setTemplateName] = useState("");

  const eligibility = useTransferEligibility();

  const { data: beneficiaries = [] } = useQuery({
    queryKey: ["beneficiaries"],
    queryFn: async () => (await beneficiariesApi.list()).data,
  });

  const { data: methods = [] } = useQuery({
    queryKey: ["payment-methods"],
    queryFn: async () => (await paymentsApi.methods()).data,
    enabled: flow.step >= 3,
  });

  const flutterwaveMethods = useMemo(
    () => methods.filter((m) => FLUTTERWAVE_METHOD_CODES.has(m.code.toLowerCase())),
    [methods],
  );

  useEffect(() => {
    if (flow.step >= 4 && flutterwaveMethods.length === 1 && !flow.paymentMethod) {
      flow.setPaymentMethod(flutterwaveMethods[0]);
    }
  }, [flow.step, flutterwaveMethods, flow.paymentMethod, flow]);

  const { data: liveQuote } = useLiveQuote(flow.amount, flow.destinationCountry, flow.step === 2 || flow.step === 5);

  useEffect(() => {
    if (liveQuote && (flow.step === 2 || flow.step === 5)) flow.setQuote(liveQuote);
  }, [liveQuote, flow.step]);

  useEffect(() => () => useSendFlowStore.getState().reset(), []);

  const filteredBeneficiaries = beneficiaries.filter(
    (b) =>
      (b.country === flow.destinationCountry || flow.destinationCountry === "GH") &&
      b.status !== "rejected",
  );
  const partner = PAYOUT_PARTNERS.find((p) => (p.corridors as readonly string[]).includes(flow.destinationCountry));
  const corridor = CORRIDORS.find((c) => c.code === flow.corridorCode);

  const confirm = async () => {
    if (!flow.beneficiary || !flow.paymentMethod) return;
    if (!eligibility.canTransfer) {
      setError(eligibility.blockers.join(" · "));
      return;
    }
    setLoading(true);
    setError("");
    try {
      const { data } = await transfersApi.create({
        beneficiary_id: flow.beneficiary.id,
        send_amount_zar: flow.amount,
        payment_method_code: flow.paymentMethod.code,
      });
      flow.setTransferId(data.id);
      hapticSuccess();
      navigation.replace("FlutterwavePayment", { transferId: data.id });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Transfer failed");
    } finally {
      setLoading(false);
    }
  };

  const next = async () => {
    if (flow.step === 2) {
      const numeric = parseFloat(flow.amount);
      if (Number.isNaN(numeric) || numeric < 50) {
        setError("Minimum send amount is R50");
        return;
      }
      if (!flow.quote && !liveQuote) {
        setError("Waiting for live quote…");
        return;
      }
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

  const handleSaveTemplate = async () => {
    if (!flow.beneficiary || !templateName.trim()) return;
    await saveTemplate({
      name: templateName.trim(),
      beneficiaryId: flow.beneficiary.id,
      beneficiaryName: flow.beneficiary.full_name,
      amount: flow.amount,
      corridorCode: flow.corridorCode,
      destinationCountry: flow.destinationCountry,
      currency: flow.currency,
    });
    setTemplateName("");
    hapticSuccess();
  };

  return (
    <Screen scroll>
      <StepIndicator step={flow.step} total={5} />
      <Text style={[typography.label, { color: theme.textTertiary, marginBottom: 4 }]}>Step {flow.step} of 5</Text>
      <Text style={[typography.h1, { color: theme.text, marginBottom: spacing.lg }]}>{STEP_LABELS[flow.step - 1]}</Text>
      {error ? <AlertBanner type="error" message={error} /> : null}
      {!eligibility.canTransfer && !eligibility.isLoading ? (
        <FintechCard variant="accent">
          <Text style={[typography.bodyBold, { color: theme.text, marginBottom: spacing.sm }]}>Complete before sending</Text>
          {eligibility.blockers.map((b) => (
            <Text key={b} style={[typography.caption, { color: theme.textSecondary }]}>• {b}</Text>
          ))}
          {eligibility.blockers.some((b) => b.includes("KYC")) ? (
            <Button title="Complete identity verification" onPress={() => navigation.navigate("Kyc")} variant="outline" style={{ marginTop: spacing.sm }} />
          ) : null}
        </FintechCard>
      ) : null}

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
        <LiveCalculator
          amount={flow.amount}
          onAmountChange={flow.setAmount}
          destinationCountry={flow.destinationCountry}
          currency={flow.currency}
          corridorCode={flow.corridorCode}
        />
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
          <Text style={[typography.body, { color: theme.textSecondary, marginBottom: spacing.md }]}>
            Pay securely via Flutterwave — card, bank transfer, Capitec Pay, 1Voucher and more.
          </Text>
          {flutterwaveMethods.map((m) => (
            <SelectableRow key={m.id} selected={flow.paymentMethod?.id === m.id} onPress={() => flow.setPaymentMethod(m)}>
              <View style={{ width: 44, height: 44, borderRadius: radius.md, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center", marginRight: spacing.md }}>
                <Ionicons name="card" size={22} color={theme.primary} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={typography.bodyBold}>{m.name}</Text>
                <Text style={[typography.caption, { color: theme.textSecondary }]}>
                  {m.description ?? "Card, EFT, Capitec Pay, 1Voucher via Flutterwave"}
                </Text>
              </View>
            </SelectableRow>
          ))}
          {flutterwaveMethods.length === 0 && (
            <Text style={{ color: theme.textSecondary }}>Flutterwave checkout is temporarily unavailable. Please try again later.</Text>
          )}
        </>
      )}

      {flow.step === 5 && flow.quote && flow.beneficiary && flow.paymentMethod && (
        <FintechCard variant="elevated">
          <Text style={[typography.label, { color: theme.textTertiary, marginBottom: spacing.md }]}>Transfer summary</Text>
          <ListItem title={flow.beneficiary.full_name} subtitle="Recipient" avatarName={flow.beneficiary.full_name} showChevron={false} style={{ paddingHorizontal: 0, backgroundColor: "transparent" }} />
          <View style={{ gap: spacing.sm, marginTop: spacing.md }}>
            <Row label="You send" value={formatZAR(flow.quote.send_amount_zar)} />
            <Row label="Fee" value={formatZAR(flow.quote.fee_zar)} />
            <Row label="Rate" value={`1 ZAR = ${flow.quote.exchange_rate} ${flow.currency}`} />
            <Row label="They receive" value={formatForeign(flow.quote.receive_amount_ghs, flow.currency)} highlight />
            <Row label="Payment" value={flow.paymentMethod.name} />
            <Row label="Delivery" value={corridor?.eta ?? "Same day"} />
          </View>
          {partner && (
            <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginTop: spacing.md, padding: spacing.sm, backgroundColor: theme.primaryMuted, borderRadius: radius.md }}>
              <Ionicons name="shield-checkmark" size={16} color={theme.primary} />
              <Text style={[typography.caption, { color: theme.text }]}>Payout via {partner.name}</Text>
            </View>
          )}
          <View style={{ marginTop: spacing.lg, gap: spacing.sm }}>
            <Text style={[typography.caption, { color: theme.textSecondary }]}>Save as template</Text>
            <TextInput
              value={templateName}
              onChangeText={setTemplateName}
              placeholder="e.g. Monthly rent — Ghana"
              placeholderTextColor={theme.textTertiary}
              style={{ borderWidth: 1, borderColor: theme.border, borderRadius: radius.md, padding: spacing.md, color: theme.text }}
            />
            <Button title="Save template" onPress={handleSaveTemplate} variant="outline" disabled={!templateName.trim()} />
          </View>
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
