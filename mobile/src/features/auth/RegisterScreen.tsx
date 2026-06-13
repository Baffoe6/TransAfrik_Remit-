import { useState } from "react";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AlertBanner, Button, Input, PinInput, Screen, H2, Caption } from "../../components";
import { useAuthStore } from "../../store/authStore";
import { normalizePhone } from "../../utils/phone";
import { isValidMobile, isValidPin } from "../../utils/validation";
import { AuthStackParamList } from "../../navigation/AuthNavigator";

type Props = NativeStackScreenProps<AuthStackParamList, "Register">;

export default function RegisterScreen({ navigation }: Props) {
  const { register, loading } = useAuthStore();
  const [form, setForm] = useState({ mobile_number: "", email: "", first_name: "", last_name: "", pin: "", invite_code: "" });
  const [error, setError] = useState("");

  const submit = async () => {
    setError("");
    if (!isValidMobile(form.mobile_number)) return setError("Enter a valid mobile number");
    if (!isValidPin(form.pin)) return setError("PIN must be 4–6 digits");
    try {
      await register({
        mobile_number: normalizePhone(form.mobile_number),
        password: form.pin,
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email || undefined,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Registration failed");
    }
  };

  return (
    <Screen scroll>
      <H2>Create Account</H2>
      <Caption>Mobile number required · PIN is your secure login</Caption>
      {error ? <AlertBanner type="error" message={error} /> : null}
      <Input label="Mobile Number *" value={form.mobile_number} onChangeText={(v) => setForm({ ...form, mobile_number: v })} keyboardType="phone-pad" placeholder="+27..." />
      <Input label="First Name *" value={form.first_name} onChangeText={(v) => setForm({ ...form, first_name: v })} />
      <Input label="Last Name *" value={form.last_name} onChangeText={(v) => setForm({ ...form, last_name: v })} />
      <Input label="Email (optional)" value={form.email} onChangeText={(v) => setForm({ ...form, email: v })} autoCapitalize="none" keyboardType="email-address" />
      <PinInput label="Create 4-digit PIN *" value={form.pin} onChange={(pin) => setForm({ ...form, pin })} />
      <Input label="Invite Code (if required)" value={form.invite_code} onChangeText={(v) => setForm({ ...form, invite_code: v })} hint="Required during pilot launch" />
      <Button title="Create Account" onPress={submit} loading={loading} />
      <Button title="Already have an account?" onPress={() => navigation.goBack()} variant="ghost" />
    </Screen>
  );
}
