import { useState } from "react";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AlertBanner, Button, Input, Screen, H2, Body } from "../../components";
import { useAuthStore } from "../../store/authStore";
import { authApi } from "../../api/auth";
import { normalizePhone } from "../../utils/phone";
import { AuthStackParamList } from "../../navigation/AuthNavigator";

type Props = NativeStackScreenProps<AuthStackParamList, "OtpLogin">;

export default function OtpLoginScreen({ navigation, route }: Props) {
  const { loginOtp, loading } = useAuthStore();
  const [mobile, setMobile] = useState(route.params?.mobile ?? "");
  const [code, setCode] = useState("");
  const [channel, setChannel] = useState<"sms" | "whatsapp">("sms");
  const [sent, setSent] = useState(!!route.params?.mobile);
  const [error, setError] = useState("");

  const send = async () => {
    setError("");
    try {
      await authApi.sendOtp(normalizePhone(mobile), channel, "login");
      setSent(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send OTP");
    }
  };

  const submit = async () => {
    setError("");
    try {
      await loginOtp(normalizePhone(mobile), code);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invalid code");
    }
  };

  return (
    <Screen scroll>
      <H2>OTP Login</H2>
      <Body muted>Sign in with a one-time code via SMS or WhatsApp</Body>
      {error ? <AlertBanner type="error" message={error} /> : null}
      <Input label="Mobile Number" value={mobile} onChangeText={setMobile} keyboardType="phone-pad" />
      <Button title={`Send OTP via ${channel === "sms" ? "SMS" : "WhatsApp"}`} onPress={send} variant="outline" />
      <Button title={`Switch to ${channel === "sms" ? "WhatsApp" : "SMS"}`} onPress={() => setChannel(channel === "sms" ? "whatsapp" : "sms")} variant="ghost" />
      {sent && <Input label="OTP Code" value={code} onChangeText={setCode} keyboardType="number-pad" maxLength={6} />}
      {sent && <Button title="Verify & Sign In" onPress={submit} loading={loading} />}
      <Button title="Back" onPress={() => navigation.goBack()} variant="ghost" />
    </Screen>
  );
}
