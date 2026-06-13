import { useState } from "react";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AlertBanner, Button, Input, Screen, H2 } from "../../components";
import { profileApi } from "../../api";
import { useQueryClient } from "@tanstack/react-query";
import { RootStackParamList } from "../../navigation/MainNavigator";

type Props = NativeStackScreenProps<RootStackParamList, "EditProfile">;

export default function EditProfileScreen({ navigation }: Props) {
  const qc = useQueryClient();
  const [form, setForm] = useState({ address_line1: "", city: "", province: "", postal_code: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const save = async () => {
    setLoading(true);
    try {
      await profileApi.update(form);
      await qc.invalidateQueries({ queryKey: ["profile"] });
      navigation.goBack();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Update failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen scroll>
      <H2>Edit Profile</H2>
      {error ? <AlertBanner type="error" message={error} /> : null}
      <Input label="Address" value={form.address_line1} onChangeText={(v) => setForm({ ...form, address_line1: v })} />
      <Input label="City" value={form.city} onChangeText={(v) => setForm({ ...form, city: v })} />
      <Input label="Province" value={form.province} onChangeText={(v) => setForm({ ...form, province: v })} />
      <Input label="Postal Code" value={form.postal_code} onChangeText={(v) => setForm({ ...form, postal_code: v })} />
      <Button title="Save" onPress={save} loading={loading} />
    </Screen>
  );
}
