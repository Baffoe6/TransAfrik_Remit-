import { useState } from "react";
import { ScrollView, Text } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Screen, Input, Button, Muted } from "../../components/ui";
import { beneficiariesApi, transfersApi } from "../../api";
import { useNavigation } from "@react-navigation/native";

export default function CreateTransferScreen() {
  const navigation = useNavigation();
  const [amount, setAmount] = useState("1000");
  const [beneficiaryId, setBeneficiaryId] = useState<number | null>(null);
  const [quote, setQuote] = useState<Record<string, string> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const { data: beneficiaries = [] } = useQuery({
    queryKey: ["beneficiaries"],
    queryFn: async () => (await beneficiariesApi.list()).data,
  });

  const calculate = async () => {
    const { data } = await transfersApi.calculate(amount);
    setQuote(data as Record<string, string>);
  };

  const submit = async () => {
    if (!beneficiaryId) {
      setError("Select a beneficiary");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await transfersApi.create({
        beneficiary_id: beneficiaryId,
        send_amount_zar: amount,
      });
      navigation.goBack();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create transfer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <ScrollView>
        <Input label="Amount (ZAR)" value={amount} onChangeText={setAmount} keyboardType="decimal-pad" />
        <Button title="Get Quote" variant="outline" onPress={calculate} />
        {quote && (
          <Muted>
            Fee: R{quote.fee_zar} · Rate: {quote.exchange_rate} · Receive: {quote.receive_amount_ghs} GHS
          </Muted>
        )}
        <Muted>Select beneficiary:</Muted>
        {beneficiaries.map((b) => (
          <Button
            key={b.id}
            title={b.full_name}
            variant={beneficiaryId === b.id ? "primary" : "outline"}
            onPress={() => setBeneficiaryId(b.id)}
          />
        ))}
        {error ? <Text style={{ color: "#DC2626" }}>{error}</Text> : null}
        <Button title="Create Transfer" onPress={submit} loading={loading} />
      </ScrollView>
    </Screen>
  );
}
