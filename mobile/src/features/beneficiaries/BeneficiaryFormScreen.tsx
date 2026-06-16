import { useEffect, useState } from "react";
import { ScrollView, Text, TouchableOpacity } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useQueryClient } from "@tanstack/react-query";
import { AlertBanner, Button, Input, Screen, H2, Caption } from "../../components";
import { beneficiariesApi } from "../../api";
import { GHANA_MM_PROVIDERS, RELATIONSHIPS } from "../../utils/constants";
import { isValidGhanaMobile } from "../../utils/validation";
import { RootStackParamList } from "../../navigation/MainNavigator";
import type { BeneficiaryType } from "../../types";

type Props = NativeStackScreenProps<RootStackParamList, "BeneficiaryForm">;

export default function BeneficiaryFormScreen({ navigation, route }: Props) {
  const id = route.params?.id;
  const qc = useQueryClient();
  const [type, setType] = useState<BeneficiaryType>("mobile_money");
  const [form, setForm] = useState({
    full_name: "",
    country: "GH",
    relationship_to_sender: "Family",
    mobile_money_provider: "MTN Ghana",
    mobile_wallet_number: "",
    bank_name: "",
    bank_account_number: "",
    city: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    beneficiariesApi.get(id).then(({ data }) => {
      setType(data.beneficiary_type);
      setForm({
        full_name: data.full_name,
        country: data.country,
        relationship_to_sender: data.relationship_to_sender,
        mobile_money_provider: data.mobile_money_provider ?? "MTN Ghana",
        mobile_wallet_number: data.mobile_wallet_number ?? "",
        bank_name: data.bank_name ?? "",
        bank_account_number: data.bank_account_number ?? "",
        city: "",
      });
    });
  }, [id]);

  const save = async () => {
    setLoading(true);
    setError("");
    if (!form.full_name.trim()) { setError("Full name is required"); setLoading(false); return; }
    if (type === "mobile_money" && form.mobile_wallet_number && !isValidGhanaMobile(form.mobile_wallet_number)) {
      setError("Enter a valid Ghana mobile money number");
      setLoading(false);
      return;
    }
    const payload = { beneficiary_type: type, ...form, relationship_to_sender: form.relationship_to_sender };
    try {
      if (id) await beneficiariesApi.update(id, payload);
      else await beneficiariesApi.create(payload);
      await qc.invalidateQueries({ queryKey: ["beneficiaries"] });
      navigation.goBack();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setLoading(false);
    }
  };

  const remove = async () => {
    if (!id) return;
    await beneficiariesApi.remove(id);
    await qc.invalidateQueries({ queryKey: ["beneficiaries"] });
    navigation.goBack();
  };

  return (
    <Screen scroll>
      <H2>{id ? "Edit" : "Add"} Beneficiary</H2>
      {error ? <AlertBanner type="error" message={error} /> : null}

      <Caption>Type</Caption>
      {(["mobile_money", "bank_account", "cash_pickup"] as BeneficiaryType[]).map((t) => (
        <TouchableOpacity key={t} onPress={() => setType(t)} style={{ padding: 12, borderWidth: type === t ? 2 : 1, borderColor: type === t ? "#1B5E3B" : "#E5E7EB", borderRadius: 8, marginBottom: 8 }}>
          <Text style={{ fontWeight: "600", textTransform: "capitalize" }}>{t.replace("_", " ")}</Text>
        </TouchableOpacity>
      ))}

      <Input label="Full Name" value={form.full_name} onChangeText={(v) => setForm({ ...form, full_name: v })} />
      <Input label="Country Code" value={form.country} onChangeText={(v) => setForm({ ...form, country: v })} />
      <Input label="Relationship" value={form.relationship_to_sender} onChangeText={(v) => setForm({ ...form, relationship_to_sender: v })} />

      {type === "mobile_money" && (
        <>
          <Caption>Mobile Money Provider</Caption>
          {GHANA_MM_PROVIDERS.map((p) => (
            <TouchableOpacity key={p.id} onPress={() => setForm({ ...form, mobile_money_provider: p.label })} style={{ padding: 10, marginBottom: 4 }}>
              <Text style={{ fontWeight: form.mobile_money_provider === p.label ? "700" : "400" }}>{p.label}</Text>
            </TouchableOpacity>
          ))}
          <Input label="Mobile Wallet Number" value={form.mobile_wallet_number} onChangeText={(v) => setForm({ ...form, mobile_wallet_number: v })} keyboardType="phone-pad" />
        </>
      )}

      {type === "bank_account" && (
        <>
          <Input label="Bank Name" value={form.bank_name} onChangeText={(v) => setForm({ ...form, bank_name: v })} />
          <Input label="Account Number" value={form.bank_account_number} onChangeText={(v) => setForm({ ...form, bank_account_number: v })} />
        </>
      )}

      {type === "cash_pickup" && <Input label="Pickup City" value={form.city} onChangeText={(v) => setForm({ ...form, city: v })} />}

      <Button title="Save Beneficiary" onPress={save} loading={loading} />
      {id ? <Button title="Delete" onPress={remove} variant="danger" /> : null}
    </Screen>
  );
}
