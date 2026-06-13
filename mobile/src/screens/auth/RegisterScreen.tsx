import { useState } from "react";
import { Text, ScrollView } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AuthStackParamList } from "../../navigation/AuthNavigator";
import { Screen, Title, Input, Button } from "../../components/ui";
import { useAuthStore } from "../../store/authStore";

type Props = NativeStackScreenProps<AuthStackParamList, "Register">;

export default function RegisterScreen({ navigation }: Props) {
  const { register, loading } = useAuthStore();
  const [form, setForm] = useState({
    mobile_number: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
  });
  const [error, setError] = useState("");

  const submit = async () => {
    setError("");
    try {
      await register({
        ...form,
        email: form.email || undefined,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Registration failed");
    }
  };

  return (
    <Screen>
      <ScrollView>
        <Title>Create Account</Title>
        {error ? <Text style={{ color: "#DC2626" }}>{error}</Text> : null}
        <Input label="Mobile Number" value={form.mobile_number} onChangeText={(v) => setForm({ ...form, mobile_number: v })} keyboardType="phone-pad" placeholder="+27721234567" />
        <Input label="Email (optional)" value={form.email} onChangeText={(v) => setForm({ ...form, email: v })} autoCapitalize="none" keyboardType="email-address" />
        <Input label="First Name" value={form.first_name} onChangeText={(v) => setForm({ ...form, first_name: v })} />
        <Input label="Last Name" value={form.last_name} onChangeText={(v) => setForm({ ...form, last_name: v })} />
        <Input label="Password" value={form.password} onChangeText={(v) => setForm({ ...form, password: v })} secureTextEntry />
        <Button title="Register" onPress={submit} loading={loading} />
        <Button title="Back to Login" variant="outline" onPress={() => navigation.goBack()} />
      </ScrollView>
    </Screen>
  );
}
