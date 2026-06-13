import { useEffect, useState } from "react";
import { ScrollView, Text } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { Screen, Input, Button } from "../../components/ui";
import { beneficiariesApi } from "../../api";
import { MOBILE_MONEY_PROVIDERS } from "../../types";
import { useQueryClient } from "@tanstack/react-query";

type Props = NativeStackScreenProps<RootStackParamList, "BeneficiaryForm">;

export default function BeneficiaryFormScreen({ route, navigation }: Props) {
  const id = route.params?.id;
  const qc = useQueryClient();
  const [form, setForm] = useState({
    full_name: "",
    mobile_wallet_number: "",
    mobile_money_provider: MOBILE_MONEY_PROVIDERS[0],
    relationship_to_sender: "",
    country: "GH",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (id) {
      beneficiariesApi.get(id).then(({ data }) => {
        setForm({
          full_name: data.full_name,
          mobile_wallet_number: data.mobile_wallet_number || "",
          mobile_money_provider: data.mobile_money_provider || MOBILE_MONEY_PROVIDERS[0],
          relationship_to_sender: data.relationship_to_sender,
          country: data.country,
        });
      });
    }
  }, [id]);

  const save = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        beneficiary_type: "mobile_money",
        ...form,
      };
      if (id) await beneficiariesApi.update(id, payload);
      else await beneficiariesApi.create(payload);
      qc.invalidateQueries({ queryKey: ["beneficiaries"] });
      navigation.goBack();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <ScrollView>
        {error ? <Text style={{ color: "#DC2626" }}>{error}</Text> : null}
        <Input label="Full Name" value={form.full_name} onChangeText={(v) => setForm({ ...form, full_name: v })} />
        <Input label="Mobile Number" value={form.mobile_wallet_number} onChangeText={(v) => setForm({ ...form, mobile_wallet_number: v })} keyboardType="phone-pad" placeholder="+233..." />
        <Input label="Provider" value={form.mobile_money_provider} onChangeText={(v) => setForm({ ...form, mobile_money_provider: v })} />
        <Input label="Relationship" value={form.relationship_to_sender} onChangeText={(v) => setForm({ ...form, relationship_to_sender: v })} />
        <Button title={id ? "Update" : "Add"} onPress={save} loading={loading} />
      </ScrollView>
    </Screen>
  );
}
