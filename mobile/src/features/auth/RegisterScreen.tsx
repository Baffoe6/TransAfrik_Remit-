import { useState } from "react";
import { Linking, Switch, Text, View } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AlertBanner, Button, FintechCard, Input, PinInput, Screen } from "../../components";
import { profileApi } from "../../api/dashboard";
import { useAuthStore } from "../../store/authStore";
import { authApi } from "../../api/auth";
import { COMPLIANCE } from "../../utils/compliance";
import { normalizePhone } from "../../utils/phone";
import { isValidDateOfBirth, isValidEmail, isValidMobile, isValidPin } from "../../utils/validation";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { AuthStackParamList } from "../../navigation/AuthNavigator";

type Props = NativeStackScreenProps<AuthStackParamList, "Register">;

export default function RegisterScreen({ navigation }: Props) {
  const theme = useAppTheme();
  const register = useAuthStore((s) => s.register);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [acceptPopia, setAcceptPopia] = useState(false);
  const [form, setForm] = useState({
    mobile_number: "",
    email: "",
    first_name: "",
    last_name: "",
    date_of_birth: "",
    pin: "",
    confirm_pin: "",
  });

  const submit = async () => {
    setError("");
    if (!form.first_name.trim() || !form.last_name.trim()) return setError("First and last name are required");
    if (!isValidMobile(form.mobile_number)) return setError("Enter a valid mobile number");
    if (!isValidPin(form.pin)) return setError("PIN must be 4 digits");
    if (form.pin !== form.confirm_pin) return setError("PINs do not match");
    if (form.email && !isValidEmail(form.email)) return setError("Enter a valid email address");
    if (form.date_of_birth && !isValidDateOfBirth(form.date_of_birth)) return setError("Enter date of birth as YYYY-MM-DD (18+)");
    if (!acceptTerms || !acceptPopia) return setError("Please accept POPIA and Terms & Conditions");

    setLoading(true);
    try {
      await register({
        mobile_number: normalizePhone(form.mobile_number),
        pin: form.pin,
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        email: form.email.trim() || undefined,
        accept_popia: acceptPopia,
        accept_terms: acceptTerms,
      });
      if (form.date_of_birth) {
        try {
          await profileApi.update({ date_of_birth: form.date_of_birth });
        } catch {
          /* profile patch is best-effort after register */
        }
      }
      try {
        await authApi.sendOtp(normalizePhone(form.mobile_number), "sms", "verify_phone");
      } catch {
        /* OTP provider may not be configured — user can resend on verify screen */
      }
      navigation.replace("VerifyPhone");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen scroll>
      <Text style={[typography.h1, { color: theme.text }]}>Create your account</Text>
      <Text style={[typography.body, { color: theme.textSecondary, marginBottom: spacing.lg }]}>
        Your mobile number and 4-digit PIN are your login. {COMPLIANCE.pilotAccess}
      </Text>
      {error ? <AlertBanner type="error" message={error} /> : null}

      <Input label="Mobile number *" value={form.mobile_number} onChangeText={(v) => setForm({ ...form, mobile_number: v })} keyboardType="phone-pad" placeholder="+27 82 123 4567" />
      <Input label="First name *" value={form.first_name} onChangeText={(v) => setForm({ ...form, first_name: v })} />
      <Input label="Last name *" value={form.last_name} onChangeText={(v) => setForm({ ...form, last_name: v })} />
      <Input label="Email (optional)" value={form.email} onChangeText={(v) => setForm({ ...form, email: v })} autoCapitalize="none" keyboardType="email-address" />
      <Input label="Date of birth (YYYY-MM-DD)" value={form.date_of_birth} onChangeText={(v) => setForm({ ...form, date_of_birth: v })} placeholder="1990-01-15" />
      <PinInput label="4-digit PIN *" value={form.pin} onChange={(v) => setForm({ ...form, pin: v })} length={4} />
      <PinInput label="Confirm PIN *" value={form.confirm_pin} onChange={(v) => setForm({ ...form, confirm_pin: v })} length={4} />

      <FintechCard variant="muted" style={{ marginVertical: spacing.md }}>
        <ConsentRow label={COMPLIANCE.termsAcceptance} value={acceptTerms} onChange={setAcceptTerms} />
        <ConsentRow label={COMPLIANCE.popiaConsent} value={acceptPopia} onChange={setAcceptPopia} />
      </FintechCard>

      <Text style={[typography.caption, { color: theme.textTertiary, marginBottom: spacing.md }]}>
        {COMPLIANCE.platformDisclaimer}
      </Text>

      <Button title="Create account" onPress={submit} loading={loading} />
      <Button title="Already have an account? Sign in" onPress={() => navigation.goBack()} variant="ghost" />
      <Button title="View Terms" onPress={() => Linking.openURL("https://app.ipaygo.co.za/legal/terms")} variant="ghost" />
    </Screen>
  );
}

function ConsentRow({ label, value, onChange }: { label: string; value: boolean; onChange: (v: boolean) => void }) {
  const theme = useAppTheme();
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.md, marginBottom: spacing.sm }}>
      <Switch value={value} onValueChange={onChange} trackColor={{ false: theme.border, true: theme.primary }} />
      <Text style={[typography.caption, { color: theme.text, flex: 1 }]}>{label}</Text>
    </View>
  );
}
