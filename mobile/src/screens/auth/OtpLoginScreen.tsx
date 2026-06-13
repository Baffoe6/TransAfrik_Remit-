import { useState } from "react";
import { Text, ScrollView } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AuthStackParamList } from "../../navigation/AuthNavigator";
import { Screen, Title, Muted, Input, Button } from "../../components/ui";
import { useAuthStore } from "../../store/authStore";
import { authApi } from "../../api/auth";

type Props = NativeStackScreenProps<AuthStackParamList, "OtpLogin">;

export default function OtpLoginScreen({ navigation }: Props) {
  const { loginOtp, loading } = useAuthStore();
  const [mobile, setMobile] = useState("");
  const [code, setCode] = useState("");
  const [channel, setChannel] = useState<"sms" | "whatsapp">("sms");
  const [sent, setSent] = useState(false);
  const [devCode, setDevCode] = useState<string | null>(null);
  const [error, setError] = useState("");

  const send = async () => {
    setError("");
    try {
      const { data } = await authApi.sendOtp(mobile, channel, "login");
      setSent(true);
      if (data.dev_code) setDevCode(data.dev_code);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send OTP");
    }
  };

  const verify = async () => {
    setError("");
    try {
      await loginOtp(mobile, code);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invalid code");
    }
  };

  return (
    <Screen>
      <ScrollView>
        <Title>OTP Login</Title>
        <Muted>Passwordless sign-in via SMS or WhatsApp</Muted>
        {error ? <Text style={{ color: "#DC2626" }}>{error}</Text> : null}
        <Input label="Mobile Number" value={mobile} onChangeText={setMobile} keyboardType="phone-pad" editable={!sent} />
        {!sent && (
          <>
            <Button title="Send via SMS" variant={channel === "sms" ? "primary" : "outline"} onPress={() => { setChannel("sms"); send(); }} />
            <Button title="Send via WhatsApp" variant={channel === "whatsapp" ? "primary" : "outline"} onPress={() => { setChannel("whatsapp"); send(); }} />
          </>
        )}
        {sent && (
          <>
            {devCode && <Muted>Dev code: {devCode}</Muted>}
            <Input label="Verification Code" value={code} onChangeText={setCode} keyboardType="number-pad" />
            <Button title="Verify & Sign In" onPress={verify} loading={loading} />
          </>
        )}
        <Button title="Back" variant="outline" onPress={() => navigation.goBack()} />
      </ScrollView>
    </Screen>
  );
}
