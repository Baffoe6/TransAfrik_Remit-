import { useEffect, useState } from "react";
import { FlatList, Text, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AlertBanner, Body, Button, Caption, Card, H2, Input, Screen, StepIndicator } from "../../components";
import { beneficiariesApi, paymentsApi, transfersApi } from "../../api";
import { useSendFlowStore } from "../../store/sendFlowStore";
import { CORRIDORS } from "../../utils/constants";
import { formatForeign, formatZAR } from "../../utils/format";
import { spacing } from "../../theme/spacing";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import type { Beneficiary } from "../../types";

type Props = NativeStackScreenProps<RootStackParamList, "SendFlow">;

export default function SendFlowScreen({ navigation }: Props) {
  const flow = useSendFlowStore();
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
      setError("Select a beneficiary");
      return;
    }
    if (flow.step === 4 && !flow.paymentMethod) {
      setError("Select a payment method");
      return;
    }
    if (flow.step < 5) flow.setStep(flow.step + 1);
    else confirm();
  };

  return (
    <Screen scroll>
      <StepIndicator step={flow.step} total={5} />
      <H2>Send Money</H2>
      <Caption>Step {flow.step} of 5</Caption>
      {error ? <AlertBanner type="error" message={error} /> : null}

      {flow.step === 1 && (
        <>
          <Body muted>Select destination country</Body>
          {CORRIDORS.map((c) => (
            <TouchableOpacity
              key={c.code}
              onPress={() => flow.setDestination(c.country, c.code, c.currency)}
              style={{ padding: spacing.md, borderWidth: flow.corridorCode === c.code ? 2 : 1, borderColor: flow.corridorCode === c.code ? "#1B5E3B" : "#E5E7EB", borderRadius: 12, marginBottom: spacing.sm, flexDirection: "row", alignItems: "center", gap: 12 }}
            >
              <Text style={{ fontSize: 28 }}>{c.flag}</Text>
              <View>
                <Text style={typography.bodyBold}>{c.name}</Text>
                <Caption>{c.currency} · {c.eta}</Caption>
              </View>
            </TouchableOpacity>
          ))}
        </>
      )}

      {flow.step === 2 && (
        <>
          <Input label="Amount (ZAR)" value={flow.amount} onChangeText={flow.setAmount} keyboardType="decimal-pad" />
          <Button title="Get Live Quote" onPress={fetchQuote} variant="outline" loading={loading} />
          {flow.quote && (
            <Card>
              <Caption>You send</Caption>
              <Text style={typography.amount}>{formatZAR(flow.quote.send_amount_zar)}</Text>
              <Caption>Fee: {formatZAR(flow.quote.fee_zar)} · Rate: {flow.quote.exchange_rate}</Caption>
              <Caption>Recipient gets: {formatForeign(flow.quote.receive_amount_ghs, flow.currency)}</Caption>
            </Card>
          )}
        </>
      )}

      {flow.step === 3 && (
        <>
          <Body muted>Select beneficiary</Body>
          {filteredBeneficiaries.map((b: Beneficiary) => (
            <TouchableOpacity key={b.id} onPress={() => flow.setBeneficiary(b)} style={{ padding: spacing.md, borderWidth: flow.beneficiary?.id === b.id ? 2 : 1, borderColor: flow.beneficiary?.id === b.id ? "#1B5E3B" : "#E5E7EB", borderRadius: 12, marginBottom: spacing.sm }}>
              <Text style={typography.bodyBold}>{b.full_name}</Text>
              <Caption>{b.beneficiary_type} · {b.mobile_wallet_number ?? b.bank_account_number ?? "—"}</Caption>
            </TouchableOpacity>
          ))}
          <Button title="Add New Beneficiary" onPress={() => navigation.navigate("BeneficiaryForm", {})} variant="outline" />
        </>
      )}

      {flow.step === 4 && (
        <>
          <Body muted>Choose payment method</Body>
          {methods.map((m) => (
            <TouchableOpacity key={m.id} onPress={() => flow.setPaymentMethod(m)} style={{ padding: spacing.md, borderWidth: flow.paymentMethod?.id === m.id ? 2 : 1, borderColor: flow.paymentMethod?.id === m.id ? "#1B5E3B" : "#E5E7EB", borderRadius: 12, marginBottom: spacing.sm }}>
              <Text style={typography.bodyBold}>{m.name}</Text>
              <Caption>{m.description ?? m.provider}</Caption>
            </TouchableOpacity>
          ))}
          <Card><Caption>Flutterwave card/link — coming soon</Caption></Card>
        </>
      )}

      {flow.step === 5 && flow.quote && flow.beneficiary && flow.paymentMethod && (
        <Card elevated>
          <Caption>Review transfer</Caption>
          <Text style={typography.bodyBold}>To: {flow.beneficiary.full_name}</Text>
          <Text style={typography.body}>Send: {formatZAR(flow.quote.send_amount_zar)}</Text>
          <Text style={typography.body}>Fee: {formatZAR(flow.quote.fee_zar)}</Text>
          <Text style={typography.body}>Rate: {flow.quote.exchange_rate}</Text>
          <Text style={typography.body}>Gets: {formatForeign(flow.quote.receive_amount_ghs, flow.currency)}</Text>
          <Text style={typography.body}>Pay via: {flow.paymentMethod.name}</Text>
          <Caption>Est. delivery: Same day · Processed via licensed partners. TransAfrik is not a bank.</Caption>
        </Card>
      )}

      <View style={{ flexDirection: "row", gap: spacing.sm, marginTop: spacing.lg }}>
        {flow.step > 1 && <Button title="Back" onPress={() => flow.setStep(flow.step - 1)} variant="outline" style={{ flex: 1 }} />}
        <Button title={flow.step === 5 ? "Confirm & Pay" : "Continue"} onPress={next} loading={loading} style={{ flex: 2 }} disabled={flow.step === 1 && !flow.corridorCode} />
      </View>
    </Screen>
  );
}
